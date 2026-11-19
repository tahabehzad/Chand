#!/usr/bin/env bash
# P0-T16 logical backup baseline.
#
# Authority: docs/specs/DEPLOYMENT.md §5 (backup/restore baseline; 10-year
# retention for tax/labour audit) and WBS §14.3 `P0-T16`.
#
# Produces one self-contained set per run:
#   <output-dir>/<UTC timestamp>/db.dump          pg_dump custom format
#                                 /schema.fingerprint  catalogue digest
#                                 /manifest.txt        metadata + dump SHA-256
# and prunes all but the newest <retention> sets.
#
# No credential is read, written or echoed: the container is reached with the
# local trust/peer configuration, and the dump is produced inside the
# container so no password ever appears on a command line.
set -euo pipefail

SRC="${1:?usage: backup.sh <source-container> <output-dir> [retention=7] [db-user=postgres] [db=app]}"
OUT="${2:?usage: backup.sh <source-container> <output-dir> [retention=7] [db-user=postgres] [db=app]}"
RETAIN="${3:-7}"
DB_USER="${4:-postgres}"
DB_NAME="${5:-app}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$(date -u '+%Y-%m-%dT%H%M%SZ')"
SET_DIR="${OUT}/${STAMP}"

mkdir -p "${SET_DIR}"

# 1. Consistent logical dump inside the container.
docker exec "${SRC}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" -Fc \
    --file /tmp/pish_p0t16.dump
docker cp "${SRC}:/tmp/pish_p0t16.dump" "${SET_DIR}/db.dump"
docker exec "${SRC}" rm -f /tmp/pish_p0t16.dump

# 2. Catalogue digest of the source, for the restore comparison.
docker exec -i "${SRC}" psql -U "${DB_USER}" -d "${DB_NAME}" -At -F '|' \
    -v ON_ERROR_STOP=1 -f - \
    < "${HERE}/schema_fingerprint.sql" > "${SET_DIR}/schema.fingerprint"
[[ -s "${SET_DIR}/schema.fingerprint" ]] || {
    echo "schema fingerprint is empty; refusing to declare a backup" >&2
    exit 4
}

FINGERPRINT="$(tr '|' ' ' < "${SET_DIR}/schema.fingerprint")"
# Hash from stdin: a path containing a backslash (a Windows host path) would
# otherwise be escaped into the digest line.
DUMP_SHA256="$(sha256sum < "${SET_DIR}/db.dump" | cut -d' ' -f1)"
PG_VERSION="$(docker exec "${SRC}" postgres --version | tr -d '\r')"

{
    echo "backup_utc=${STAMP}"
    echo "source_container=${SRC}"
    echo "database=${DB_NAME}"
    echo "pg_version=${PG_VERSION}"
    echo "dump_format=custom"
    echo "dump_sha256=${DUMP_SHA256}"
    echo "schema_fingerprint=${FINGERPRINT}"
} > "${SET_DIR}/manifest.txt"

# 3. Retention: keep the newest <retention> sets only.
if [[ -d "${OUT}" ]]; then
    COUNT="$(find "${OUT}" -mindepth 1 -maxdepth 1 -type d | wc -l)"
    if (( COUNT > RETAIN )); then
        find "${OUT}" -mindepth 1 -maxdepth 1 -type d | sort \
            | head -n "$((COUNT - RETAIN))" \
            | while read -r stale; do rm -rf "${stale}"; done
    fi
fi

echo "backup_set=${SET_DIR}"
echo "schema_fingerprint=${FINGERPRINT}"
