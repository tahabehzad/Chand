---
name: llm-market-grounding
description: Governs Google Gemini Search Grounding for Iranian labor market data: prompt synthesis, anti-hallucination constraints, refusal invariants, Persian currency normalization (Toman to Rial), and grounding citation extraction.
---

# LLM Market Grounding Skill

## Purpose
Ensure that any integration with Large Language Models (specifically Google Gemini with Google Search Grounding) extracts objective, verifiable Iranian labor market salary observations from real web sources, strictly enforces the "Refuse instead of Fabricate" invariant, and converts noisy Iranian currency data into integer Rial without introducing mathematical or rounding errors.

---

## 1. Anti-Hallucination & Refusal Invariants (AGENTS.md §2 Invariant 7)
1. **Extraction, Never Invention:** The LLM is an information extraction agent, never an actuarial or economic guesser. If real job postings, salary surveys, or market reports for the requested cohort do not exist in the search results, the engine must return `insufficient_data`.
2. **Explicit Null Constraints in Prompts:** Every prompt sent to the LLM must carry an unambiguous refusal clause:  
   *"If no verified salary range or compensation data is found on Iranian job portals for this role, return null for all numerical fields. Do NOT guess, interpolate, or estimate."*
3. **No Unmeasured National Fallback:** If a profile cannot be matched to real market observations in the target city/seniority cohort, never fall back to an unverified national average or model-generated guess.

---

## 2. Query Construction Discipline
4. **Taxonomy-Driven Keywords:** Use the canonical definitions in `backend/app/domain/salary_estimation/taxonomy.py`. Queries must combine:
   - Canonical Persian title (`JobFamily.title_fa`)
   - Common aliases (`JobFamily.aliases`)
   - Target Iranian employment portals: JobVision (جاب‌ویژن), Jobinja (جابینجا), IranTalent/IranSalary (ایران‌تلنت / ایران‌سلری), Quera (کوئرا), Karboom (کاربوم).
5. **Zero PII Leakage:** Never include candidate identity details (names, contact info, previous employers) in LLM search queries. Queries must only contain general cohort parameters: `job_title`, `city`, `seniority_level`, and `employment_type`.

---

## 3. Currency & Text Normalization
6. **Folding & Normalization:** Use `taxonomy.normalize_text()` and `numerals.normaliseNumericInput()` to fold Persian/Arabic digits, tatweel, and ZWNJ before parsing.
7. **Strict Currency Conversion:**
   - Detect unit: "تومان", "میلیون تومان", "ریال".
   - Standardize to base Toman, then multiply by 10 to store as canonical integer Rial.
   - Example: «۳۵ میلیون تومان» → `35,000,000` Toman → `350,000,000` Rial.
8. **Decimal Precision Rule:** Monetary figures must be parsed into `decimal.Decimal` with `getcontext().prec = 34` and rounded with `ROUND_HALF_UP`. Floating-point arithmetic (`float`) is banned.
9. **Money Path Validation:** Every parsed salary figure must pass `validate_estimate_money_path()` before being returned to the domain layer.

---

## 4. Citation, Provenance & Transparency
10. **Compulsory Citations:** An extracted data point without a source URL is invalid. Every `MarketDataRow` must contain:
    - `source`: Platform name (e.g., "جاب‌ویژن", "جابینجا")
    - `source_url`: Verifiable web link retrieved from search grounding
    - `collected_at`: Collection timestamp (ISO 8601)
    - `sample_count`: Validated sample count (or 1 for individual job postings)
11. **Data Source Mode Tagging:** The API response must explicitly declare how data was obtained:
    - `"gemini_live"`: Retrieved via real-time search grounding.
    - `"database_fallback"`: Retrieved from local PostgreSQL reference tables.
    - `"hybrid"`: Combined live observations and historical aggregates.

---

## 5. Resilience & Fallback Flow
12. **Graceful Fallback:** If Gemini API fails (network interruption, invalid/expired API key, quota limit), the service must catch `GeminiApiError` and seamlessly fall back to local `MarketDataRepository` observations.
13. **Clean Refusals:** If both Gemini live search and the local database lack sufficient samples, raise `InsufficientMarketDataError` which translates to HTTP 409 with missing sample counts, not an unhandled 500 error.

---

## 6. BYOK (Bring Your Own Key) Security & Privacy
14. **No Central API Key Storage:** In BYOK mode, the Gemini API key belongs to the user and is stored in browser `localStorage`. It is delivered in the request body per call.
15. **Zero Key Logging:** Never log, print, or expose the Gemini API key in backend logs, debug traces, or error payloads.
16. **Stateless Candidate Privacy:** Never persist candidate salary estimates or inputs to the database. Calculations are performed in-memory and returned directly to the client.
