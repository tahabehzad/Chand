"""Bounded official-source discovery CLI (P1-T02 evidence preparation only)."""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import ipaddress
import json
import socket
import ssl
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from uuid import uuid4

MAX_BYTES = 8 * 1024 * 1024
MAX_LINKS = 8
TIMEOUT_SECONDS = 8
MAX_ELAPSED_SECONDS = 30
ALLOWED_HOSTS = frozenset(
    {
        "www.mcls.gov.ir",
        "www.tamin.ir",
        "news.tamin.ir",
        "www.intamedia.ir",
        "www.rrk.ir",
        "www.dotic.ir",
    }
)


@dataclass(frozen=True)
class Source:
    """A discovery target, not a legally verified document or parameter."""

    source_id: str
    families: tuple[str, ...]
    url: str


SOURCES = (
    Source("labor", ("S1",), "https://www.mcls.gov.ir/"),
    Source("sso", ("S4", "S5"), "https://www.tamin.ir/"),
    Source("sso-wage-discovery", ("S4",), "https://news.tamin.ir/News/Item/197732"),
    Source("tax", ("S6", "S7"), "https://www.intamedia.ir/"),
    Source("gazette", ("S1", "S2", "S3", "S5", "S6", "S7", "S8"), "https://www.rrk.ir/"),
    Source("cabinet", ("S2",), "https://www.dotic.ir/"),
)


class AcquisitionError(ValueError):
    """Safe categorical failure: never embed a remote response or raw exception."""

    def __init__(self, code: str, *, status: int | None = None, mime: str | None = None) -> None:
        super().__init__(code)
        self.status = status
        self.mime = mime


def validate_url(url: str) -> tuple[str, str]:
    """Allow only known public HTTPS origins, without userinfo or query secrets."""
    try:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname not in ALLOWED_HOSTS
            or parsed.port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or any(ord(char) < 33 or ord(char) > 126 for char in url)
            or "\\" in url
        ):
            raise AcquisitionError("URL_POLICY")
    except ValueError:
        raise AcquisitionError("URL_POLICY") from None
    return parsed.hostname, parsed.path or "/"


