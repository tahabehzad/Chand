# Specification: Document Intelligence & Employee Intelligence

- **Document ID:** `SPEC-DOC-001`
- **Status:** Draft — proposed specification
- **Author:** Documentation Engineering (Forensics workstream)
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](../EXECUTION_PLAN.md) §9 · [`docs/adr/ADR-005-async-execution-strategy.md`](../adr/ADR-005-async-execution-strategy.md) · [`docs/specs/TESTING.md`](TESTING.md) §10 · `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` Module 3, Module 4

> **Provenance.** The substantive content of this specification was harvested from `RESEARCH_GAP_ANALYSIS_AND_ADVANCED_SPECIFICATION.md` Deliverables 2 and 3. Those deliverables were **not** among the sections superseded by the red-team audit — the historical banner on that file names only Celery/Redis architecture, Next.js, and 1404 SH temporal assumptions. The material below is therefore **retained**, while every technology rejected by ADR-002/003/004 (MinIO COMPLIANCE mode, `pgcrypto` for PII, MCDA endpoints) has been **excluded**. See `docs/DOCUMENTATION_INDEX.md` for the full section-level supersession matrix.

---

## 1. Scope

### 1.1 In scope

Document ingestion and custody · Persian OCR and field extraction · tamper detection · official-issuer verification · cryptographic signature verification · cross-document consistency · the 4-way experience disambiguation · the evidence credibility score.

### 1.2 Out of scope

Candidate-facing portals (ADR-004) · biometric attendance · direct *Sabt-e Ahval* API access (legally unavailable to private employers) · automated final determination of fraud (anomaly detection routes to a human; it never concludes) · general-ledger accounting.

---

## 2. Document Taxonomy

### 2.1 The twelve primary categories

