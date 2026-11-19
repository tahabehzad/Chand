# Specification: Statutory Parameter Ingestion & Verification

- **Document ID:** `SPEC-STAT-001`
- **Status:** Draft — awaiting Legal Counsel and Certified Tax Accountant sign-off
- **Author:** Documentation Engineering (Chief Software Architect workstream)
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](../EXECUTION_PLAN.md) §3 · [`docs/DECISIONS_REGISTER.md`](../DECISIONS_REGISTER.md) DEC-001 · `docs/adr/ADR-003-sensitive-data-encryption-alee-blind-indexing.md`

> **Scope.** This document defines *how* a Solar Hijri statutory rule set enters the system, who verifies it, how it is versioned, and what must be true before it may be used to compute a real offer. It does **not** authorise activation of any 1405 parameter. The activation gate in §7 is currently **NOT MET**.

---

## 1. Source Identification

### 1.1 Authority ladder

A statutory parameter may only enter the engine if it is traceable to a source at the highest reachable level. Where a lower level is used, the parameter must carry a `verification_status` of `UNVERIFIED` and may not be activated.

| Level | Source | Examples | Admissible for activation |
| :--- | :--- | :--- | :--- |
| L1 | Primary official publication (PDF, gazette, government portal) | `mcls.gov.ir` circular PDF, `rrk.ir` gazette, Council of Ministers resolution PDF | **Yes** |
| L2 | Official circular reproduced verbatim by a licensed legal database | `shenasname.ir` (شناسنامه قانون), `ekhtebar.ir` | Yes, if the reproduction carries the resolution number and date and is archived |
| L3 | Professional secondary publication (accounting firms, labour-law advisory) | `dadyarkar.ir`, `kartaban.com`, `sarayehesabdar.ir` | **No** — corroboration only |
| L4 | News media / aggregator | various | **No** — discovery only |

### 1.2 Mandatory source set for a Solar Hijri year `Y`

| # | Parameter family | Issuing authority | Channel | Document |
| :-- | :--- | :--- | :--- | :--- |
| S1 | Minimum daily wage, wage-level uplift, seniority base, grocery allowance, marriage allowance | High Council of Labor (شورای عالی کار) | Ministry of Cooperatives, Labour and Social Welfare (وزارت تعاون، کار و رفاه اجتماعی) | Wage circular for year `Y` (bends 1–9) |
| S2 | Housing allowance (حق مسکن) | Council of Ministers (هیئت وزیران) on a High Council of Labor proposal | Cabinet resolution | `تصویبنامه` with resolution number and date |
| S3 | Child allowance (حق اولاد) | Labour Law Art. 86 (statutory formula) + S1 | Labour Law | Formula applied to S1 daily wage |
| S4 | Insurable wage ceiling (سقف دستمزد مشمول کسر حق بیمه) | Social Security Organisation (تأمین اجتماعی) | SSO circular on the insurance base | "بخشنامه دستمزد مبنای کسر حق بیمه" year `Y` |
| S5 | Social Security contribution rates | Social Security Law Art. 28 | Statute | Statute (stable, re-verified annually) |
| S6 | Salary income tax exemption ceiling and progressive rates | Majlis (مجلس شورای اسلامی) | Budget Law (قانون بودجه / قانون الزامات بودجه‌های سنواتی) year `Y` | Budget Law ماده واحده |
| S7 | Non-cash benefit exemption (Art. 91 DTA) | Direct Taxes Act | Budget Law + DTA | Formula applied to S6 |
| S8 | Eydi ceiling (1370 Law) | Labour Law + Budget Law | Statute | Formula applied to S1 |

### 1.3 Primary-source reachability status (verified 2026-11-14)

| Channel | Attempted | Result |
| :--- | :--- | :--- |
| `www.mcls.gov.ir` | HTTP + HTTPS | **Transport error** — unreachable from the build environment |
| `www.tamin.ir` | HTTPS | **HTTP 403** — bot protection |
| `www.intamedia.ir` | HTTPS | **Transport error** — unreachable |
| `www.rrk.ir` (Official Gazette) | — | Not attempted; L1 not reachable |
| Legal databases (`shenasname.ir`) | HTTPS | **Reachable** — L2 |
| General internet egress | HTTPS | **Reachable** (`example.com` 200 OK) |

**Consequence:** no **L1** primary PDF could be retrieved from this environment. The transcription in §3 is therefore **L2/L3-sourced**. Per §7 the 1405 rule set **remains disabled**.

