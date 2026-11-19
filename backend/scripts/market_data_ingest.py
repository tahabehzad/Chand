"""Import verified market salary observations from a CSV file.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §2.4 (a row may
enter only with a source, a licence state, a collection date and a currency unit;
validation runs before storage); ``docs/LABOR_MARKET_DATA_SPEC.md`` R-01…R-05.

Related
-------
``app/repositories/market_data.py`` (storage),
``app/domain/salary_estimation/validation.py`` (the same classifier the estimator
runs), ``app/domain/salary_estimation/taxonomy.py`` (family keys).

Scope
-----
A one-shot operator tool.  It never scrapes, never guesses a licence and never
invents a figure: every row must arrive with its provenance, and a row that fails
validation is stored with its verdict and reason instead of being dropped.

Usage
-----
    python scripts/market_data_ingest.py --file observations.csv \
        --source-id survey-1405-x --source-name "گزارش حقوق ۱۴۰۵" \
        --kind licensed_survey --license-status licensed \
        --terms-url https://example.invalid/terms

    python scripts/market_data_ingest.py --census

CSV header (UTF-8, comma separated)::

    family_key,job_title_reported,city,province,seniority_level,experience_years,
    employment_type,work_condition,amount,period,currency,collected_at,source_url

``amount`` is the figure **as published**, with ``currency`` saying whether it is
Rial or Toman; normalisation happens in the estimator and is reported there.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import get_settings
from app.db import build_engine, build_session_factory
from app.domain.salary_estimation.market_data import (
    DataQuality,
    MarketObservation,
    MarketSource,
)
from app.domain.salary_estimation.taxonomy import JOB_FAMILIES
from app.domain.salary_estimation.validation import (
    ValidationPolicy,
    classify_observations,
    reason_text,
)
from app.repositories.market_data import SqlMarketDataRepository

FAMILY_KEYS = {family.key for family in JOB_FAMILIES}
PERIODS = {"monthly", "hourly", "daily"}
CURRENCIES = {"rial", "toman"}


def _row_id(source_id: str, row: dict[str, str]) -> str:
    """Return a stable id derived from the row's own content."""
    payload = "|".join(
        [
            source_id,
            row["family_key"].strip(),
            row["city"].strip(),
            row.get("seniority_level", "").strip(),
            row["amount"].strip(),
            row["period"].strip(),
            row["collected_at"].strip(),
        ]
    )
    return f"{source_id}-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"


def _parse_row(row: dict[str, str], source_id: str) -> MarketObservation:
    """Turn one CSV row into an observation, refusing malformed input."""
    family_key = row["family_key"].strip()
    if family_key not in FAMILY_KEYS:
        raise ValueError(f"unknown family_key {family_key!r}; see app/domain/salary_estimation/taxonomy.py")
    period = row["period"].strip()
    if period not in PERIODS:
        raise ValueError(f"period must be one of {sorted(PERIODS)}")
    currency = row["currency"].strip()
    if currency not in CURRENCIES:
        raise ValueError(f"currency must be one of {sorted(CURRENCIES)}")
    amount = int(row["amount"].strip())
    if amount <= 0:
        raise ValueError("amount must be a positive integer of the reported currency")
    collected_at = datetime.fromisoformat(row["collected_at"].strip())
    if collected_at.tzinfo is None:
        collected_at = collected_at.replace(tzinfo=UTC)

    experience = row.get("experience_years", "").strip()
    return MarketObservation(
        id=_row_id(source_id, row),
        family_key=family_key,
        job_title_reported=row["job_title_reported"].strip(),
        city=row["city"].strip(),
        province=(row.get("province") or "").strip() or None,
        seniority_level=(row.get("seniority_level") or "").strip() or None,
        experience_years=int(experience) if experience else None,
        employment_type=(row.get("employment_type") or "").strip() or None,
        work_condition=(row.get("work_condition") or "").strip() or None,
        amount_rial=amount,
        period=period,
        currency_unit_reported=currency,
        source_id=source_id,
        source_url=(row.get("source_url") or "").strip() or None,
        license_status=row["license_status"].strip(),
        collected_at=collected_at,
        is_synthetic=False,
    )


