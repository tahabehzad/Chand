FROM postgres:16.16-bookworm

# P0-T03: official image + signed distribution package. Record the pulled
# digest/package versions after a successful build; this is a dev image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-16-pgaudit \
    && rm -rf /var/lib/apt/lists/*

COPY postgresql.conf pg_hba.conf /etc/pish-postgres/
COPY init.sql /docker-entrypoint-initdb.d/010-hardening.sql
COPY entrypoint.sh /usr/local/bin/pish-postgres-entrypoint
RUN chmod 0755 /usr/local/bin/pish-postgres-entrypoint

ENTRYPOINT ["pish-postgres-entrypoint"]
CMD ["postgres", "-c", "config_file=/etc/pish-postgres/postgresql.conf"]