| # | Category (fa / en) | Issuing authority | Primary fields extracted |
| :--: | :--- | :--- | :--- |
| 1 | کارت هوشمند ملی — National Identity Card | Civil Registration (ثبت احوال) | National Code, birth date, serial number, validity expiry |
| 2 | شناسنامه — Identity Certificate | Civil Registration | Shenasnameh no., series, spouse details, child count & birth dates (Art. 86 / Ta'ahol) |
| 3 | سوابق بیمه تامین اجتماعی — Social Security History | Social Security Organisation | 8-digit insurance no., 10-digit workshop codes, start/end dates, total insured days, base wage |
| 4 | دانشنامه و گواهی موقت تحصیلی — Higher Education Degree | MSRT (سامانه سجاد) | Degree level, major, university, date, 20-digit health code (کد صحت), QR |
| 5 | دانشنامه دانشگاه آزاد — Azad University Degree | Islamic Azad University Central Organisation | Degree level, major, campus, issue date, diploma serial, verification tracking ID |
| 6 | گواهینامه فنی‌حرفه‌ای — Technical & Vocational Certificate | Iran Technical & Vocational Training Organisation (TVTO) | Skill title, standard occupation code, level, certificate ID, issue date |
| 7 | دیپلم متوسطه — Secondary Education Diploma | Ministry of Education | Branch/major, GPA, issue date, national student ID, verification serial |
| 8 | گواهی اشتغال به کار قبلی — Previous Employment Letter | Previous employer (legal entity, on letterhead) | Employer national ID, workshop code, exact start/end dates, job title, exit reason |
| 9 | فیش حقوقی و فیش واریز — Pay Slips & Bank Statements | Employer payroll / Iranian banking network (Shetab, پایا, ساتنا) | Gross/base wage, deductions, transfer reference (رهگیری), Sheba (IR-IBAN) |
| 10 | برگه تسویه‌حساب و اقرارنامه — Final Settlement & Release | Employer and employee, signed / fingerprinted | Itemised severance, unused leave pay, prorated Eydi, signed waiver, deposit slip |
| 11 | کارت پایان خدمت / معافیت — Military Service Exemption | Police Public Conscription Organisation (ناجا) | Service status (exempt / completed / امریه), issue date, reason (medical, دانش‌بنیان) |
| 12 | گواهی عدم سوء پیشینه — Criminal Background Clearance | Judiciary electronic services (سامانه ثنا / adliran) | Clearance status, issue date, validity expiry, unique judicial tracking code |

### 2.2 Additional categories for workplace valuation

| Category | Purpose |
| :--- | :--- |
| روزنامه رسمی — Commercial Gazette Registry (`rrk.ir`) | Proves the legal existence of a previous employer, registered capital, board, authorised signatories |
| پروانه اشتغال و عضویت نظام مهندسی / نظام صنفی رایانه‌ای — Professional guild licences | Certified technical level |
| گواهی نخبگی / امریه دانش‌بنیان — Knowledge-Based enterprise certificates | Official *Amriyeh* status, which affects statutory wage floors under the Vice-Presidency of Science |

---

## 3. Custody and Ingestion

### 3.1 Upload pipeline

```
1. RECEIVE   — MIME magic-byte validation (not the client-declared type); size limit 50 MB
2. HASH      — SHA-256 of the raw bytes, computed on the server
3. QUARANTINE— stored to a temporary, non-archived bucket
4. ARCHIVE   — stored to the WORM bucket under tenants/{tenant_id}/documents/{document_id}/,
               with Object Lock GOVERNANCE, 3650-day retention (ADR-002)
5. RECORD    — a DOCUMENTS row with the hash, the key, the version ID and the metadata
6. ENQUEUE   — a document-verification job (ADR-005, proposed)
```

**Ordering rule:** the file is hashed **before** any transformation. The hash is of the bytes as received. Every downstream artifact records the hash of its input, so the forensic chain from the original file to the extracted field is reconstructable.

### 3.2 Duplicate detection

The same document uploaded twice must not create two forensic trails. The tenant-scoped unique index on `(tenant_id, file_sha256_hash)` prevents it; the API returns the existing document with `200` rather than creating a duplicate.

### 3.3 Storage model

```
documents
  id                UUID PK
  tenant_id         UUID NOT NULL
  candidate_id      UUID NOT NULL
  document_category VARCHAR(50) NOT NULL
  original_file_name VARCHAR(255) NOT NULL
  mime_type         VARCHAR(100) NOT NULL
  file_size_bytes   INTEGER NOT NULL
  file_sha256_hash  CHAR(64) NOT NULL
  s3_object_key     TEXT NOT NULL
  s3_version_id     TEXT
  verification_status VARCHAR(40) NOT NULL DEFAULT 'UNVERIFIED_SELF_REPORTED'
  verification_method VARCHAR(50)
  official_tracking_code VARCHAR(100)
  issuer_inquiry_payload JSONB
  uploaded_by       UUID NOT NULL REFERENCES users(id)
  uploaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
  expires_at        TIMESTAMPTZ
  UNIQUE (tenant_id, file_sha256_hash)

forensic_audit_artifacts
  id                UUID PK
  document_id       UUID NOT NULL REFERENCES documents(id)
  tenant_id         UUID NOT NULL
  analysis_version  VARCHAR(40) NOT NULL        -- code + model version
  ocr_extracted_tables JSONB
  extracted_fields  JSONB NOT NULL
  signature_result  JSONB
  ela_tamper_score  NUMERIC(5,2)
  metadata_findings JSONB
  anomaly_flags     TEXT[]
  engine_version    CHAR(40) NOT NULL
  input_sha256      CHAR(64) NOT NULL
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
  UNIQUE (document_id, analysis_version)       -- a retry overwrites, never duplicates
```

The `UNIQUE (document_id, analysis_version)` constraint is what makes the job pipeline idempotent under retry (ADR-005, proposed).

---

## 4. Persian OCR & Extraction

### 4.1 Engine selection

**PaddleOCR with PP-Structure, self-hosted.** Selected for Persian table structure recognition (SLANet + DBNet), Persian character accuracy, on-premise deployment (no external SaaS leakage of candidate documents), and zero marginal cost per page.

### 4.2 Latency budget — realistic, not aspirational

| Environment | Budget per page | Source |
| :--- | :--: | :--- |
| 4 vCPU (no GPU) | **3.5 s – 6.0 s** | `FIND-ARCH-05` |
| NVIDIA T4 | **1.2 s – 1.8 s** | `FIND-ARCH-05` |
| Single page on a modern laptop CPU | ~8 s | Planning estimate |

> The commonly quoted "450 ms GPU / 1.8 s CPU" figure from the technology survey is **not** applicable to complex Persian insurance micro-tables. The red-team audit corrected this (`FIND-ARCH-05`). The capacity model must use the corrected budget.

**Capacity formula:** pages/second = `concurrency ÷ seconds_per_page`. On a 4 vCPU host with 2 concurrent worker processes, sustained throughput is roughly **0.4 pages/second**. A 500-page corpus takes ~21 minutes — which is why the corpus acquisition (below) is a long-lead item.

### 4.3 Persian-specific extraction challenges

| Challenge | Handling |
| :--- | :--- |
| RTL cursive shapes (initial/medial/final/isolated) | PaddleOCR's recogniser is trained on Persian cursive; a dedicated `lang="fa"` model is required |
| ZWNJ (نیم‌فاصله) | Splitting errors are a known weakness of the alternative engine (Tesseract); the Persian PaddleOCR model handles them well. Validate on a ZWNJ corpus |
| Persian `ک`/`ی` vs Arabic `ك`/`ي` | Normalise after extraction to the Persian forms (U+06A9, U+06CC) before storage, so downstream matching is stable |
| Persian numerals in tables | The OCR output frequently yields Arabic-Indic (U+0660–0669) or Persian (U+06F0–06F9) digits. **Normalise to ASCII in the machine layer** — the same three-layer numeral policy as the frontend (`SPEC-FE-001` §4.1) |
| Dense multi-column tables | PP-Structure table model; a field-level post-processor per document category |
| Handwriting, wrinkles, phone-camera capture | Lower accuracy expected; the pipeline reports a confidence, and low confidence routes to human review rather than to an assertion |

### 4.4 The 8 forensic fields of a Social Security slip

| Field | Persian | Notes |
| :--- | :--- | :--- |
| National Code | کد ملی | Must pass the modulo-11 check before it is stored |
| Branch code | کد شعبه | — |
| Employer workshop ID | کد کارگاه | 10 digits; links to the workshop registry |
| Title / occupation code | عنوان شغل / کد شغل | Reconciles against ISCO-08 and the workshop classification plan |
| Insurable days per month | روزهای بیمه‌پردازی | The primary input to the 4-way experience disambiguation |
| Insurable base wage | دستمزد مبنای حق بیمه | Cross-checks against the declared wage |
| Total cumulative history | سابقه کل | The insured-days total |
| Premium paid | حق بیمه پرداختی | A lower bound on the actual wage — used as an under-reporting detector |

### 4.5 Accuracy claim — correction

The technology survey reports "94.8 % – 98.2 %" Persian character accuracy for PaddleOCR. `PHASE_1_RED_TEAM_AUDIT.md` List 3 records that this applies **only to clean, high-resolution PDFs** and that real-world field accuracy on wrinkled, low-contrast or phone-captured Iranian insurance slips remains **[UNVERIFIED — Requires Enterprise Pilot Dataset]**.

**The acceptance criterion for this module is therefore field-extraction accuracy > 95 % on the authentic corpus, measured — never the character-accuracy figure.**

---

## 5. Tamper Detection

### 5.1 PDF structural forensics

| Technique | Detection | Tool |
| :--- | :--- | :--- |
| Incremental-update parsing | A legitimate PDF has one revision tree; a tampered PDF usually has several, with earlier numeric content occluded by later stream objects. The `/Prev` offset chain is walked and every revision inspected | `pikepdf` |
| Font-subset consistency | Official PDFs embed consistent subsets (`IRANSans*`, `BNazanin*`, `Vazirmatn*`). A tampered document often introduces an un-embedded system font, a `/ToUnicode` CMap mismatch, or a different font descriptor | `pikepdf` |
| Producer metadata | A `/Producer` of `Canva`, `iLovePDF`, `Adobe Photoshop` on an alleged government-issued document is an immediate flag | `pikepdf` |
| Timestamp consistency | A gap or inversion between `/CreationDate` and `/ModDate`, or dates after the upload date, is a flag | `pikepdf` |

### 5.2 Image forensics

**Error Level Analysis.** JPEG quantises each 8×8 block. A region that was pasted or modified and re-saved exhibits a different compression error level. The image is re-saved at a fixed quality (90) and the absolute difference map is computed:

```
ELA(x, y) = | I_original(x, y) − I_resaved(x, y) | × ScaleFactor
```

**Copy-move detection.** ORB/SIFT keypoints detect duplicated decorative elements, cloned official stamps or duplicated signature patterns across the canvas.

**Limitation to state in the UI:** ELA and clone detection are **screening heuristics**, not proof. A false-positive rate of ≤ 5 % is the target. The pipeline must present a score and a flag, never a verdict. `RESEARCH_GAP` §2.3 is explicit: *"AI-based anomaly detection never issues a definitive verdict of fraud; it merely adjusts the status and routes the item for human adjudication."*

---

## 6. Digital Signature Verification

| Element | Specification |
| :--- | :--- |
| Tooling | **pyHanko** + `cryptography` |
| Trust anchor | A **local** trust store containing the Iranian National Root CA (the E-Commerce Development Center) and the governmental intermediate CAs (GICA) |
| What is inspected | `/ByteRange`, `/Contents` and `/Cert` — whether the signed byte range is intact (no post-signing modification) |
| Standards | PAdES / ISO 32000-1, ETSI TS 102 778 |
| Revocation | **Local offline CRL cache with a 24-hour expiry.** Public-sector OCSP availability is unreliable, and a network timeout must not fail a verification that should succeed (`FIND-ARCH-06`) |
| Result | Stored in `forensic_audit_artifacts.signature_result` |
| Failure behaviour | An **unavailable** revocation check is reported as `REVOCATION_UNKNOWN`, **not** as a failure. An unavailable check must never silently pass as valid |

**Dependency on the pilot environment:** the Iranian PKI trust store must be assembled and reviewed during Phase 2; it is not a build-time download.

---

## 7. Official Issuer Verification

### 7.1 Real-world access modes

| Authority | Channel | Access mode | Payload |
| :--- | :--- | :--- | :--- |
| Social Security Organisation | `eservices.tamin.ir` | **User-initiated**; the candidate generates the official report and provides the inquiry token | National Code + tracking code |
| MSRT (Sajjad) | `estelam.msrt.ir` / `portal.saorg.ir` | Public web inquiry + QR | 20-digit health code (کد صحت) or National Code + health code |
| Islamic Azad University | `estelam.iau.ir` | Public web inquiry + dynamic QR | Diploma serial + National Code + tracking ID |
| TVTO | `portaltvto.com` | Public inquiry | National Code + certificate ID |
| Judiciary (Sana) | `adliran.ir` | Authenticated web portal | 16-digit judicial tracking code + National Code |
| Official Gazette / Companies | `rrk.ir`, `ilenc.ssaa.ir` | Open web search + CAPTCHA | 11-digit legal-entity ID |

### 7.2 The Shahkar reality check

| Fact | Consequence |
| :--- | :--- |
| Direct *Sabt-e Ahval* API access is restricted to government ministries, banks and major financial institutions on the National Information Network via the Government Service Gateway. **Private employers and SaaS platforms cannot obtain it.** | No "verify against the civil registry" feature may be advertised or implemented |
| Shahkar validates only whether a National Code matches a mobile-number subscriber. It returns a **boolean only** — no name, no father's name, no birth date, no photo | The data model must not expect more |
| Shahkar access for legal entities is via PGSB/SITAD or a licensed third-party aggregator (UID, Vandar, Zibal, ApiEco) | Access requires a commercial agreement — an external dependency, on the critical path for the identity module |

### 7.3 Shahkar must be interactive — never background (`FIND-ARCH-07`)

The Communications Regulatory Authority's Shahkar rules require **interactive SMS OTP consent from the subscriber**. Automated background verification is both prohibited and technically impossible.

**The only permitted flow:**

```
HR operator → POST /api/v1/identity/shahkar/request-otp { candidate_id }
            → system sends an official SMS OTP to the candidate
            → candidate reads the OTP to the HR operator (interview / intake)
            → HR operator enters it → POST /api/v1/identity/shahkar/verify-otp
            → the operator must act within 120 seconds
            → result stored against a consent record
```

A consent record is created (`CANDIDATE_CONSENT_RECORDS`) with the purpose, the client IP, the OTP verification reference and the timestamp. The identity check is **never** performed without a recorded consent.

**AUTO mode must not exist.** If a product requirement ever asks for background Shahkar verification, it is a compliance violation and must be refused.

### 7.4 Deterministic validation before any external call

| Check | Algorithm |
| :--- | :--- |
| National Code (10 digits) | `Check = Σ dᵢ × (11 − i) mod 11`; `d₁₀ = Check` if `Check < 2`, else `11 − Check`. Repeated-digit sequences (`0000000000`) are rejected |
| Legal-entity ID (11 digits) | The Iranian corporate weighted modulo-11 algorithm |
| Bank Sheba | IRAN format check: `IR` + 24 digits with the `62` prefix and the modulo-97 check digits |

These run client-side **and** server-side. A failure short-circuits before any external call, saving cost and avoiding pointless PII transmission.

---

## 8. Verification Status Model

| Status | Weight | Evidence requirement |
| :--- | ---: | :--- |
| `VERIFIED_OFFICIAL_ISSUER` | 1.00 | Validated directly against an official portal with a valid tracking code or a verified official digital signature |
| `DIGITALLY_VERIFIED` | 0.95 | Cryptographically valid PAdES signature from an authorised Iranian CA; intact byte range; valid timestamp |
| `MANUALLY_REVIEWED` | 0.85 | An authorised HR manager or legal auditor inspected the original and signed off |
| `CROSS_CHECKED_CONSISTENT` | 0.80 | Corroborated across independent secondary documents (e.g. employment-letter dates match the Tamin workshop record) |
| `UNVERIFIED_SELF_REPORTED` | 0.30 | No tracking code, no signature, no corroboration. Indicative only |
| `EXPIRED` | 0.20 | Previously authentic but past its validity window (expired inquiry code, lapsed licence) |
| `INVESTIGATION_REQUIRED` | 0.00 | Anomaly triggered: metadata mismatch, ELA divergence, date overlap across two full-time workshops, or a checksum failure |
| `REJECTED_FRAULENT` | −1.00 | Definitively invalid, counterfeit or forged, following **formal human review and issuer refutation** |

**Status transitions are append-only.** Each transition is a row with the actor, the timestamp, the reason and the evidence reference. A status is never overwritten.

---

## 9. Cross-Document Consistency Matrix

| Primary document | Cross-check | Rule |
| :--- | :--- | :--- |
| National ID card | All other documents | Strict exact match of the National Code, first name, last name and birth date |
| Shenasnameh | Benefit claims (Art. 86 / Ta'ahol) | The registered count of children under 18 and the official marital status must match |
| Tamin insurance record | Previous employment letters | Workshop code and employment dates must match the Tamin branch history |
| Tamin insurance record | Claimed occupational experience | Insured contribution days must match, or the gap must be explained |
| Previous pay slip | Tamin insurable wage history | The base wage on the slip must align with the declared wage in Tamin |
| Higher-education degree | Resume / claims | The graduation date must precede or align with the professional roles claimed |
| Previous employment letter | Official Gazette (`rrk.ir`) | The issuing company must have been legally registered and active during the claimed employment |
| Bank transfer slip | Final settlement | The settlement net must match the transferred amount in the Sheba record |

**Two-workshop overlap detection.** Two full-time workshop records covering the same calendar period is a strong indicator of double employment and must raise `INVESTIGATION_REQUIRED`.

**Under-reporting detection.** Where the declared wage in a candidate's claim materially exceeds the insurable base wage in the Tamin record, the platform should surface the statutory consequence: the employer must contribute on the actual wage, and the difference becomes an employer cost and a social-security exposure. This is presented as information for the hiring decision — **never** as legal advice.

---

## 10. Employee Intelligence — 4-Way Experience Disambiguation

### 10.1 The four orthogonal dimensions

| # | Dimension | Persian | Statutory role | Primary evidence |
| :--: | :--- | :--- | :--- | :--- |
| E1 | Total professional experience (`E_total`) | سابقه کار حرفه‌ای کل | Market benchmark bracket | CV, portfolio, references |
| E2 | Social Security insurance history (`E_sso`) | سابقه پرداخت حق بیمه | **Statutory eligibility trigger** — Art. 86 child allowance requires ≥ 720 insured days | Official SSO history |
| E3 | Seniority with the current employer (`S_current`) | سابقه کار در کارگاه فعلی | Severance accrual (Art. 24); leave rollover (Art. 66) | Employment contract, payroll log |
| E4 | Legally recognised base seniority (`S_legal`) | سابقه مشمول مزد سنوات | The mandatory daily base seniority increment (پایه سنوات) | Job classification plan, workshop tenure |

**Conflating these is the primary source of financial distortion.** A candidate may have 10 years of total experience, 3 years of insurance, 1 year at the current firm, and 0 years of legally recognised base seniority.

### 10.2 The statutory consequences that make disambiguation mandatory

1. **Art. 86 child allowance is gated.** The employer is **legally prohibited** from paying the child allowance unless the worker has accumulated **at least 720 days (24 months)** of verified SSO contributions across their working life. Conflating E1 with E2 causes either an unlawful denial or an unlawful payment. The engine must therefore evaluate the allowance against `E_sso`, not against `E_total`.
2. **Severance does not carry over.** Art. 24 severance is 1 month of the final base wage per full year of continuous service **with this employer**. Previous service does not transfer.
3. **Base seniority depends on the workshop classification.**
   - **Unclassified workshops** (فاقد طرح طبقه‌بندی مشاغل): base seniority is earned **only after 365 days of continuous service with the same employer**. Prior service does not transfer. Treating a hire's 10 years of prior experience as legal base seniority inflates the statutory payroll by millions of Toman.
   - **Classified workshops** (دارای طرح طبقه‌بندی مشاغل مصوب، Arts. 48–49): prior relevant experience is evaluated under the Ministry of Labour's Job Classification Executive Regulations and mapped to job grades and step increments.

### 10.3 Zero-double-counting architecture

```
LAYER 1 — DETERMINISTIC STATUTORY FLOOR
  · Minimum base wage + mandatory allowances (مسکن، بن، تاهل)
  · Art. 86 child allowance gated strictly by E_sso ≥ 720 days
  · Legal base seniority computed strictly from S_legal (workshop rules)
                      │
                      ▼
LAYER 2 — MARKET COMPETENCY VALUATION
  · E_rel = min(E_total_occupational, 16.0)
  · M_exp = 1.0 + α · ln(1.0 + β · E_rel),  α = 0.18, β = 0.40
  · Bounded to [1.00, 1.35]; at E_rel = 16 the multiplier reaches 1.364
  · Zero dependence on E_sso or S_current — strictly orthogonal to Layer 1
                      │
                      ▼
LAYER 3 — EVIDENCE CREDIBILITY MODULATION
  · V_score ∈ [0.30, 1.00]
  · Unverified claims NEVER inflate the median (P50)
  · A low V_score widens the uncertainty band (P25–P75 dispersion)
    and pulls the recommendation toward the conservative lower quartile
```

The earlier baseline research applied a seniority-tier boost, an additive logarithmic multiplier **and** an insurance-based bump simultaneously, which multiplied a 10-year candidate's salary by over 180 %. The three-layer orthogonal model exists to prevent exactly that.

---

## 11. Evidence Credibility Score

```
V_score = Σₖ  wₖ · StatusWeight(dₖ) · Completeness(dₖ)
```

| Component | Definition |
| :--- | :--- |
| `wₖ` | The statistical weight of the document category (a Tamin slip outweighs a self-reported CV) |
| `StatusWeight(dₖ)` | The verification-status weight from §8 |
| `Completeness(dₖ)` | The proportion of the category's expected fields successfully extracted and validated |

**Zero optimistic imputation.** A missing document is **not** treated as a neutral claim. It lowers `V_score` and widens the band. It is never replaced by a population average or a favourable assumption. `RESEARCH_GAP` §3.3: *"principled handling of missing data (zero optimistic imputation)"*.

**Where V_score is used.** It modulates the **uncertainty band and the recommendation**, never the statutory floor. A candidate with a weak evidence base may still be hired; the platform simply presents a wider band and a lower-confidence recommendation.

---

## 12. Title Discrepancy Resolution (`FIND-PROD-03`)

When a candidate's claimed title ("Lead Architect") conflicts with the official insurance title ("کارگر فنی"), the platform must **not** treat this as fraud and must not silently reject the candidate.

**Required flow:**

1. Flag the discrepancy and present both titles.
2. Prompt the hiring team to record a **structured commercial justification** — a controlled vocabulary of reasons (e.g. *"standard tech-sector insurance premium optimisation"*, *"workshop classification pending"*, *"title inflation on the CV"*).
3. Store the justification with the actor, the timestamp and the timestamp of the source documents.
4. The justification is part of the audit trail and appears in the evidentiary dossier.

The rationale: the insurance title is a legal classification for premium purposes; it is frequently narrower than the market title. Rejecting on that basis produces false fraud rejections and systematic discrimination against candidates whose prior employers classified their roles conservatively.

---

## 13. End-to-End Document Workflow

```
1. Secure upload (PDF / image)          → hash, MIME validation, WORM archival
2. Structural PDF & metadata forensics   → pikepdf revision tree, fonts, producer, timestamps
3. OCR & layout extraction               → PaddleOCR PP-Structure (Persian)
4. Entity extraction                     → per-category field extractor + validation
5. Image forensics                       → ELA + clone detection (raster only)
6. Signature verification                → pyHanko, local trust store, offline CRL cache
7. Official issuer verification          → candidate-initiated token flow
8. Cross-document consistency            → the matrix in §9
9. Status assignment & weighting         → §8, §11
10. Human adjudication (if flagged)      → queued for LEGAL_REVIEWER
11. Audit ledger                         → append-only, hash-chained, with actor and rule version
```

Steps 2–6 are CPU-bound and run in the **worker process**, never in the request path (`ADR-005`, proposed).

---

## 14. Acceptance Criteria

| ID | Criterion | Gate |
| :-- | :--- | :-- |
| DF-01 | Field extraction accuracy **> 95 %** on 500 authentic Social Security slips | **Phase 2 gate (blocking)** |
| DF-02 | Per-field accuracy ≥ 90 % on the 8 forensic fields | Phase 2 |
| DF-03 | Document category classification ≥ 95 % | Phase 2 |
| DF-04 | False-positive tamper flag rate ≤ 5 % on an untampered corpus | Phase 2 |
| DF-05 | True-positive detection ≥ 90 % on the deliberately tampered corpus | Phase 2 |
| DF-06 | OCR latency within the `FIND-ARCH-05` budget for the deployed hardware | Reported |
| DF-07 | Every forensic artifact records the input hash, the engine version and the model version | Blocking |
| DF-08 | A retry of the same job never duplicates an artifact | Blocking |
| DF-09 | Verification status transitions are append-only and actor-attributed | Blocking |
| DF-10 | Shahkar verification is impossible without a consent record, and no automated path exists | Blocking |
| DF-11 | The revocation-unavailable case is reported as `REVOCATION_UNKNOWN`, never as valid | Blocking |
| DF-12 | A title discrepancy never causes an automatic rejection | Blocking |
| DF-13 | The Art. 86 child allowance is refused when `E_sso < 720` days | Blocking |

> **DF-01 depends on an external corpus that does not yet exist** (`P2-T16`, BLOCKED). No synthetic corpus may be used to satisfy it. The red-team audit records the underlying accuracy claim as **[UNVERIFIED]**.

---

## 15. Open Decisions

| ID | Question | Recommendation | Approver | Status |
| :-- | :--- | :--- | :-- | :-- |
| DEC-011 | What are the acceptance criteria for Module 3 / document intelligence? | Adopt §14 verbatim, with the corpus acquisition as a separate blocking task | Product Manager + QA Lead | OPEN |
| DEC-011a | Which Shahkar aggregator (PGSB/SITAD direct, or a licensed third party)? | PGSB/SITAD direct if the commercial terms are obtainable; otherwise a licensed aggregator. The choice depends on an agreement that must be in place before Phase 2 completes | Legal Counsel + Procurement | OPEN |
| DEC-011b | Who performs the human adjudication of flagged documents? | `LEGAL_REVIEWER` (a new role from `SPEC-AUTH-001` §3), with `HR_MANAGER` explicitly excluded | Product Manager + CISO | OPEN |
| DEC-011c | Is the 720-day Art. 86 threshold verified against the SSO's own determination? | Verify with a written SSO ruling before relying on it as a hard gate | Labor Law Counsel | OPEN |

---

## 16. Related Tasks

| Task | Phase | Title | Status |
| :--- | :--- | :--- | :--- |
| `P2-T01` | 2 | Document taxonomy, storage model and custody design | NOT_STARTED |
| `P2-T02` | 2 | Upload endpoint, MIME magic validation, SHA-256 | NOT_STARTED |
| `P2-T03` | 2 | Ceph/S3 integration (boto3, GOVERNANCE Object Lock) | NOT_STARTED |
| `P2-T04` | 2 | Async execution strategy (ADR-005) and job pipeline | **BLOCKED** (ADR-005 Proposed) |
| `P2-T05` | 2 | PaddleOCR PP-Structure Persian pipeline and model provisioning | NOT_STARTED |
| `P2-T06` | 2 | Per-category field extraction and validation | NOT_STARTED |
| `P2-T07` | 2 | PDF structural forensics (pikepdf) | NOT_STARTED |
| `P2-T08` | 2 | ELA and copy-move image forensics | NOT_STARTED |
| `P2-T09` | 2 | pyHanko signature verification, Iranian trust store, offline CRL cache | NOT_STARTED |
| `P2-T10` | 2 | Verification status model and weighting | NOT_STARTED |
| `P2-T11` | 2 | Cross-document consistency matrix engine | NOT_STARTED |
| `P2-T12` | 2 | Shahkar interactive OTP flow and consent records | NOT_STARTED |
| `P2-T13` | 2 | Official issuer verification orchestrators (Tamin, MSRT, TVTO) | NOT_STARTED |
| `P2-T14` | 2 | 4-way experience disambiguation engine | NOT_STARTED |
| `P2-T15` | 2 | Evidence credibility score (V_score) | NOT_STARTED |
| `P2-T16` | 2 | OCR accuracy harness and 500-document authentic corpus | **BLOCKED** (corpus acquisition) |
| `P2-T17` | 2 | Document forensics test suite | NOT_STARTED |
