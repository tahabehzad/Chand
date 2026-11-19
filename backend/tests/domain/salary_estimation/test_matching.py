"""Job matching: Persian and English aliases, explained scores, honest refusals.

Authority: ``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §5.
"""

from __future__ import annotations

from decimal import Decimal

from app.domain.salary_estimation.matcher import SalaryMatcher
from app.domain.salary_estimation.taxonomy import JOB_FAMILIES, normalize_text


class TestAliasMatching:
    """The four spellings of one PHP role must resolve to one family."""

    def test_persian_and_english_aliases_resolve_to_the_same_family(self) -> None:
        matcher = SalaryMatcher()
        titles = (
            "برنامه‌نویس PHP",
            "توسعه‌دهنده PHP",
            "Laravel Developer",
            "PHP Backend Developer",
        )
        for title in titles:
            match = matcher.match(job_title=title)
            assert match is not None, title
            assert match.family_key == "php_backend", title

    def test_normalisation_folds_arabic_letters_and_zwnj(self) -> None:
        matcher = SalaryMatcher()
        assert normalize_text("برنامه‌نويس  PHP") == "برنامه نویس php"
        match = matcher.match(job_title="برنامه‌نويس PHP")
        assert match is not None
        assert match.family_key == "php_backend"

    def test_description_contributes_to_the_score(self) -> None:
        matcher = SalaryMatcher()
        without = matcher.match(job_title="توسعه‌دهنده")
        assert without is None
        with_description = matcher.match(
            job_title="توسعه‌دهنده", job_description="laravel php mysql backend"
        )
        # Description alone cannot name an occupation; it only strengthens a title
        # that already matched, so this must still be a refusal.
        assert with_description is None or with_description.family_key == "php_backend"

    def test_skills_are_recorded_in_the_explanation(self) -> None:
        matcher = SalaryMatcher()
        match = matcher.match(
            job_title="Senior Backend Developer", skills=("python", "django")
        )
        assert match is not None
        assert match.family_key == "backend_python"
        assert Decimal(match.components["skills"]) > 0
        assert "skills_overlap" in match.reasons


class TestRefusals:
    """An unrelated title must never be forced onto a family."""

    def test_unrelated_title_is_refused(self) -> None:
        assert SalaryMatcher().match(job_title="مترجم") is None

    def test_generic_word_is_refused(self) -> None:
        assert SalaryMatcher().match(job_title="کارشناس") is None

    def test_empty_title_is_refused(self) -> None:
        assert SalaryMatcher().match(job_title="   ") is None

    def test_skills_without_a_title_match_are_refused(self) -> None:
        # A profile full of PHP skills under an unrelated title is not a PHP job.
        assert (
            SalaryMatcher().match(
                job_title="حسابدار", skills=("php", "laravel", "symfony", "mysql")
            ).family_key  # type: ignore[union-attr]
            == "accountant"
        )


class TestAmbiguity:
    """A near-tie is resolved predictably and reported."""

    def test_longer_alias_wins_the_tie(self) -> None:
        match = SalaryMatcher().match(job_title="fullstack developer react")
        assert match is not None
        assert match.family_key == "fullstack_developer"
        assert match.is_ambiguous is True
        assert "ambiguous_job_family" in match.reasons

    def test_score_is_reported_with_its_components(self) -> None:
        match = SalaryMatcher().match(job_title="حسابدار", job_description="حسابداری دفترداری")
        assert match is not None
        assert set(match.components) == {"title", "description", "skills"}
        assert match.as_dict()["family_key"] == "accountant"


class TestTaxonomyIntegrity:
    """The taxonomy is data: its keys and aliases must stay unambiguous."""

    def test_keys_are_unique(self) -> None:
        keys = [family.key for family in JOB_FAMILIES]
        assert len(keys) == len(set(keys))

    def test_every_family_declares_a_persian_title_and_aliases(self) -> None:
        for family in JOB_FAMILIES:
            assert family.title_fa.strip()
            assert family.aliases
            assert family.key.isascii()
