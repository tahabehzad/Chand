"""Job-family taxonomy and Persian/English text normalisation.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §5 (internal,
owner-editable taxonomy first; a standard classification can be mapped onto it
later); ``docs/AI_ANALYSIS_SPEC.md`` §3 B-01/B-02 (no invented market facts).

Related
-------
``matcher.py`` consumes :class:`JobFamily` records; ``validation.py`` groups
observations by :attr:`JobFamily.key`.

Scope
-----
A data table plus pure normalisation helpers.  No salary value, weight or
threshold lives here: this module only answers *what a job is called*.

WARNING (recorded, not resolved): the family list is a starting set drafted from
the job titles already used by the project's own screens.  Choosing an official
classification (ISCO-08 or the Iranian national classification) is an owner
decision recorded in ``docs/DECISIONS_REGISTER.md`` DEC-016.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

__all__ = (
    "JOB_FAMILIES",
    "JobFamily",
    "family_by_key",
    "normalize_text",
    "tokenize",
)

_PUNCTUATION = re.compile(r"[^\w\s\u0600-\u06FF+#.]", re.UNICODE)
_WHITESPACE = re.compile(r"\s+", re.UNICODE)

#: Characters that differ between Persian and Arabic orthography in real
#: postings.  Folding them is what makes "توسعه‌دهنده" match "توسعه دهنده".
_FOLD = str.maketrans(
    {
        "\u064a": "\u06cc",  # ي -> ی
        "\u0643": "\u06a9",  # ك -> ک
        "\u0629": "\u0647",  # ة -> ه
        "\u0640": "",  # tatweel
        "\u200c": " ",  # ZWNJ -> space
        "\u200e": "",
        "\u200f": "",
        "\u202b": "",
        "\u202c": "",
    }
)


@dataclass(frozen=True)
class JobFamily:
    """One canonical job family with the aliases known for it.

    ``key`` is the stable identifier stored on every market observation.  It is
    never derived from user input, so renaming an alias can never orphan data.
    """

    key: str
    title_fa: str
    #: Lower-case, already normalised aliases (Persian and English).
    aliases: tuple[str, ...]
    #: Tokens that indicate the family in a job description or skills list.
    keywords: tuple[str, ...]
    #: Canonical skills associated with the family (used for match scoring).
    skills: tuple[str, ...] = ()
    #: The statutory/official classification code, once one is chosen.
    external_code: str | None = None


JOB_FAMILIES: tuple[JobFamily, ...] = (
    JobFamily(
        key="php_backend",
        title_fa="برنامه‌نویس بک‌اند PHP",
        aliases=(
            "برنامه نویس php",
            "برنامه‌نویس php",
            "توسعه‌دهنده php",
            "توسعه دهنده php",
            "php developer",
            "php backend developer",
            "laravel developer",
            "back-end php developer",
            "backend php developer",
            "برنامه‌نویس لاراول",
        ),
        keywords=("php", "laravel", "symfony", "mysql", "بک‌اند", "backend"),
        skills=("php", "laravel", "symfony", "mysql"),
    ),
    JobFamily(
        key="frontend_react",
        title_fa="توسعه‌دهنده فرانت‌اند",
        aliases=(
            "توسعه‌دهنده فرانت اند",
            "توسعه‌دهنده فرانت‌اند",
            "برنامه‌نویس فرانت اند",
            "react developer",
            "frontend developer",
            "front-end developer",
            "react frontend developer",
            "توسعه‌دهنده ری‌اکت",
        ),
        keywords=("react", "frontend", "front-end", "javascript", "typescript", "فرانت"),
        skills=("react", "typescript", "javascript", "css"),
    ),
    JobFamily(
        key="backend_python",
        title_fa="توسعه‌دهنده بک‌اند پایتون",
        aliases=(
            "توسعه‌دهنده پایتون",
            "برنامه‌نویس پایتون",
            "backend developer",
            "python developer",
            "python backend developer",
            "django developer",
        ),
        keywords=("python", "django", "fastapi", "flask", "بک‌اند"),
        skills=("python", "django", "fastapi", "postgresql"),
    ),
    JobFamily(
        key="fullstack_developer",
        title_fa="توسعه‌دهنده فول‌استک",
        aliases=(
            "توسعه‌دهنده فول استک",
            "توسعه‌دهنده فول‌استک",
            "fullstack developer",
            "full-stack developer",
            "full stack developer",
        ),
        keywords=("fullstack", "full-stack", "فول‌استک", "react", "node"),
        skills=("react", "node.js", "typescript", "sql"),
    ),
    JobFamily(
        key="qa_engineer",
        title_fa="کارشناس تست نرم‌افزار",
        aliases=(
            "کارشناس تست",
            "تستر نرم‌افزار",
            "مهندس تست",
            "qa engineer",
            "test engineer",
            "quality assurance engineer",
        ),
        keywords=("qa", "testing", "selenium", "تست", "کیفیت"),
        skills=("pytest", "selenium", "cypress", "postman"),
    ),
    JobFamily(
        key="accountant",
        title_fa="حسابدار",
        aliases=("حسابدار", "کارشناس حسابداری", "accountant", "accounting specialist"),
        keywords=("حسابداری", "دفترداری", "مالی", "حساب", "accounting", "ledger"),
        skills=("excel", "راهکاران", "سپیدار"),
    ),
    JobFamily(
        key="sales_representative",
        title_fa="کارشناس فروش",
        aliases=(
            "نماینده فروش",
            "نمایندۀ فروش",
            "کارشناس فروش",
            "فروشنده",
            "sales representative",
            "sales specialist",
        ),
        keywords=("فروش", "بازاریابی", "sales", "crm"),
        skills=("crm", "مذاکره"),
    ),
    JobFamily(
        key="hr_manager",
        title_fa="مدیر منابع انسانی",
        aliases=("مدیر منابع انسانی", "مدیر منابع انسانی و اداری", "hr manager", "hr specialist"),
        keywords=("منابع انسانی", "جذب", "hr", "recruitment"),
        skills=("recruitment", "hris"),
    ),
    JobFamily(
        key="mechanical_engineer",
        title_fa="مهندس مکانیک",
        aliases=("مهندس مکانیک", "کارشناس مکانیک", "mechanical engineer"),
        keywords=("مکانیک", "mechanical", "cad", "سالیدورک"),
        skills=("solidworks", "autocad", "catia"),
    ),
    JobFamily(
        key="driver",
        title_fa="راننده",
        aliases=("راننده", "راننده پایه یک", "driver", "truck driver"),
        keywords=("رانندگی", "حمل و نقل", "driver"),
        skills=("گواهینامه پایه یک",),
    ),
)


def normalize_text(value: str) -> str:
    """Return *value* folded for matching: orthography, case, punctuation.

    The function is deliberately conservative — it never translates between
    Persian and English, because a translation would silently equate two
    different job families.
    """
    decomposed = unicodedata.normalize("NFKC", value)
    folded = decomposed.translate(_FOLD).lower()
    without_punctuation = _PUNCTUATION.sub(" ", folded)
    return _WHITESPACE.sub(" ", without_punctuation).strip()


def tokenize(value: str) -> tuple[str, ...]:
    """Return the normalised tokens of *value*."""
    normalised = normalize_text(value)
    return tuple(token for token in normalised.split(" ") if token)


def family_by_key(key: str) -> JobFamily | None:
    """Return the family with *key*, or ``None`` when it is not in the taxonomy."""
    for family in JOB_FAMILIES:
        if family.key == key:
            return family
    return None
