"""Prompt formulation and instruction engineering for Gemini Search Grounding.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §4 (grounded
search); ``AGENTS.md`` §2 Domain invariant 7 (anti-fabrication & grounded extraction);
Universal job coverage across all verified Iranian recruitment sources.

Scope
-----
Formulates targeted search prompts instructing Google Gemini with web grounding to
query all authoritative Iranian job boards, classifieds, and compensation surveys,
perform adjacent/related occupational semantic aggregation, and return realistic
compensation ranges formatted cleanly in multiples of 10 Rial (whole-Toman).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.salary_estimation.matcher import JobMatch
    from app.domain.salary_estimation.schemas import EstimationProfile

from app.domain.salary_estimation.taxonomy import family_by_key

__all__ = ("build_estimation_prompt",)


def build_estimation_prompt(
    profile: EstimationProfile,
    match: JobMatch | None = None,
) -> str:
    """Build a comprehensive, grounded prompt for Iranian labor market search."""
    family_title = (
        match.family_title_fa
        if match and match.family_key != "custom_role"
        else profile.job_title
    )
    keywords: tuple[str, ...] = ()
    skills_hint: tuple[str, ...] = ()

    if match and match.family_key != "custom_role":
        fam = family_by_key(match.family_key)
        if fam:
            keywords = fam.keywords
            skills_hint = fam.skills

    skills_list = ", ".join(profile.skills) if profile.skills else ", ".join(skills_hint)
    keywords_str = ", ".join(keywords) if keywords else profile.job_title

    return (
        "You are an expert Iranian labor market compensation researcher and data extractor.\n"
        "Search across verified Iranian recruitment platforms (JobVision, Jobinja, IranTalent, "
        "IranSalary, e-estekhdam, IranEstekhdam, Karboom, Divar, Sheypoor, LinkedIn Iran, and "
        "official annual salary reports) for authentic compensation data in Iran "
        "(in 1403-1404 / 2024-2025) for the following position:\n\n"
        f"- Target Job Title: {profile.job_title}\n"
        f"- Job Family (Persian): {family_title}\n"
        f"- Relevant Keywords: {keywords_str}\n"
        f"- Experience Level: {profile.experience_years} years\n"
        f"- Seniority Level: {profile.seniority_level} (junior / mid / senior / lead / manager)\n"
        f"- Employment Type: {profile.employment_type}\n"
        f"- Target City: {profile.city} (Province: {profile.province or profile.city})\n"
        f"- Work Condition: {profile.work_condition}\n"
        f"- Core Skills: {skills_list or 'Not specified'}\n"
        f"- Education: {profile.education or 'Not specified'}\n\n"
        "SEARCH SOURCES & CHANNELS ACROSS IRAN:\n"
        "1. Specialized Job Portals: Jobvision (جاب‌ویژن), Jobinja (جابینجا), "
        "IranTalent / IranSalary (ایران‌تلنت و ایران‌سلری), Quera (کوئرا), Karboom (کاربوم), "
        "e-estekhdam (ای‌استخدام), IranEstekhdam (ایران‌استخدام).\n"
        "2. General & Classified Listings: Divar recruitment (بخش استخدام دیوار), "
        "Sheypoor (شیپور), سامانه کاریابی وزارت کار (karyabi / shoghl.mcls.gov.ir).\n"
        "3. Professional & Reports: LinkedIn jobs in Iran, "
        "گزارش‌های سالانه جامع حقوق و دستمزد جاب‌ویژن، ایران‌سلری و گزارش‌های تخصصی منابع انسانی.\n\n"
        "ADJACENT & RELATED ROLE SEARCH AGGREGATION (نتایج نزدیک و همرده):\n"
        f"If exact matches for the specific job title '{profile.job_title}' are sparse, "
        "do NOT return null or zero. Instead, identify closely related, synonymous, and adjacent "
        "occupational roles in the Iranian market (e.g., if searching 'طراح رابط کاربری', also analyze "
        "'طراح UI/UX', 'طراح محصول', 'Product Designer'; if searching 'کارشناس دیجیتال مارکتینگ', "
        "also analyze 'کارشناس بازاریابی آنلاین', 'ادمین ارشد مارکتینگ'; if searching 'مهندس عمران', "
        "also analyze 'سرپرست کارگاه', 'مهندس اجرا', 'کارشناس دفتر فنی').\n"
        "Aggregate compensation ranges from these adjacent postings to establish a realistic, "
        "customary market range (e.g., 35 to 65 million Toman for mid-level professionals), "
        "reflecting standard Iranian market conventions for this experience level and city.\n\n"
        "GEOGRAPHIC CASCADE HIERARCHY:\n"
        f"1. Tier 1 (Local): Search for '{profile.job_title}' and related roles in '{profile.city}'. "
        "If >= 2 samples found, set \"cohort_scope\": \"city\".\n"
        f"2. Tier 2 (Metropolitan / Tehran): If localized samples in '{profile.city}' are fewer than 2, "
        "search Tehran and major metropolises with regional parity. Set \"cohort_scope\": \"province\".\n"
        "3. Tier 3 (National): If local data is sparse, provide the national benchmark across Iran. "
        "Set \"cohort_scope\": \"national\".\n\n"
        "CRITICAL ANTI-FABRICATION INVARIANT (ADR-014):\n"
        "- Extract authentic figures from postings, employer listings, or surveys.\n"
        "- Emitted figures must represent realistic, customary Iranian market compensation ranges.\n\n"
        "CURRENCY & NUMERICAL INVARIANTS:\n"
        "- Convert all amounts to monthly RIAL (IRR). 1 Toman = 10 Rial "
        "(e.g. 45 million Toman = 450,000,000 Rial, 70 million Toman = 700,000,000 Rial).\n"
        "- Minimum plausible monthly salary is 20,000,000 Rial (2,000,000 Toman) for internships / entry-level.\n"
        "- Emitted figures must be realistic, market-grounded figures formatted cleanly in whole-Toman "
        "multiples of 10 Rial without math errors.\n\n"
        "RESPONSE FORMAT:\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "found_data": true,\n'
        '  "cohort_scope": "city" | "province" | "national",\n'
        '  "refusal_reason": null,\n'
        '  "observations": [\n'
        "    {\n"
        '      "job_title_reported": "exact title or adjacent title analyzed",\n'
        '      "source_name": "Jobinja / Jobvision / IranTalent / e-estekhdam / Divar / etc.",\n'
        '      "source_url": "URL if available or null",\n'
        '      "city": "Tehran / etc.",\n'
        '      "seniority_level": "junior / mid / senior",\n'
        '      "amount_rial": 450000000,\n'
        '      "period": "monthly",\n'
        '      "license_status": "manual_verified",\n'
        '      "notes": "brief context or adjacent role relation"\n'
        "    }\n"
        "  ],\n"
        '  "aggregates": [\n'
        "    {\n"
        '      "source_name": "Jobvision 1403 Report / IranSalary Survey",\n'
        '      "job_title_reported": "reported or adjacent job title",\n'
        '      "city": "Tehran / National",\n'
        '      "seniority_level": "mid",\n'
        '      "p25_rial": 380000000,\n'
        '      "median_rial": 480000000,\n'
        '      "p75_rial": 620000000,\n'
        '      "sample_size": 150,\n'
        '      "source_url": "URL if available or null"\n'
        "    }\n"
        "  ],\n"
        '  "factors_influence": [\n'
        '    "عوامل موثر بر حقوق طبق شواهد وب و موقعیت‌های شغلی همرده"\n'
        "  ],\n"
        '  "factors_notes": [\n'
        '    "یادداشت‌های تحلیلی و شواهد آماری بازار کار"\n'
        "  ]\n"
        "}"
    )
