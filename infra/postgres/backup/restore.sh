#!/usr/bin/env bash
# P0-T16 restore dry run.
#
# Authority: docs/specs/DEPLOYMENT.md §5 and WBS §14.3 `P0-T16`
# ("a restore script"; AC: a backup restores to a schema-identical isolated
# instance).
#
# Restores one backup set into an already-running *disposable* target
# container. It refuses to run against the source container and never touches
# a database it did not create in this invocation.
set -euo pipefail

SET_DIR="${1:?usage: restore.sh <backup-set-dir> <target-container> [db-user=postgres] [db=app]}"
TGT="${2:?usage: restore.sh <backup-set-dir> <target-container> [db-user=postgres] [db=app]}"
DB_USER="${3:-postgres}"
DB_NAME="${4:-app}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[[ -f "${SET_DIR}/db.dump" ]] || { echo "no db.dump in ${SET_DIR}" >&2; exit 2; }
SOURCE_CONTAINER="$(grep -m1 '^source_container=' "${SET_DIR}/manifest.txt" | cut -d= -f2-)"
if [[ -n "${SOURCE_CONTAINER}" && "${SOURCE_CONTAINER}" == "${TGT}" ]]; then
    echo "refusing to restore onto the backup's own source container" >&2
    exit 3
fi

docker exec -i "${TGT}" psql -U "${DB_USER}" -d postgres -v ON_ERROR_STOP=1 \
    -c "DROP DATABASE IF EXISTS \"${DB_NAME}\"" >/dev/null
docker exec "${TGT}" createdb -U "${DB_USER}" "${DB_NAME}"

docker cp "${SET_DIR}/db.dump" "${TGT}:/tmp/pish_p0t16_restore.dump"
docker exec "${TGT}" pg_restore -U "${DB_USER}" -d "${DB_NAME}" \
    --exit-on-error /tmp/pish_p0t16_restore.dump
docker exec "${TGT}" rm -f /tmp/pish_p0t16_restore.dump

docker exec -i "${TGT}" psql -U "${DB_USER}" -d "${DB_NAME}" -At -F '|' \
    -v ON_ERROR_STOP=1 -f - < "${HERE}/schema_fingerprint.sql"
