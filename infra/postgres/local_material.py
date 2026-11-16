"""P0-T03 development-only credentials/TLS material; never print private values."""

from __future__ import annotations

import os
import secrets
import subprocess
from datetime import UTC, datetime, timedelta
from ipaddress import ip_address
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

EXPECTED_FILES = frozenset({"password", "ca.key", "ca.crt", "server.key", "server.crt"})
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SECRET_DIRECTORY = REPOSITORY_ROOT / ".secrets" / "postgres"


class LocalMaterialError(RuntimeError):
    """Refuse incomplete, unsafe or expired development material."""


def _restrict_access(directory: Path) -> None:
    if os.name == "nt":
        # Static script; the path is passed as an environment value, never
        # interpolated into executable PowerShell. Replace DACLs with only
        # this user and SYSTEM; no inherited broad read grants remain.
        script = r"""
$ErrorActionPreference='Stop'
$dir=[System.IO.DirectoryInfo]::new($env:PISH_LOCAL_SECRET_DIR)
$ids=@([System.Security.Principal.WindowsIdentity]::GetCurrent().User,
       [System.Security.Principal.SecurityIdentifier]::new('S-1-5-18'))
$acl=[System.Security.AccessControl.DirectorySecurity]::new()
$acl.SetAccessRuleProtection($true,$false)
foreach($id in $ids) {
 $rule=[System.Security.AccessControl.FileSystemAccessRule]::new($id,'FullControl','ContainerInherit,ObjectInherit','None','Allow')
 $acl.AddAccessRule($rule)
}
$dir.SetAccessControl($acl)
foreach($file in $dir.EnumerateFiles()) {
 $fileAcl=[System.Security.AccessControl.FileSecurity]::new()
 $fileAcl.SetAccessRuleProtection($true,$false)
 foreach($id in $ids) {
  $fileAcl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($id,'FullControl','Allow'))
 }
 $file.SetAccessControl($fileAcl)
}
"""
        environment = os.environ.copy()
        environment["PISH_LOCAL_SECRET_DIR"] = str(directory)
        subprocess.run(  # noqa: S603 — static executable/script, validated task-owned path
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],  # noqa: S607
            env=environment,
            check=True,
            capture_output=True,
            timeout=20,
        )
    else:
        directory.chmod(0o700)
        for path in directory.iterdir():
            path.chmod(0o600)


def _write_private(path: Path, value: bytes) -> None:
    # Exclusive creation: an existing file is never overwritten.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(value)


def _private_bytes(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def _validate(directory: Path) -> None:
    now = datetime.now(UTC)
    ca = x509.load_pem_x509_certificate((directory / "ca.crt").read_bytes())
    server = x509.load_pem_x509_certificate((directory / "server.crt").read_bytes())
    ca_key = serialization.load_pem_private_key((directory / "ca.key").read_bytes(), password=None)
    server_key = serialization.load_pem_private_key(
        (directory / "server.key").read_bytes(), password=None
    )
    if not isinstance(ca_key, ec.EllipticCurvePrivateKey) or not isinstance(
        server_key, ec.EllipticCurvePrivateKey
    ):
        raise LocalMaterialError("Unexpected key type.")
    for certificate, key in ((ca, ca_key), (server, server_key)):
        if not certificate.not_valid_before_utc <= now < certificate.not_valid_after_utc:
            raise LocalMaterialError("Development certificate is not currently valid.")
        public = key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        if public != certificate.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        ):
            raise LocalMaterialError("Development key/certificate mismatch.")
    if (
        server.issuer != ca.subject
        or not ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    ):
        raise LocalMaterialError("Invalid development issuer.")
    if not isinstance(server.signature_hash_algorithm, hashes.SHA256) or not isinstance(
        ca.signature_hash_algorithm, hashes.SHA256
    ):
        raise LocalMaterialError("Unexpected signature algorithm.")
    ca_key.public_key().verify(
        ca.signature, ca.tbs_certificate_bytes, ec.ECDSA(ca.signature_hash_algorithm)
    )
    ca_key.public_key().verify(
        server.signature, server.tbs_certificate_bytes, ec.ECDSA(server.signature_hash_algorithm)
    )
    names = server.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    if not {"localhost", "db"} <= set(names.get_values_for_type(x509.DNSName)):
        raise LocalMaterialError("Missing development DNS SAN.")
    if not {ip_address("127.0.0.1"), ip_address("::1")} <= set(
        names.get_values_for_type(x509.IPAddress)
    ):
        raise LocalMaterialError("Missing development IP SAN.")
    if (
        ExtendedKeyUsageOID.SERVER_AUTH
        not in server.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
    ):
        raise LocalMaterialError("Missing server-auth usage.")
    password = (directory / "password").read_bytes()
    if len(password) < 32 or any(
        value not in b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        for value in password
    ):
        raise LocalMaterialError("Invalid local password material.")


def prepare_material(directory: Path) -> str:
    """Create once or validate existing complete material, with private permissions."""
    directory = directory.absolute()
    if directory.is_symlink() or directory.resolve() != directory:
        raise LocalMaterialError("Secret directory must not traverse links.")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    entries = list(directory.iterdir())
    if any(path.is_symlink() or not path.is_file() for path in entries):
        raise LocalMaterialError("Unexpected secret-directory entry.")
    present = {path.name for path in entries}
    if present and present != EXPECTED_FILES:
        raise LocalMaterialError("Partial or unexpected material; no automatic overwrite.")
    _restrict_access(directory)
    if present:
        _validate(directory)
        return "validated"

    now = datetime.now(UTC)
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Pish development CA")])
    ca = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=90))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(False, False, False, False, False, True, True, False, False),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False
        )
        .sign(ca_key, hashes.SHA256())
    )
    server_key = ec.generate_private_key(ec.SECP256R1())
    server = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "db")]))
        .issuer_name(ca.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(True, False, False, False, False, False, False, False, False),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()), critical=False
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False
        )
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("db"),
                    x509.DNSName("localhost"),
                    x509.IPAddress(ip_address("127.0.0.1")),
                    x509.IPAddress(ip_address("::1")),
                ]
            ),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    contents = {
        "password": secrets.token_urlsafe(48).encode("ascii"),
        "ca.key": _private_bytes(ca_key),
        "ca.crt": ca.public_bytes(serialization.Encoding.PEM),
        "server.key": _private_bytes(server_key),
        "server.crt": server.public_bytes(serialization.Encoding.PEM),
    }
    for name, value in contents.items():
        _write_private(directory / name, value)
    _restrict_access(directory)
    _validate(directory)
    return "created"


def main() -> int:
    try:
        if not SECRET_DIRECTORY.resolve().is_relative_to(REPOSITORY_ROOT):
            raise LocalMaterialError("Secret path is outside the repository.")
        prepare_material(SECRET_DIRECTORY)
    except Exception:
        print("FAIL: local material preparation refused; values suppressed.")  # noqa: T201
        return 1
    print("PASS: private local PostgreSQL material ready; values suppressed.")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
