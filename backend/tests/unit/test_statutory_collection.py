"""Adversarial evidence-collection tests; no live network or legal-value fixtures."""

from __future__ import annotations

import hashlib
import io
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from app.statutory import collect_sources as collector


@pytest.mark.parametrize(
    "url",
    [
        "http://www.mcls.gov.ir/",
        "https://127.0.0.1/",
        "https://www.mcls.gov.ir.evil.example/",
        "https://www.mcls.gov.ir:8443/",
        "https://user:secret@www.mcls.gov.ir/",
        "https://www.mcls.gov.ir/?token=secret",
        "https://www.mcls.gov.ir/#fragment",
        "https://www.mcls.gov.ir/\r\nInjected: header",
        "https://www.mcls.gov.ir/\\private",
        "https://www.mcls.gov.ir:broken/",
    ],
)
def test_reject_unsafe_url(url: str) -> None:
    with pytest.raises(collector.AcquisitionError, match="URL_POLICY"):
        collector.validate_url(url)


@pytest.mark.parametrize(
    "ip", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "::1", "::ffff:127.0.0.1"]
)
def test_reject_private_dns_answer(monkeypatch: pytest.MonkeyPatch, ip: str) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **kw: [(2, 1, 6, "", (ip, 443))])
    with pytest.raises(collector.AcquisitionError, match="DNS_POLICY"):
        collector.public_address("www.mcls.gov.ir")


def test_reject_mixed_dns_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **kw: [(2, 1, 6, "", (ip, 443)) for ip in ("8.8.8.8", "10.0.0.1")],
    )
    with pytest.raises(collector.AcquisitionError, match="DNS_POLICY"):
        collector.public_address("www.mcls.gov.ir")


def test_discovery_limits_and_host_policy() -> None:
    parser = collector.PDFLinks("https://www.mcls.gov.ir/news")
    parser.feed(
        '<a href="http://127.0.0.1/file.pdf">bad</a><a href="https://evil.example/file.pdf">bad</a>'
    )
    parser.feed('<a href="/first.pdf">ok</a><a href="/first.pdf">duplicate</a>')
    parser.feed("".join(f'<a href="/{index}.pdf">ok</a>' for index in range(100)))
    assert len(parser.links) == collector.MAX_LINKS
    assert parser.links[0] == "https://www.mcls.gov.ir/first.pdf"


def test_single_tag_duplicate_hrefs_cannot_bypass_limit() -> None:
    parser = collector.PDFLinks("https://www.mcls.gov.ir/")
    parser.feed("<a " + " ".join(f'href="/{index}.pdf"' for index in range(100)) + ">links</a>")
    assert len(parser.links) == collector.MAX_LINKS


def test_hard_deadline_covers_stalled_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    def stalled(*args: object, **kwargs: object) -> None:
        assert kwargs["timeout"] == collector.MAX_ELAPSED_SECONDS
        raise subprocess.TimeoutExpired("synthetic", 30)

    monkeypatch.setattr(subprocess, "run", stalled)
    with pytest.raises(collector.AcquisitionError, match="TIME_POLICY"):
        collector.fetch(collector.SOURCES[0].url)


def test_policy_failure_preserves_response_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_connection(monkeypatch, Response(b"not PDF", {"Content-Type": "application/pdf"}))
    path = collector.collect(collector.SOURCES[0], tmp_path, getter=collector._fetch_in_process)
    data = json.loads(path.read_text())
    assert data["http_status"] == 200
    assert data["mime_type"] == "application/pdf"
    assert data["outcome"] == "CONTENT_POLICY"
    assert data["raw_file"] is None


