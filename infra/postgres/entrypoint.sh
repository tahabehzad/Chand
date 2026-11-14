#!/bin/sh
set -eu

# The official entrypoint subsequently drops to postgres. Private Windows
# bind mounts do not carry reliable Linux mode bits: copy into tmpfs with
# explicit ownership/mode. Never echo file contents or enable shell xtrace.
install -d -m 0700 -o postgres -g postgres /run/pish-postgres-tls
install -m 0600 -o postgres -g postgres /run/secrets/db_server_key /run/pish-postgres-tls/server.key
install -m 0644 -o postgres -g postgres /run/secrets/db_server_cert /run/pish-postgres-tls/server.crt

exec /usr/local/bin/docker-entrypoint.sh "$@"
