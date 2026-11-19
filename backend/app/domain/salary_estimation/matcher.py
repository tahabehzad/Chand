"""Job matching: canonical family resolution with an explained score.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §5 (title,
description, skills and seniority all contribute; every match carries its reasons;
an unrelated title must be refused rather than forced onto a family);
``docs/AI_ANALYSIS_SPEC.md`` §3 (no invented market fact — a family is a
classification, not a salary).

Related
-------
``taxonomy.py`` (the family table and the normaliser),
``salary_estimator.py`` (refuses an estimation when ``match`` returns ``None``).

Scope
-----
Pure matching.  No salary table, no market data and no clock.  The previous
implementation matched five hard-coded English keys by exact string equality
against a mock table; this one matches a normalised title, description and skills
against the taxonomy and explains the score.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from .taxonomy import JOB_FAMILIES, JobFamily, normalize_text, tokenize

__all__ = ("JobMatch", "SalaryMatcher")

#: Weight of each signal in the final score.  They sum to 1.
_TITLE_WEIGHT = Decimal("0.55")
_DESCRIPTION_WEIGHT = Decimal("0.25")
_SKILLS_WEIGHT = Decimal("0.20")

#: Below this score no family is claimed.  The estimator then refuses with
#: ``insufficient_data`` instead of estimating an unrelated occupation.
DEFAULT_MINIMUM_SCORE = Decimal("0.45")

#: Two families closer than this are reported as ambiguous; the higher one is
#: still used, but the output says so and confidence is reduced.
AMBIGUITY_MARGIN = Decimal("0.05")


@dataclass(frozen=True)
class JobMatch:
    """The resolved family, its score and the reasons behind it."""

    family_key: str
    family_title_fa: str
    score: Decimal
    reasons: tuple[str, ...]
    components: dict[str, str]

    @property
    def is_ambiguous(self) -> bool:
        """Whether another family scored almost as high."""
        return "ambiguous_job_family" in self.reasons

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable view for the API report."""
        return {
            "family_key": self.family_key,
            "family_title_fa": self.family_title_fa,
            "score": f"{self.score:.3f}",
            "components": dict(self.components),
            "reasons_fa": list(self.reasons),
        }


def _title_score(
    family: JobFamily, title: str, title_tokens: tuple[str, ...]
) -> tuple[Decimal, int]:
    """Return ``(score, matched_alias_length)`` for how strongly *title* names *family*.

    The alias length is the tie-breaker: when two families are contained in the
    same title ("fullstack developer react" naming both the full-stack and the
    front-end alias), the longer, more specific alias wins.
    """
    best = Decimal(0)
    best_length = 0
    for alias in family.aliases:
        normalised_alias = normalize_text(alias)
        if not normalised_alias:
            continue
        if normalised_alias == title:
            return Decimal(1), len(normalised_alias)
        alias_tokens = tokenize(normalised_alias)
        if alias_tokens and all(token in title_tokens for token in alias_tokens):
            if Decimal("0.9") > best:
                best, best_length = Decimal("0.9"), len(normalised_alias)
            elif Decimal("0.9") == best and len(normalised_alias) > best_length:
                best_length = len(normalised_alias)
            continue
        if not alias_tokens or not title_tokens:
            continue
        shared = len(set(alias_tokens) & set(title_tokens))
        union = len(set(alias_tokens) | set(title_tokens))
        if union:
            candidate = Decimal("0.7") * Decimal(shared) / Decimal(union)
            if candidate > best:
                best, best_length = candidate, len(normalised_alias)
    return best, best_length


def _keyword_score(family: JobFamily, text_tokens: Sequence[str]) -> Decimal:
    """Return the share of *family* keywords present in a description."""
    if not family.keywords or not text_tokens:
        return Decimal(0)
    hits = 0
    for keyword in family.keywords:
        keyword_tokens = set(tokenize(keyword))
        if keyword_tokens and keyword_tokens <= set(text_tokens):
            hits += 1
    return min(Decimal(1), Decimal(hits) / Decimal(3))


def _skills_score(family: JobFamily, skills: Sequence[str]) -> Decimal:
    """Return the share of the family's canonical skills the profile declares."""
    if not family.skills or not skills:
        return Decimal(0)
    declared = {normalize_text(skill) for skill in skills}
    matched = sum(1 for skill in family.skills if normalize_text(skill) in declared)
    return Decimal(matched) / Decimal(len(family.skills))


@dataclass(frozen=True)
class SalaryMatcher:
    """Resolve a candidate profile to one canonical job family."""

    families: tuple[JobFamily, ...] = JOB_FAMILIES
    minimum_score: Decimal = DEFAULT_MINIMUM_SCORE

    def match(
        self,
        *,
        job_title: str,
        job_description: str | None = None,
        skills: Sequence[str] = (),
        seniority_level: str | None = None,
    ) -> JobMatch | None:
        """Return the best family for the profile, or ``None`` when unrelated.

        ``seniority_level`` is consulted for the explanation only.  It cannot
        create a match: seniority narrows a cohort, it never names an occupation.
        """
        title = normalize_text(job_title)
        title_tokens = tokenize(job_title)
        description_tokens = tokenize(job_description or "")
        if not title_tokens:
            return None

        scored: list[tuple[Decimal, int, JobFamily, Decimal, Decimal, Decimal]] = []
        for family in self.families:
            title_component, alias_length = _title_score(family, title, title_tokens)
            if title_component == 0:
                # Description and skills alone can never name an occupation.
                continue
            description_component = _keyword_score(family, description_tokens)
            skills_component = _skills_score(family, skills)
            total = (
                title_component * _TITLE_WEIGHT
                + description_component * _DESCRIPTION_WEIGHT
                + skills_component * _SKILLS_WEIGHT
            )
            scored.append(
                (
                    total,
                    alias_length,
                    family,
                    title_component,
                    description_component,
                    skills_component,
                )
            )

        if not scored:
            return None
        scored.sort(key=lambda item: (-item[0], -item[1], item[2].key))
        total, _alias_length, family, title_component, description_component, skills_component = (
            scored[0]
        )
        if total < self.minimum_score:
            return None

        reasons: list[str] = []
        if title_component == 1:
            reasons.append("title_exact_alias")
        elif title_component >= Decimal("0.9"):
            reasons.append("title_alias_contained")
        else:
            reasons.append("title_partial_tokens")
        if description_component > 0:
            reasons.append("description_keywords")
        if skills_component > 0:
            reasons.append("skills_overlap")
        if seniority_level:
            reasons.append("seniority_recorded")
        if len(scored) > 1 and scored[1][0] >= total - AMBIGUITY_MARGIN:
            reasons.append("ambiguous_job_family")

        return JobMatch(
            family_key=family.key,
            family_title_fa=family.title_fa,
            score=total,
            reasons=tuple(reasons),
            components={
                "title": f"{title_component:.3f}",
                "description": f"{description_component:.3f}",
                "skills": f"{skills_component:.3f}",
            },
        )