### 1.4 Latest acquisition probe — 2026-11-15

Parent ran the bounded collector against all six official discovery entries. Ministry, tax authority and gazette: `TRANSPORT_FAILED`. SSO homepage, SSO wage-news discovery URL and Cabinet/legal portal: HTTP **403**. Zero complete HTTP-200 bodies or primary PDFs captured. Failure manifests exist in git-ignored `.freebuff/statutory-acquisition/`, with UTC retrieval times, source IDs, statuses and UNVERIFIED/LOCAL_STAGING flags. Final-code SSO repeat also returned 403. This is evidence of current reachability failure, not a legal-source completeness assessment or proof that an amendment does not exist. No gate or rule status changed. See BOOTSTRAP_CHANGELOG §16.

---

### 1.5 Owner-requested current-year recheck — 2026-11-17

Owner requested official-source verification and backend activation for 1405. Accountable owner: Codex /root, P1-T02 evidence collection; no legal verifier or certified accountant is asserted. This dated addendum does not overwrite the historical transcription or satisfy A1–A8.

- Fresh bounded official collector results: ministry `TRANSPORT_FAILED`; SSO `HTTP_REJECTED` / 403; tax authority `TRANSPORT_FAILED`; Official Gazette `TRANSPORT_FAILED`; Cabinet/legal portal `HTTP_REJECTED` / 403. Failure manifests are in `.freebuff/statutory-acquisition/20261117T120230-labor-4b9ce6fd97704b8dba5f0c2377552908/`, `20261117T120238-sso-9878af5b72e54081869f5f1156e65be9/`, `20261117T120239-tax-0b67c15e80314ce69f37d2591ce8bc18/`, `20261117T120413-gazette-b499fa6798a94cd79f40affbd7358082/`, and `20261117T120413-cabinet-7a4950b499ae4757b3ed8c1adf2450df/`. Web access to the official wage news page also failed. No challenge or access restriction was bypassed.
- Acquired two reproduced primary documents for review, **not official-host captures**: [S1 circular 6682, 1405/01/31](https://bidbarg.net/documents/100/mozd1405.pdf), SHA-256 `3a48fa71fbc7a3219ac8ba5f6a0cc88574493bfc2d69828df68176b8ca7aa65a`; [S6 circular 1005/200/ص, 1405/01/31](https://shenasname.ir/wp-content/uploads/2026/04/بخشنامه-احکام-مالیاتی-قانون-بودجه-سال-۱۴۰۵-کل-کشور.pdf), SHA-256 `f3e9bf0080784189e5a61a4a400818e893506fd4a5cfe3c02476e2b772be728e`. Raw bytes and manifest: `.freebuff/statutory-acquisition/1405-reproductions-1794917085659252900/`. This is LOCAL_STAGING, UNVERIFIED, activation_eligible=false; it is not WORM archival or cryptographic legal-verifier sign-off.
- Read the source text: S1 states daily minimum 5,541,850 Rial, daily seniority base 166,667, monthly grocery 22,000,000 and marriage allowance 5,000,000. S6 page 2 states annual exemption 4,800 million Rial and annual bands 9,600 / 12,000 / 14,400 / 16,800 million Rial at 10 / 15 / 20 / 25 / 30 percent. These corroborate the existing candidate table only, not all statutory inputs. They are not written to an active rule set.
- The SSO circular reproduction at `https://hoghogh.ai/circulars/c-37c3a40f` is discovery evidence only, not proof of an archived latest original. Discovery also surfaced references to tax circular 200/1405/59 dated 1405/07/27 about welfare-benefit treatment; its original was not acquired. Its applicability/effective period must be checked before assuming that changing annual thresholds alone updates current-year tax logic. Housing-resolution verification and O1–O5 remain open.
- Activation remains blocked by missing A1 specialist signatures, A3 official-source-family originals, A4 closure of open items, A6 certified vectors, and A7–A8 approval/persistence. Local reproduction hashes alone do not satisfy these gates. No seed, loader allowlist, request default or year label changed. P1-T02 stays BLOCKED, P1-T03 NOT_STARTED; verified 1404 remains the only usable baseline. See BOOTSTRAP_CHANGELOG §41 for fresh commands/tests.

## 2. Document Acquisition and Archival

### 2.1 Bounded acquisition implementation contract — 2026-11-15

Owner-authorized first slice of P1-T02 (evidence collection only; the WBS task remains BLOCKED on external verification). Accountable owner: Codex `/root`. No prerequisite is claimed for independent public-source acquisition; database integration depends on P0-T04 and WORM integration on P0-T11. This slice does not implement those tasks.

- A manually invoked CLI collects only public HTTPS GET responses from an explicit official-host catalog (ministry, SSO, tax authority, gazette and Cabinet/legal portal). Homepage/news captures are discovery evidence, never proof of a complete circular or latest law. No candidate data, credentials, cookies or external AI service is involved. No automatic schedule or queue is selected.
- Permit port 443 only; reject userinfo, queries and fragments, non-allowlisted hosts, non-public DNS results and redirects. Connect to a validated public IP while keeping the original hostname for certificate verification/SNI; do not resolve it a second time for the connection. Keep TLS verification on, ignore environment proxies, bound timeout, response size and the number of PDF links queued from each page. Do not bypass 403/bot protection.
- Preserve response bytes without content decoding and record URL, source code(s), timestamp, HTTP status, SHA-256, MIME type, retrieval outcome and legal verification state. Store only complete HTTP-200 HTML/PDF responses; reject unsupported encodings/content types and oversized/truncated responses. An HTML error/challenge page remains discovery-only, never parsed into a statutory value.
- Each retrieval creates an exclusive new staging directory, raw bytes and manifest; existing evidence is never overwritten. Failed attempts produce a sanitized manifest without a complete accepted body/hash; storage failures may leave only a quarantined `.part` file. Local staging is explicitly `LOCAL_STAGING`, not an immutable/WORM archive or accepted legal evidence. All manifests carry `verification_status=UNVERIFIED`, `activation_eligible=false`. No code in this slice activates a rule, fills a seed, emits a wage or claims the latest law. Acquisition runs in a killable child process with a 30-second parent timeout covering DNS, TLS, headers and body.
- Extract bounded same-allowlist PDF links from HTML for discovery; downloads require an explicit CLI flag. Link discovery neither validates legal content nor grants a new host permission. S3 GOVERNANCE/3650-day retention, database provenance, extraction, change review, signatures and A1–A8 remain subsequent integration work.
- Acceptance: offline tests demonstrate byte hashes, no overwrite, sanitized failure manifests, size/encoding/MIME limits, redirect/host/IP rejection and PDF discovery bounds; independent security review; parent-observed lint, strict types, full suite and a bounded real acquisition run. Network denial is recorded as a failed acquisition, never successful statutory verification.

Run from `backend/` using the existing environment:

```powershell
rtk proxy .\.venv\Scripts\python.exe -B -m app.statutory.collect_sources
rtk proxy .\.venv\Scripts\python.exe -B -m app.statutory.collect_sources --source sso
```

`--download-pdfs` additionally retrieves at most eight allowlisted PDF links per source, without recursive crawling. Exit 1 means at least one acquisition failed. A successful capture still means UNVERIFIED discovery only. The CLI has no activation command and is not a scheduled service.

### 2.2 Archival integration target

1. **Acquisition** — retrieve the document at the highest reachable level (§1.1). Record, for each artefact:
   - `source_url`, `retrieved_at` (ISO-8601 with timezone), `http_status`
   - `sha256` of the raw response bytes
   - `level` (L1–L4) and `mime_type`
2. **Archival** — write the raw artefact to the WORM object store (ADR-002, Ceph/S3 `GOVERNANCE` mode, 3650-day retention) under the immutable key prefix `statutory/{year}/{source_id}/{filename}`.
   - The object key MUST include the retrieval date; overwriting is prohibited by the bucket's Object Lock.
   - The `sha256` is recorded in `statutory_source_artefacts` and is referenced by every parameter row that derives from it.
3. **Provenance record** — one row per source artefact:

```
statutory_source_artefacts
  id                UUID PK
  rule_year_shamsi  INT  NOT NULL
  source_code       VARCHAR(16) NOT NULL      -- 'S1'..'S8'
  issuing_authority VARCHAR(200) NOT NULL
  document_title    VARCHAR(300) NOT NULL
  reference_number  VARCHAR(120)              -- e.g. 'Resolution No. 9234'
  reference_date_sh VARCHAR(20)               -- e.g. '1405/02/15'
  source_url        TEXT NOT NULL
  retrieval_level   CHAR(1) NOT NULL CHECK (retrieval_level IN ('L1','L2','L3','L4'))
  retrieved_at      TIMESTAMPTZ NOT NULL
  sha256            CHAR(64) NOT NULL
  s3_object_key     TEXT NOT NULL
  archived_by       UUID NOT NULL             -- FK users.id
```

4. **No silent overwrite.** A re-retrieval of the same source with a different `sha256` creates a *new* artefact row and raises a change-review task; it never mutates the existing row.

---

## 3. Parameter Transcription (1405 SH — PROPOSED, NOT ACTIVATED)

> **Status of this table: TRANSCRIBED, CROSS-CORROBORATED, NOT FOUR-EYES VERIFIED.**
> The values below are recorded here as the *candidate* rule set for 1405 SH. They are **not** written into `backend/data/seeds/statutory_rules_1405.yaml` (that file was not modified) and they are **not** loadable by the engine, whose loader must fail closed (§7.2).

### 3.1 Verified 1405 SH values

| Parameter | 1405 value (Rial) | Source | Level | Derivation | Verification |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `daily_minimum_wage_rial` | `5,541,850` | S1 wage circular, بند 1, session 1404/12/24 (2026-03-15) | L2 | Direct | Corroborated by S1 reproduction, S4 item 1, and 4 independent payroll sources |
| `monthly_minimum_wage_30days_rial` | `166,255,500` | S1 | L2 | `5,541,850 × 30` | Arithmetic |
| `monthly_minimum_wage_31days_rial` | `171,797,350` | S1 | L2 | `5,541,850 × 31` | Arithmetic |
| `monthly_housing_allowance_rial` | `30,000,000` | S2, Council of Ministers Resolution **No. 9234**, session 1405/02/06, issued 1405/02/15 (2026-05-05) | L2 | Direct | Full resolution text retrieved with number and date; corroborated by 5 sources |
| `monthly_grocery_allowance_rial` | `22,000,000` | S1 wage circular, بند 3 | L2 | Direct | Corroborated (unchanged from 1404) |
| `monthly_marriage_allowance_rial` | `5,000,000` | S1 wage circular, بند 4 | L2 | Direct | Corroborated (unchanged from 1404) |
| `child_allowance_per_child_rial` | `16,625,550` | Labour Law Art. 86 via S1 | L2 | `3 × 5,541,850` | Formula verified: reproduces the 1404 seed exactly (`3 × 3,463,656 = 10,390,968`) |
| `daily_seniority_base_rial` | `166,667` | S1 wage circular, بند 2 | L2 | Direct | Corroborated by S4 item 3 |
| `monthly_seniority_base_30days_rial` | `5,000,010` | S1 | L2 | `166,667 × 30` | Arithmetic |
| `max_daily_insurable_wage_rial` | `38,792,950` | S4 item 13 | L2 | `7 × 5,541,850` | Multiplier confirmed verbatim: *"حداکثر دستمزد روزانه مشمول کسر حق بیمه ... ۷ برابر حداقل دستمزد روزانه"* |
| `max_monthly_insurable_wage_29days_rial` | `1,124,995,550` | S4 item 13 | L2 | `38,792,950 × 29` | Arithmetic; S4 requires per-month-length application |
| `max_monthly_insurable_wage_30days_rial` | `1,163,788,500` | S4 item 13 | L2 | `38,792,950 × 30` | Arithmetic |
| `max_monthly_insurable_wage_31days_rial` | `1,202,581,450` | S4 item 13 | L2 | `38,792,950 × 31` | Arithmetic |
| `monthly_tax_exemption_rial` | `400,000,000` | S6 Budget Law 1405, Art. 84 ceiling | L2/L3 | Direct | Corroborated by 8 independent sources; annual equivalent `4,800,000,000` confirmed |
| `annual_tax_exemption_rial` | `4,800,000,000` | S6 | L2/L3 | Direct | Corroborated |
| `eydi_tax_exemption_rial` | `400,000,000` | S6 + S8 | L2 | `annual_exemption ÷ 12` | Formula; reproduces the 1404 seed (`2,880,000,000 ÷ 12 = 240,000,000`) |
| `non_cash_benefit_annual_tax_exemption_rial` | `800,000,000` | S6 + S7 (DTA Art. 91) | L2 | `annual_exemption × 2 ÷ 12` | Formula; reproduces the 1404 seed (`2,880,000,000 × 2 ÷ 12 = 480,000,000`) |
| `max_annual_eydi_rial` | `498,766,500` | S8 + S1 | L2 | `3 × 166,255,500` | Formula; reproduces the 1404 seed (`3 × 103,909,680 = 311,729,040`) |

### 3.2 1405 SH progressive salary income tax brackets

Source: S6 Budget Law 1405, ماده واحده. Rates and thresholds as published; monthly basis.

| Slab | Lower bound (Rial) | Upper bound (Rial) | Rate | Toman band (as published) |
| :-- | ---: | ---: | ---: | :--- |
| 1 | 0 | `400,000,000` | 0 % | کمتر از ۴۰ میلیون تومان — معاف |
| 2 | `400,000,001` | `800,000,000` | 10 % | مازاد بر ۴۰ تا ۸۰ میلیون تومان |
| 3 | `800,000,001` | `1,000,000,000` | 15 % | مازاد بر ۸۰ تا ۱۰۰ میلیون تومان |
| 4 | `1,000,000,001` | `1,200,000,000` | 20 % | مازاد بر ۱۰۰ تا ۱۲۰ میلیون تومان |
| 5 | `1,200,000,001` | `1,400,000,000` | 25 % | مازاد بر ۱۲۰ تا ۱۴۰ میلیون تومان |
| 6 | `1,400,000,001` | `null` | 30 % | مازاد بر ۱۴۰ میلیون تومان |

**Corroborating arithmetic published by sources:** a monthly taxable income of 80,000,000 Toman (800,000,000 Rial) yields exactly 4,000,000 Toman of tax, i.e. `40,000,000 exempt + 40,000,000 × 10 %`. Recomputed and confirmed.

### 3.3 Unchanged statutory constants (re-verified annually, not annual)

| Parameter | Value | Authority |
| :--- | ---: | :--- |
| `employee_sso_rate` | `0.07` | Social Security Law Art. 28 |
| `employer_sso_rate` | `0.20` | Social Security Law Art. 28 |
| `employer_unemployment_rate` | `0.03` | Unemployment Insurance Act |
| `sanavat_monthly_accrual_rate` | `0.0833333333` | Labour Law Art. 24 |
| `eydi_min_days` | `60` | 1370 Law |
| `eydi_max_days_min_wage` | `90` | 1370 Law |
| `article_137_deduction_policy` | `conservative_inta` | Default posture; toggle per `FIND-LEG-02` |

### 3.4 Wage-level uplift rule (1405, S1 بند 1)

> *"سایر سطوح مزدی" به میزان ۴۵ درصد مزد ثابت یا مزد مبنا (موضوع ماده ۳۶ قانون کار) به اضافه روزانه مبلغ ۵۱۹,۵۴۹ ریال نسبت به آخرین مزد در سال ۱۴۰۴ افزایش می‌یابد.*

```
daily_wage_1405 = (daily_wage_1404 × 1.45) + 519,549
```
A classified-workshop job wage or fixed wage **must not fall below `5,541,850` Rial/day**. This uplift function is required to project a candidate's 1404 package into the 1405 baseline.

### 3.5 Open items found during transcription

| # | Item | Status | Action |
| :-- | :--- | :--- | :--- |
| O1 | S4 item 4 states that if the Council of Ministers **raises** the housing allowance, SSO will issue a follow-up circular. The housing allowance **was** raised (9,000,000 → 30,000,000, Resolution 9234). | **UNRESOLVED** | Determine whether a supplementary SSO circular adjusts the insurance base for the housing allowance. Affects `mozd_e_mabna`. |
| O2 | The salary-tax band boundaries were obtained from one L2/L3 source with explicit figures plus 8 corroborating sources that confirm the exemption and the 0/10/15/20/25/30 rate ladder, but only one that prints the exact band edges. | **PARTIAL** | Four-eyes check the band table against the Budget Law PDF (S6). |
| O3 | Legal citation for the child allowance appears as *Labour Law Art. 86* in some sources and *Social Security Law Art. 86* in others. | **CONFLICTING** | Legal Counsel to confirm the correct instrument before activation. |
| O4 | The tax exemption is characterised by sources as *"ماده واحده قانون الزامات بودجه‌های سنواتی"* while the project corpus cites *"Band Z Tab 1"* of the Budget Law. | **AMBIGUOUS** | Align the citation string in `statutory_rule_set_versions` with the verified instrument reference. |
| O5 | Date of the SSO insurance-base circular (S4) was not captured from the retrieved reproduction. | **UNVERIFIED** | Capture from the PDF before archiving. |

### 3.6 Correction to `1.docx`

`1.docx` (Defect 1) states that the 1405 figure of `5,541,850 IRR/day` is *"lower than the 1404 ceiling (727.37M IRR/month), indicating a likely digit transposition or unverified source"*. That inference is **wrong**: it compares a **daily** wage against a **monthly** ceiling. Under the correct comparison, 1405's daily wage of 5,541,850 Rial is a **+60.0 %** increase over 1404's 3,463,656 Rial, and the 1405 monthly insurable ceiling (`1,163,788,500` Rial) is **+60.0 %** above 1404's (`727,367,760` Rial). The value 5,541,850 is **confirmed correct** by the S1 circular, the S4 SSO circular and multiple independent sources. `1.docx` remains a valid historical audit; this correction is recorded here and raised as DEC-001 evidence.

---

## 4. Independent Four-Eyes Verification

### 4.1 Protocol

1. **Transcriber (A)** enters each parameter into the staging rule set from the archived artefact, recording the exact source location (article / بند / table row).
2. **Verifier (B)** independently re-derives the value from the *same* archived artefact, without seeing A's entry, and signs the parameter row.
3. **A ≠ B in role and never the same person.** For legal-interpretation parameters (bracket semantics, exemption applicability, Article 137 scope) a third role — **Certified Tax Accountant** or **Labor Law Counsel** — signs.
4. A parameter is `VERIFIED` only when ≥2 independent signatures exist AND ≥1 of them is at role *Certified Tax Accountant* or *Labor Law Counsel*.
5. Signatures are cryptographic: `sha256(parameter_canonical_json ‖ verifier_id ‖ timestamp ‖ artefact_sha256)` appended to `statutory_parameter_signatures`. Signature rows are append-only.

### 4.2 Signature record

```
statutory_parameter_signatures
  id                  UUID PK
  rule_set_version_id UUID NOT NULL REFERENCES statutory_rule_set_versions(id)
  parameter_key       VARCHAR(120) NOT NULL
  parameter_value     NUMERIC(24,4) NOT NULL
  derivation_note     TEXT
  source_artefact_id  UUID NOT NULL REFERENCES statutory_source_artefacts(id)
  verifier_role       VARCHAR(40) NOT NULL   -- 'TRANSCRIBER'|'VERIFIER'|'CERTIFIED_ACCOUNTANT'|'LABOR_COUNSEL'
  verifier_id         UUID NOT NULL REFERENCES users(id)
  signature_sha256    CHAR(64) NOT NULL
  signed_at           TIMESTAMPTZ NOT NULL
  UNIQUE (rule_set_version_id, parameter_key, verifier_role)
```

### 4.3 Required verification roster for 1405

| Role | Responsibility | Count |
| :--- | :--- | :--- |
| Transcriber — Payroll Engineer | S1, S2, S4 transcription | 1 |
| Verifier — Senior Statutory Analyst | Independent re-derivation of S1, S2, S4 | 1 |
| Certified Tax Accountant | S6 exemption, band table, Art. 137, S7 | 1 |
| Labor Law Counsel | S3 child-allowance instrument (O3), S8 Eydi | 1 |

---

## 5. Effective Dates and Versioning

### 5.1 Rule set identity

A rule set is identified by `(rule_year_shamsi, revision)`. The canonical form is `YYYY.R` — e.g. `1405.1` for the first revision of 1405. The label `1405.1-VERIFIED` (used by the defective example in `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §5.1) is **not** a valid status string; see §5.3.

### 5.2 Columns

```
statutory_rule_set_versions
  id                    UUID PK
  rule_year_shamsi      INT  NOT NULL
  revision              INT  NOT NULL
  effective_from        DATE NOT NULL          -- 1405-01-01 for a year-opening set
  effective_to          DATE                  -- NULL while active
  supersedes_id         UUID REFERENCES statutory_rule_set_versions(id)
  status                VARCHAR(24) NOT NULL
        CHECK (status IN ('DRAFT','UNDER_REVIEW','VERIFIED','ACTIVE','RETIRED','REJECTED'))
  is_active             BOOLEAN NOT NULL DEFAULT FALSE
  source_manifest       JSONB NOT NULL         -- [{source_code, artefact_id, sha256}]
  parameter_snapshot    JSONB NOT NULL         -- the full parameter set as loaded
  verified_at           TIMESTAMPTZ
  verified_by           UUID REFERENCES users(id)
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
  UNIQUE (rule_year_shamsi, revision)
```

### 5.3 Status semantics — the `1405.1-VERIFIED` defect

`REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §5.1 publishes `"statutory_version": "1405.1-VERIFIED"` for a calculation that was in fact performed with **1404** parameters (the 1404 exemption of 240,000,000, the 1404 seniority base of 94,000/day and the 1404 Eydi cap of 311,729,040 all appear in the arithmetic). The published string conflates three independent facts:

- the **year** (`1405`),
- the **revision** (`1`), and
- the **verification state** (`VERIFIED`).

These must be separate, machine-checkable fields:

```
statutory_version: "1405.1"
rule_set_status:   "VERIFIED" | "DRAFT" | ...
is_verified:       true | false
```

The API must never emit a status token that the loader did not read from the database. A response whose `rule_set_status` is not `VERIFIED` **must** carry a machine-readable `warning` field; a response computed against a non-`ACTIVE` rule set must not be presented as a quotable offer.

### 5.4 Month-length variants

Every parameter set must carry all three calendar-month variants (29/30/31 days) for the monthly insurable ceiling, the monthly minimum wage and the monthly seniority base, or a `days_in_month` field sufficient to derive them at load time. The engine must never assume 30 days.

### 5.5 Change history and audit trail

- A rule set that has produced any stored simulation is **immutable**. Corrections create a new `revision` with `supersedes_id` set and `effective_from` advanced.
- A change-review record is written for every new revision:

```
statutory_rule_changes
  id                UUID PK
  rule_set_version_id UUID NOT NULL
  parameter_key     VARCHAR(120) NOT NULL
  old_value         NUMERIC(24,4)
  new_value         NUMERIC(24,4)
  legal_citation    TEXT NOT NULL
  effective_from    DATE NOT NULL
  change_reason     TEXT NOT NULL
  requested_by      UUID NOT NULL REFERENCES users(id)
  approved_by       UUID NOT NULL REFERENCES users(id)
  affected_simulation_count INT NOT NULL DEFAULT 0   -- snapshots relying on the old value
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

- `affected_simulation_count` is computed at approval time. Historical simulations are **never** recomputed; they continue to reference the rule set version that produced them. A change report is generated for the legal file.
- Every rule-set read during a calculation is written to the append-only audit ledger (`AUDIT_LOGS`) together with the `rule_set_version_id`.

---

## 6. Change History of the 1404 Rule Set

The 1404 rule set is **verified and must not be modified**. It is the historical regression testbed and the legal baseline for every pre-1405 simulation.

| Item | Value |
| :--- | :--- |
| Rule set id | `1404.1` |
| Status | `VERIFIED` → `ACTIVE` for pre-1405 simulations |
| Effective | 1404/01/01 – 1404/12/29 |
| Source | 335th High Council of Labor Wage Circular (approved 25 Esfand 1403) + 1404 Budget Law |
| Seed file | `backend/data/seeds/statutory_rules_1404.yaml` (`is_verified_and_active: true`) |
| Modification status in this workstream | **NOT MODIFIED** |

---

## 7. Activation Criteria

### 7.1 Mandatory conditions — all must hold

| # | Condition | Current status |
| :-- | :--- | :--- |
| A1 | Every parameter in the candidate set has ≥2 signatures, one from a Certified Tax Accountant or Labor Law Counsel | **NOT MET** |
| A2 | Every parameter traces to an archived artefact with a stored `sha256` | Partially met (artefacts not yet archived to WORM) |
| A3 | At least one **L1** primary PDF has been retrieved and archived per source family | **NOT MET** — `mcls.gov.ir`, `tamin.ir`, `intamedia.ir` unreachable from this environment |
| A4 | Open items O1–O5 are closed | **NOT MET** |
| A5 | Regression suite passes against the 1404 reference vectors with 0 Rial deviation | Pending (Phase 1) |
| A6 | Certified Tax Accountant has approved the golden vector corpus for 1405 | **NOT MET** |
| A7 | Rule set status moved `DRAFT → UNDER_REVIEW → VERIFIED` with dual approval | **NOT MET** |
| A8 | Rule set is loaded into `statutory_rule_set_versions` and set `ACTIVE` for 1405 | **NOT MET** |

### 7.2 Fail-closed loader behaviour

Until A1–A8 are satisfied, the engine MUST:

- refuse to load `statutory_rules_1405.yaml` (all values `null`, `is_verified_and_active: false`);
- raise `StatutoryParameterUnavailable` rather than coercing `null` to `0`;
- **never** silently fall back to 1404 values while labelling the result `1405`;
- return `rule_set_status: "DRAFT"` and a machine-readable `warning` on any response that is computed from a non-`ACTIVE` set.

> `1.docx` line 470: *"Launching in Aban 1405 with 1404 rates invalidates live hiring recommendations."* The fail-closed rule is the direct technical control for that legal exposure.

### 7.3 Interim baseline (requires explicit approval — DEC-001)

Until 1405 is activated, the only lawful option is to run the engine on **1404** and label every output `statutory_version: "1404.1"`, `rule_set_status: "VERIFIED"`, with the disclosure that the offer is benchmarked to the 1404 statutory year. This is **legally conservative and transparent**, unlike labelling 1404 output as 1405.

---

## 8. Regression Testing Against the 1404 Dataset

### 8.1 Invariants

The 1404 rule set is the reference implementation. On every rule-set load and on every CI run:

| ID | Invariant |
| :-- | :--- |
| R-01 | `max_monthly_insurable_wage_30days_rial == 7 × daily_minimum_wage_rial × 30` for every year |
| R-02 | `monthly_tax_exemption_rial == annual_tax_exemption_rial ÷ 12` |
| R-03 | `eydi_tax_exemption_rial == annual_tax_exemption_rial ÷ 12` |
| R-04 | `non_cash_benefit_annual_tax_exemption_rial == annual_tax_exemption_rial × 2 ÷ 12` |
| R-05 | `child_allowance_per_child_rial == 3 × daily_minimum_wage_rial` (Labour Law Art. 86) |
| R-06 | `max_annual_eydi_rial == 3 × monthly_minimum_wage_30days_rial` |
| R-07 | `monthly_minimum_wage_31days_rial ÷ monthly_minimum_wage_30days_rial == 31/30` exactly |
| R-08 | `sanavat_monthly_accrual_rate == 1/12` |
| R-09 | Tax slab boundaries are contiguous and strictly increasing; slab 1 upper bound equals `monthly_tax_exemption_rial` |
| R-10 | The 1404 seed file's byte content is unchanged from its committed state (hash-pinned in CI) |

### 8.2 Golden vectors

A versioned, rule-year-keyed corpus of certified-accountant-approved input → output pairs. **This corpus does not yet exist** — it is `P1-T15`, status `BLOCKED`, owner Certified Tax Accountant, and it is the hard gate on Phase 1.

### 8.3 Activation-time regression procedure

1. Load candidate 1405 and reference 1404 into the same engine.
2. Execute the **identical** 1404 reference vector set against both; the 1405 run must differ only where a statutory parameter changed — every differing line must be attributable to a named parameter delta.
3. Execute the **1405** vector set (once certified) against 1405; 0 Rial deviation required.
4. Execute the property-based suite over the joint input space; the inverse property (gross→net→gross) must hold within 1 Rial.
5. Emit a machine-readable diff report listing each parameter delta, its legal citation, and the set of 1404 vectors whose output changed.

---

## 9. Related Tasks

| Task | Phase | Title | Status |
| :--- | :--- | :--- | :--- |
| `P1-T01` | 1 | Statutory rule set loader (versioned, fail-closed) | NOT_STARTED |
| `P1-T02` | 1 | 1405 four-eyes verification against primary PDFs | **BLOCKED** (external; L1 unreachable) |
| `P1-T03` | 1 | 1405 activation + 1404 regression | NOT_STARTED |
| `P1-T15` | 1 | Golden vector corpus (certified tax accountant) | **BLOCKED** (external) |
| `P1-T20` | 1 | Correct §5.1 worked example and API documentation | NOT_STARTED |

---

## 10. Verification Log Template

```
statutory_verification_log
  id                  UUID PK
  rule_year_shamsi    INT NOT NULL
  parameter_key       VARCHAR(120) NOT NULL
  proposed_value      NUMERIC(24,4) NOT NULL
  proposed_source     TEXT NOT NULL
  transcription_level CHAR(1) NOT NULL
  transcriber_id      UUID NOT NULL
  transcribed_at      TIMESTAMPTZ NOT NULL
  verifier_id         UUID NOT NULL
  verifier_role       VARCHAR(40) NOT NULL
  verified_at         TIMESTAMPTZ NOT NULL
  outcome             VARCHAR(16) NOT NULL  -- 'AGREE'|'DISAGREE'|'CANNOT_VERIFY'
  discrepancy_note    TEXT
  artefact_sha256     CHAR(64) NOT NULL
```