def public_address(host: str) -> str:
    """Resolve once; reject the entire answer set if any address is not public."""
    answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    addresses = [str(answer[4][0]) for answer in answers]
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise AcquisitionError("DNS_POLICY")
    return addresses[0]


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to a validated IP, retain the official hostname for TLS/SNI."""

    def __init__(self, host: str, address: str) -> None:
        self.tls_context = ssl.create_default_context()
        super().__init__(host, timeout=TIMEOUT_SECONDS, context=self.tls_context)
        self.address = address

    def connect(self) -> None:
        raw = socket.create_connection((self.address, 443), timeout=TIMEOUT_SECONDS)
        try:
            self.sock = self.tls_context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


@dataclass(frozen=True)
class FetchResult:
    status: int
    mime: str
    body: bytes


def _body_headers(response: http.client.HTTPResponse, mime: str) -> str | None:
    """Reject unbounded/encoded or unsupported entity bodies before reading."""
    if mime not in {"text/html", "application/pdf"}:
        raise AcquisitionError("MIME_POLICY")
    if response.getheader("Content-Encoding", "identity").lower() not in {"", "identity"}:
        raise AcquisitionError("ENCODING_POLICY")
    declared = response.getheader("Content-Length")
    if declared is not None and (not declared.isdecimal() or int(declared) > MAX_BYTES):
        raise AcquisitionError("SIZE_POLICY")
    return declared


def _fetch_in_process(url: str) -> FetchResult:
    """No redirects, proxy, cookies or credentials; retain original entity bytes."""
    host, path = validate_url(url)
    connection = PinnedHTTPSConnection(host, public_address(host))
    started = time.monotonic()
    status: int | None = None
    mime: str | None = None
    try:
        connection.request(
            "GET",
            path,
            headers={"User-Agent": "PishHesabdari-SourceCheck/0.1", "Accept-Encoding": "identity"},
        )
        response = connection.getresponse()
        status = response.status
        if response.status != 200:
            return FetchResult(response.status, "", b"")
        mime = response.getheader("Content-Type", "").split(";", 1)[0].strip().lower()
        declared = _body_headers(response, mime)
        chunks: list[bytes] = []
        size = 0
        while True:
            if time.monotonic() - started > MAX_ELAPSED_SECONDS:
                raise AcquisitionError("TIME_POLICY")
            chunk = response.read(min(65536, MAX_BYTES + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > MAX_BYTES:
                raise AcquisitionError("SIZE_POLICY")
        if declared is not None and size != int(declared):
            raise AcquisitionError("TRUNCATED_BODY")
        body = b"".join(chunks)
        if not body or (mime == "application/pdf" and not body.startswith(b"%PDF-")):
            raise AcquisitionError("CONTENT_POLICY")
        return FetchResult(response.status, mime, body)
    except AcquisitionError as error:
        raise AcquisitionError(str(error), status=status, mime=mime) from None
    except (OSError, http.client.HTTPException):
        raise AcquisitionError("TRANSPORT_FAILED", status=status, mime=mime) from None
    finally:
        connection.close()


def fetch(url: str) -> FetchResult:
    """A killable subprocess bounds DNS, TLS and trickling bodies to 30 seconds."""
    validate_url(url)
    try:
        # Fixed interpreter/module, no shell; URL validated before child invocation.
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-B", "-m", "app.statutory.collect_sources", "--fetch-worker", url],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            check=False,
            timeout=MAX_ELAPSED_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise AcquisitionError("TIME_POLICY") from None
    if result.returncode != 0:
        raise AcquisitionError("TRANSPORT_FAILED")
    payload = json.loads(result.stdout)
    if payload.get("error"):
        raise AcquisitionError(payload["error"], status=payload["status"], mime=payload["mime"])
    return FetchResult(
        payload["status"], payload["mime"], base64.b64decode(payload["body"], validate=True)
    )


def _worker(url: str) -> int:
    """Private subprocess protocol; raw remote errors never cross the boundary."""
    try:
        result = _fetch_in_process(url)
        payload: dict[str, object] = {
            "status": result.status,
            "mime": result.mime,
            "body": base64.b64encode(result.body).decode("ascii"),
        }
    except AcquisitionError as error:
        payload = {"error": str(error), "status": error.status, "mime": error.mime}
    except Exception:
        payload = {"error": "TRANSPORT_FAILED", "status": None, "mime": None}
    print(json.dumps(payload))  # noqa: T201
    return 0


class PDFLinks(HTMLParser):
    """Discover at most MAX_LINKS PDF links; never execute or render remote HTML."""

    def __init__(self, base: str) -> None:
        super().__init__()
        self.base = base
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a" or len(self.links) >= MAX_LINKS:
            return
        for name, value in attrs:
            if len(self.links) >= MAX_LINKS:
                break
            if name != "href" or not value:
                continue
            try:
                url = urljoin(self.base, value)
                validate_url(url)
            except ValueError:
                continue
            if urlsplit(url).path.lower().endswith(".pdf") and url not in self.links:
                self.links.append(url)


def collect(source: Source, root: Path, *, getter: Callable[[str], FetchResult] = fetch) -> Path:
    """Store a new attempt in local staging; never mark it archived or verified."""
    # Validate caller metadata before filesystem writes, even with an injected getter.
    validate_url(source.url)
    if not source.source_id or any(
        char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in source.source_id
    ):
        raise AcquisitionError("SOURCE_POLICY")
    root.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    directory = root / f"{now:%Y%m%dT%H%M%S}-{source.source_id}-{uuid4().hex}"
    directory.mkdir(exist_ok=False)
    manifest: dict[str, object] = {
        "source_id": source.source_id,
        "source_codes": list(source.families),
        "source_url": source.url,
        "retrieved_at": now.isoformat(),
        "http_status": None,
        "retrieval_level": "L1",
        "document_role": "DISCOVERY_ONLY",
        "verification_status": "UNVERIFIED",
        "storage_status": "LOCAL_STAGING",
        "activation_eligible": False,
        "sha256": None,
        "mime_type": None,
        "raw_file": None,
        "pdf_links": [],
    }
    try:
        result = getter(source.url)
        manifest["http_status"] = result.status
        if result.status != 200:
            manifest["outcome"] = "HTTP_REJECTED"
        else:
            links: list[str] = []
            if result.mime == "text/html":
                parser = PDFLinks(source.url)
                parser.feed(result.body.decode("utf-8", errors="replace"))
                links = parser.links
            try:
                # A failed write leaves only a quarantined .part file, never a
                # manifest claiming a complete body/hash. Unique directory owns it.
                with (directory / "response.part").open("xb") as handle:
                    handle.write(result.body)
                (directory / "response.part").rename(directory / "response.bin")
            except OSError:
                manifest["outcome"] = "STORAGE_FAILED"
            else:
                manifest["outcome"] = "CAPTURED_UNVERIFIED"
                manifest["sha256"] = hashlib.sha256(result.body).hexdigest()
                manifest["mime_type"] = result.mime
                manifest["raw_file"] = "response.bin"
                manifest["pdf_links"] = links
    except AcquisitionError as error:
        # Only these local categorical strings may reach output, never error text.
        allowed = {
            "URL_POLICY",
            "DNS_POLICY",
            "MIME_POLICY",
            "ENCODING_POLICY",
            "SIZE_POLICY",
            "TIME_POLICY",
            "TRUNCATED_BODY",
            "CONTENT_POLICY",
            "TRANSPORT_FAILED",
        }
        manifest["http_status"] = error.status
        manifest["mime_type"] = error.mime
        manifest["outcome"] = str(error) if str(error) in allowed else "POLICY_REJECTED"
    except (OSError, http.client.HTTPException, ValueError):
        manifest["outcome"] = "TRANSPORT_FAILED"
    path = directory / "manifest.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=True, sort_keys=True, indent=2)
        handle.write("\n")
    return path


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--fetch-worker":
        return _worker(sys.argv[2])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", choices=[source.source_id for source in SOURCES], action="append"
    )
    parser.add_argument(
        "--download-pdfs", action="store_true", help="Download discovered allowlisted PDFs once"
    )
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[3] / ".freebuff" / "statutory-acquisition"
    selected = [
        source for source in SOURCES if not arguments.source or source.source_id in arguments.source
    ]
    failures = 0
    for source in selected:
        path = collect(source, root)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        print(  # noqa: T201
            json.dumps(
                {
                    "source_id": source.source_id,
                    "outcome": manifest["outcome"],
                    "http_status": manifest["http_status"],
                    "manifest": str(path),
                }
            )
        )
        failures += manifest["outcome"] != "CAPTURED_UNVERIFIED"
        if arguments.download_pdfs:
            for index, url in enumerate(manifest["pdf_links"]):
                pdf_path = collect(
                    Source(f"{source.source_id}-pdf-{index}", source.families, url), root
                )
                pdf = json.loads(pdf_path.read_text(encoding="utf-8"))
                failures += pdf["outcome"] != "CAPTURED_UNVERIFIED"
                print(  # noqa: T201
                    json.dumps(
                        {
                            "source_id": pdf["source_id"],
                            "outcome": pdf["outcome"],
                            "http_status": pdf["http_status"],
                            "manifest": str(pdf_path),
                        }
                    )
                )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