async def _ingest(args: argparse.Namespace, rows: list[dict[str, str]], file_name: str) -> int:
    """Validate, classify and store the rows that ``main`` already read."""
    settings = get_settings()
    database_url = settings.database_url.get_secret_value()
    if not database_url:
        print("DATABASE_URL is not configured; nothing was imported.", file=sys.stderr)
        return 2

    observations: list[MarketObservation] = []
    for index, row in enumerate(rows, start=2):
        row.setdefault("license_status", args.license_status)
        row["license_status"] = args.license_status
        try:
            observations.append(_parse_row(row, args.source_id))
        except (KeyError, ValueError) as exc:
            print(f"line {index}: {exc}", file=sys.stderr)
            return 2

    as_of = datetime.now(UTC)
    outcome = classify_observations(
        observations,
        as_of=as_of,
        policy=ValidationPolicy(max_age_days=settings.estimation_max_data_age_days),
    )
    verdicts = {finding.observation_id: finding for finding in outcome.findings}

    flagged = [
        MarketObservation(
            **{
                **observation.__dict__,
                "data_quality_status": verdicts[observation.id].status,
                "quality_reason": ", ".join(verdicts[observation.id].reasons) or None,
            }
        )
        if observation.id in verdicts
        else observation
        for observation in observations
    ]

    summary = dict.fromkeys(DataQuality.ALL, 0)
    for observation in flagged:
        summary[observation.data_quality_status] += 1

    print(f"parsed {len(flagged)} rows from {file_name}")
    for status, count in summary.items():
        print(f"  {status}: {count}")
    for code, count in sorted(outcome.quarantine_reasons.items()):
        print(f"  reason {code} ({reason_text(code)}): {count}")

    if args.dry_run:
        print("dry run: nothing written")
        return 0

    repository = SqlMarketDataRepository(build_session_factory(build_engine(database_url)))
    await repository.store_source(
        MarketSource(
            id=args.source_id,
            name=args.source_name,
            kind=args.kind,
            license_status=args.license_status,
            connected=True,
            terms_url=args.terms_url,
            notes=args.notes,
        )
    )
    written = await repository.store_observations(flagged)
    print(f"stored {written} rows and registered source {args.source_id!r}")
    return 0


async def _census() -> int:
    """Print how much verified data the store actually holds."""
    settings = get_settings()
    database_url = settings.database_url.get_secret_value()
    if not database_url:
        print("DATABASE_URL is not configured.", file=sys.stderr)
        return 2
    repository = SqlMarketDataRepository(build_session_factory(build_engine(database_url)))
    sources = await repository.sources()
    print(f"sources registered: {len(sources)}")
    for source in sources:
        state = "connected" if source.connected else "not connected"
        print(f"  {source.id} [{source.license_status}] {state}")
    total = 0
    for family in JOB_FAMILIES:
        rows = await repository.observations_for(family.key)
        total += len(rows)
        if rows:
            usable = sum(1 for row in rows if row.license_status in {"licensed", "published_report", "manual_verified"})
            print(f"  {family.key}: {len(rows)} rows ({usable} from approved licences)")
    print(f"observations total: {total}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="CSV file of observations")
    parser.add_argument("--source-id", help="stable source identifier, e.g. survey-1405-x")
    parser.add_argument("--source-name", help="human-readable source name")
    parser.add_argument(
        "--kind",
        default="manual",
        choices=("licensed_survey", "published_report", "job_board", "manual", "synthetic"),
    )
    parser.add_argument(
        "--license-status",
        default="manual_verified",
        choices=("licensed", "published_report", "manual_verified", "unknown"),
    )
    parser.add_argument("--terms-url", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--census", action="store_true")
    args = parser.parse_args(argv)

    if args.census:
        return asyncio.run(_census())
    if not args.file or not args.source_id or not args.source_name:
        parser.error("--file, --source-id and --source-name are required unless --census is used")
    path = Path(args.file)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("the file contains no rows; nothing was imported.", file=sys.stderr)
        return 2
    return asyncio.run(_ingest(args, rows, path.name))


if __name__ == "__main__":
    raise SystemExit(main())