def test_trickling_or_dns_stalled_child_is_actually_terminated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_run = subprocess.run

    def stalled(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        # Simulate a child stuck in DNS/headers/body; use the collector's actual
        # parent timeout without a network server or a 30-second test delay.
        return real_run(
            [sys.executable, "-B", "-c", "import time; time.sleep(10)"],
            capture_output=True,
            timeout=1,
            check=False,
        )

    monkeypatch.setattr(subprocess, "run", stalled)
    started = time.monotonic()
    with pytest.raises(collector.AcquisitionError, match="TIME_POLICY"):
        collector.fetch(collector.SOURCES[0].url)
    assert time.monotonic() - started < 8


def test_invalid_ipv6_discovery_link_is_skipped() -> None:
    parser = collector.PDFLinks("https://www.mcls.gov.ir/")
    parser.feed('<a href="https://[malformed/file.pdf">bad</a><a href="/ok.pdf">ok</a>')
    assert parser.links == ["https://www.mcls.gov.ir/ok.pdf"]


def test_partial_storage_never_claims_complete_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_open = Path.open

    def fail_raw_write(path: Path, *args: object, **kwargs: object) -> object:
        if path.name == "response.part":
            raise OSError("synthetic private storage failure")
        return real_open(path, *args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(Path, "open", fail_raw_write)
    path = collector.collect(
        collector.SOURCES[0],
        tmp_path,
        getter=lambda _: collector.FetchResult(200, "text/html", b"public"),
    )
    data = json.loads(path.read_text())
    assert data["outcome"] == "STORAGE_FAILED"
    assert data["sha256"] is None
    assert data["raw_file"] is None
    assert "synthetic private storage failure" not in path.read_text()


def test_body_transport_failure_retains_headers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class BrokenResponse(Response):
        def read(self, size: int) -> bytes:
            raise OSError("synthetic private peer failure")

    fake_connection(monkeypatch, BrokenResponse(b"", {"Content-Type": "text/html"}))
    path = collector.collect(collector.SOURCES[0], tmp_path, getter=collector._fetch_in_process)
    data = json.loads(path.read_text())
    assert data["http_status"] == 200
    assert data["mime_type"] == "text/html"
    assert data["outcome"] == "TRANSPORT_FAILED"
    assert "synthetic private peer failure" not in path.read_text()


def test_capture_preserves_bytes_and_never_overwrites(tmp_path: Path) -> None:
    body = b"<html>public discovery evidence</html>"
    source = collector.SOURCES[0]
    first = collector.collect(
        source, tmp_path, getter=lambda _: collector.FetchResult(200, "text/html", body)
    )
    original = first.read_bytes()
    second = collector.collect(
        source, tmp_path, getter=lambda _: collector.FetchResult(200, "text/html", b"changed")
    )
    data = json.loads(original)
    assert first != second
    assert first.read_bytes() == original
    assert (first.parent / "response.bin").read_bytes() == body
    assert data["sha256"] == hashlib.sha256(body).hexdigest()
    assert data["verification_status"] == "UNVERIFIED"
    assert data["storage_status"] == "LOCAL_STAGING"
    assert data["activation_eligible"] is False
    assert data["document_role"] == "DISCOVERY_ONLY"


@pytest.mark.parametrize("status", [301, 302, 403, 429, 500])
def test_http_failure_keeps_metadata_without_body(tmp_path: Path, status: int) -> None:
    path = collector.collect(
        collector.SOURCES[0],
        tmp_path,
        getter=lambda _: collector.FetchResult(
            status, "text/html", b"must not archive error pages"
        ),
    )
    data = json.loads(path.read_text())
    assert data["outcome"] == "HTTP_REJECTED"
    assert data["http_status"] == status
    assert data["sha256"] is None
    assert not (path.parent / "response.bin").exists()


def test_transport_errors_never_leak_remote_details(tmp_path: Path) -> None:
    def fail(_: str) -> collector.FetchResult:
        raise OSError("sensitive-remote-error-body")

    path = collector.collect(collector.SOURCES[0], tmp_path, getter=fail)
    assert "sensitive-remote-error-body" not in path.read_text()
    assert json.loads(path.read_text())["outcome"] == "TRANSPORT_FAILED"


class Response:
    def __init__(self, body: bytes, headers: dict[str, str], status: int = 200) -> None:
        self.status = status
        self.body = io.BytesIO(body)
        self.headers = headers

    def getheader(self, name: str, default: str | None = None) -> str | None:
        return self.headers.get(name, default)

    def read(self, size: int) -> bytes:
        return self.body.read(size)


def fake_connection(monkeypatch: pytest.MonkeyPatch, response: Response) -> list[str]:
    events: list[str] = []

    class Connection:
        def __init__(self, host: str, address: str) -> None:
            events.extend((host, address))

        def request(self, *args: object, **kwargs: object) -> None:
            events.append("request")

        def getresponse(self) -> Response:
            return response

        def close(self) -> None:
            events.append("closed")

    monkeypatch.setattr(collector, "public_address", lambda _: "8.8.8.8")
    monkeypatch.setattr(collector, "PinnedHTTPSConnection", Connection)
    return events


@pytest.mark.parametrize(
    ("body", "headers", "failure"),
    [
        (b"html", {"Content-Type": "application/octet-stream"}, "MIME_POLICY"),
        (b"html", {"Content-Type": "text/html", "Content-Encoding": "gzip"}, "ENCODING_POLICY"),
        (
            b"html",
            {"Content-Type": "text/html", "Content-Length": str(collector.MAX_BYTES + 1)},
            "SIZE_POLICY",
        ),
        (b"html", {"Content-Type": "text/html", "Content-Length": "20"}, "TRUNCATED_BODY"),
        (b"not PDF", {"Content-Type": "application/pdf"}, "CONTENT_POLICY"),
        (b"", {"Content-Type": "text/html"}, "CONTENT_POLICY"),
    ],
)
def test_response_limits(
    monkeypatch: pytest.MonkeyPatch, body: bytes, headers: dict[str, str], failure: str
) -> None:
    events = fake_connection(monkeypatch, Response(body, headers))
    with pytest.raises(collector.AcquisitionError, match=failure):
        collector._fetch_in_process(collector.SOURCES[0].url)
    assert events[-1] == "closed"


def test_stream_limit_without_content_length(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_connection(monkeypatch, Response(b"x" * 17, {"Content-Type": "text/html"}))
    monkeypatch.setattr(collector, "MAX_BYTES", 16)
    with pytest.raises(collector.AcquisitionError, match="SIZE_POLICY"):
        collector._fetch_in_process(collector.SOURCES[0].url)


def test_redirect_not_followed(monkeypatch: pytest.MonkeyPatch) -> None:
    events = fake_connection(monkeypatch, Response(b"", {"Location": "http://127.0.0.1/"}, 302))
    assert collector._fetch_in_process(collector.SOURCES[0].url).status == 302
    assert events.count("request") == 1


def test_complete_pdf_and_pinned_destination(monkeypatch: pytest.MonkeyPatch) -> None:
    body = b"%PDF-1.7\nsynthetic fixture"
    events = fake_connection(
        monkeypatch,
        Response(body, {"Content-Type": "application/pdf", "Content-Length": str(len(body))}),
    )
    assert collector._fetch_in_process(collector.SOURCES[0].url).body == body
    assert events[:2] == ["www.mcls.gov.ir", "8.8.8.8"]
