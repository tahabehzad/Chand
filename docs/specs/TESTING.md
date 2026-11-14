# Specification: Testing & Quality Assurance Strategy

- **Document ID:** `SPEC-QA-001`
- **Status:** Draft — proposed strategy
- **Author:** Documentation Engineering (QA workstream)
- **Date:** 2026-11-14 (23 Aban 1405 SH)
- **Related:** [`docs/EXECUTION_PLAN.md`](../EXECUTION_PLAN.md) §11, §14 · [`docs/specs/AUTH.md`](AUTH.md) · [`docs/specs/STATUTORY_INGESTION.md`](STATUTORY_INGESTION.md) · [`docs/specs/FRONTEND_PERSIAN.md`](FRONTEND_PERSIAN.md)

> **The phase acceptance gates in `REMEDIATED_TECHNICAL_SPECIFICATION_V2.md` §7 are reproduced verbatim in §12 and are not modified by this document.** Any change to a gate requires an explicit, approved change record.

---

## 1. Principles

1. **A financial figure is either exactly right or a build failure.** No tolerance bands, no "close enough", no `pytest.approx` on a Rial amount.
2. **The statutory engine is a pure function.** Its tests must not need a database, a network or a clock.
3. **Money is never a float.** This is enforced statically, not by convention.
4. **A rule set is a versioned input.** Every financial test runs against a pinned `rule_set_version_id`, never against "current".
5. **Isolation is adversarially tested.** The RLS suite assumes a hostile application, not a well-behaved one.
6. **A test that cannot fail is not a test.** Golden vectors, mutation-sensitive assertions and deliberate negative cases are required.
7. **The Phase 1 gate is a legal-evidence gate.** A test vector that has not been signed by a certified tax accountant does not count towards it.

---

## 2. Test Pyramid and Scope

| # | Layer | Scope | Target count | Runtime budget | Blocking? |
| :-- | :--- | :--- | :--: | :--: | :-- |
| L1 | Unit | Pure functions: tax, SSO, sanavat, eydi, overtime, CTC, inverter, formatters, Jalali conversion | ~1,200 | < 60 s | **Yes** |
| L2 | Property-based | Invariants over the whole input space (Hypothesis) | 150 properties | < 180 s | **Yes** |
| L3 | Golden vector | Certified input → expected output, per rule year | 10,000 cases (Phase 1 gate) | < 120 s | **Yes** |
| L4 | Integration | API + real PostgreSQL + real S3 (containerised) | ~300 | < 400 s | **Yes** |
| L5 | Contract | OpenAPI schema conformance, request/response shapes, error catalogue | ~120 | < 60 s | **Yes** |
| L6 | Isolation | RLS penetration, tenant escape, privilege escalation | ~90 | < 180 s | **Yes** |
| L7 | Cryptography | ALEE round-trip, blind-index determinism, key rotation, chain integrity | ~80 | < 60 s | **Yes** |
| L8 | Document pipeline | OCR extraction accuracy, forensics detectors, verification status | ~250 | < 900 s | **Yes** (accuracy gate) / No (others) |
| L9 | Frontend component | Vitest + Testing Library + axe | ~300 | < 180 s | **Yes** |
| L10 | End-to-end | Playwright, full user journeys | ~40 | < 400 s | **Yes** |
| L11 | Security | Static analysis, dependency audit, secret scan, SAST | continuous | < 240 s | **Yes** (high/critical) |
| L12 | Performance | Latency budgets, load, OCR throughput | ~25 | < 600 s (scheduled) | **No** in PR; **Yes** pre-release |
| L13 | Regression | Cross-year rule-set differential, historical snapshots | ~400 | < 240 s | **Yes** |

---

## 3. Tooling

| Concern | Tool | Rationale |
| :--- | :--- | :--- |
| Test runner (backend) | **pytest** | Industry standard; first-class fixture and marker support |
| Assertions | `pytest` + `hypothesis` | `hypothesis` is the property-based engine |
| Property-based | **Hypothesis** (Python) | Generates boundary-relevant inputs automatically |
| Coverage | `pytest-cov` + `coverage.py` | Branch coverage reporting |
| Static analysis | **ruff** (lint + format) + **mypy** (`strict`) | Single fast tool; no `flake8`/`black`/`isort` sprawl |
| Money-safety lint | **custom ruff rule** + `pytest` AST scan | Bans `float` in `backend/app/engines/**` |
| API contract | **Schemathesis** (or `hypothesis-jsonschema`) | Property-based OpenAPI conformance |
| DB integration | `pytest` + `testcontainers` (or docker-compose fixtures) | Real PostgreSQL 16, never SQLite |
| E2E | **Playwright** (Chromium) | Single tool for cross-browser; trace/screenshot on failure |
| Frontend unit | **Vitest** + **@testing-library/react** + **jest-axe** | Matches the Vite toolchain |
| Frontend E2E | **Playwright** (same as backend) | One browser automation stack |
| Security | `pip-audit`, `npm audit`, `bandit`, `semgrep`, `gitleaks` | SAST + dependency + secret scanning |
| Load | **k6** (or Locust) | Scriptable; a text file is reviewable |
| Mutation (financial core) | `mutmut` | Proves the golden vectors actually bite — optional, gated to the engines |

### 3.1 Static enforcement of the money rule

```python
# backend/tests/test_money_discipline.py — architectural test
FORBIDDEN_NODES = (ast.Name, ast.Attribute)

def test_engine_modules_contain_no_float_operations():
    for path in Path("backend/app/engines").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, float):
                pytest.fail(f"{path}:{node.lineno} float literal {node.value!r} "
                            "in a money path — use decimal.Decimal(str(...))")
```

A `float` literal anywhere under `backend/app/engines/**` fails the build. This is the mechanical form of the `financial-data-integrity` skill's rule 1.

---

## 4. Unit Tests — Financial Core (L1)

### 4.1 Required coverage of the statutory engine

| Area | Minimum cases | Notes |
| :--- | :--: | :--- |
| Progressive tax | 120 | Every slab boundary: exactly at the boundary, ±1 Rial either side, and inside each band |
| Tax exemption | 20 | Exactly at the exemption, exemption − 1, exemption + 1 |
| Article 137 dual policy | 40 | `conservative_inta` (2/7) and `court_precedent` (full 7%); SSO capped and uncapped |
| SSO ceiling | 40 | Exactly at the ceiling, ceiling ± 1 Rial, 29/30/31-day months |
| Sanavat | 30 | Base = *Mozd-e Saabet* (welfare excluded, continuous attraction included); fractional years |
| Eydi | 30 | Below the 60-day floor, at the floor, between floor and cap, at the cap, above the cap; progressive taxation of the excess |
| Overtime | 40 | 220 h and 227.33 h divisors; welfare allowances excluded from numerator **and** divisor; 1.40 and 1.35 multipliers |
| CTC | 30 | No 26-day leave double count; leave carryover capped at 9 days; 29/30/31-day months |
| Termination | 25 | Art. 11 full-probation liability on employer termination; Art. 66/71 leave buyout across years |
| Net-to-Gross inversion | 80 | Every slab region, the SSO-ceiling region boundary, and both Article 137 policies |
| Gross-to-Net | 40 | Forward direction, bracket selection |
| Rounding | 30 | Half-up behaviour at exact `.5` boundaries; reconciliation identities |

### 4.2 Reconciliation invariants — asserted on every calculation

These are asserted in a **shared fixture** applied to every financial test, so no test can produce an internally inconsistent result:

```
(1) Gross − Σ(deductions) == Net                            exactly, in integer Rial
(2) Σ(line items) − total == rounding_residual_rial         |residual| <= 1 per line, signed and surfaced
(3) total_employer_cost == Gross + employer_SSO + unemployment + sanavat + eydi + residuals
(4) net_to_gross(gross_to_net(G)) == G                       within 1 Rial
(5) every emitted figure is an int (never a float, never a Decimal with a fractional part)
```

Invariant (2) is what prevents the class of defect found in the original §5.1 example, where `monthly_sanavat_accrual` was computed on the wrong base and the total silently absorbed the difference.

### 4.3 Rounding policy under test

| Rule | Assertion |
| :--- | :--- |
| Mode | `ROUND_HALF_UP` only. Python's built-in `round()` (banker's rounding) is banned on money |
| Precision | `getcontext().prec = 34`; never the default 28 |
| Round once | Round at the line-item boundary; do not round an intermediate and reuse it |
| Residual | Any difference between the sum of rounded lines and the rounded total is surfaced as a signed `rounding_residual_rial` ≤ 1 Rial per line |
| Splits | Use the largest-remainder method so allocated parts sum exactly to the total |

---

## 5. Property-Based Tests (L2)

Hypothesis strategies over the input space. **Every property must be a mathematical invariant, not a restatement of the implementation.**

| ID | Property |
| :-- | :--- |
| P-01 | `net_to_gross(gross_to_net(G)) == G` within 1 Rial, for `G ∈ [1, 5×10⁹]` |
| P-02 | `gross_to_net` is monotonically non-decreasing in `G` |
| P-03 | `Gross − Σ deductions == Net` for all valid inputs |
| P-04 | `employer_SSO + employee_SSO == 0.27 × min(G, ceiling)` (± 1 Rial) |
| P-05 | `sanavat_accrual == Mozd_e_Saabet / 12` (± 1 Rial) |
| P-06 | `eydi_annual == min(2 × Mozd_e_Saabet, 3 × monthly_min_wage)` |
| P-07 | The taxable base is never negative |
| P-08 | The applied tax rate is monotonically non-decreasing in the taxable base |
| P-09 | For all `G`, the returned gross reproduces the target net within 1 Rial |
| P-10 | Allowance set permutations do not change the result (order independence) |
| P-11 | A tenant id in a query never widens the result set |
| P-12 | Jalali ↔ Gregorian round-trips for all dates in 1900–2100 |
| P-13 | Persian digit conversion round-trips for all integers in a sampled range |
| P-14 | The hash chain verifies for any sequence of appended events |
| P-15 | `round_half_up(x)` is monotonically non-decreasing in `x` |

---

## 6. Golden Financial Calculation Vectors (L3) — the Phase 1 gate

### 6.1 Status

> **THE CORPUS DOES NOT EXIST.** It is task `P1-T15`, status **BLOCKED**, owner Certified Tax Accountant (external), and it is the hard gate on Phase 1. **No vector is fabricated.** The engine must not be marked Phase-1-complete without it.

### 6.2 Corpus format

```json
{
  "vector_set_id": "PH-1404.1-ACCT-v1",
  "rule_year_shamsi": 1404,
  "rule_set_version_id": "<uuid>",
  "approved_by": "<certified tax accountant id>",
  "approved_at": "<iso8601>",
  "signature": "<sha256 of canonical json + approver id>",
  "cases": [
    {
      "id": "1404-CASE-0001",
      "input": {
        "target_net_monthly_rial": 280000000,
        "marital_status": "married",
        "eligible_children_count": 1,
        "tax_posture": "conservative_inta",
        "days_in_month": 30,
        "monthly_fixed_allowances_rial": {
          "housing": 9000000, "grocery": 22000000, "marriage": 5000000,
          "child": 10390968, "continuous_attraction": 40000000
        }
      },
      "expected": {
        "computed_gross_rial": 307790549,
        "employee_sso_rial": 21545338,
        "income_tax_rial": 6245211,
        "net_rial": 280000000,
        "employer_sso_rial": 61558110,
        "unemployment_fund_rial": 9233716,
        "monthly_sanavat_accrual_rial": 21783298,
        "monthly_eydi_accrual_rial": 25977420,
        "total_monthly_employer_cost_rial": 426343093
      },
      "note": "Recomputed 2026-11-14 from the verified 1404 dataset. NOT accountant-certified."
    }
  ]
}
```

> The single case above is the **engineering reference** for the 1404 rule set, recomputed independently during this workstream. It is explicitly marked `NOT accountant-certified` and therefore **does not count** towards the 10,000-case gate. It exists so the engine has a starting point; the certified corpus must replace it.

### 6.3 Corpus requirements

| Requirement | Value |
| :--- | :--- |
| Minimum size | **10,000 cases** (Phase 1 gate) |
| Coverage | Every slab, every exemption boundary, every SSO-ceiling boundary, 29/30/31-day months, 0–3 children, single/married, both Article 137 policies, negative and zero-net inputs |
| Golden files | Stored under `backend/tests/golden/{rule_year}/`, hash-pinned in CI |
| Approval | Each rule-year corpus signed by a **Certified Tax Accountant**; the signature is stored with the corpus |
| Change control | Any change to a golden file requires a reviewed pull request that also states why the engine's behaviour changed. A silent golden-file update is a build failure |

### 6.4 The CI golden gate

```
$ pytest backend/tests/golden -q
...
FAILED: golden vector mismatch
  vector_set : PH-1404.1-ACCT-v1
  case_id    : 1404-CASE-0042
  field     : computed_gross_rial
  expected  : 307790549
  actual    : 307790541
  delta     : 8
```

A non-zero delta **fails the build**. There is no tolerance. The Phase 1 gate additionally requires the deviation to be **< 1 Rial**, which in practice means exactly 0.

---

## 7. API Contract Tests (L5)

| Check | Tool |
| :--- | :--- |
| Every response conforms to the OpenAPI 3.1 schema | Schemathesis |
| No undocumented status codes | Schemathesis |
| Every documented status code is reachable | Integration test |
| Every response carries `rule_version`, `rule_set_status`, `engine_version`, `calculation_hash`, `generated_at` | Contract assertion |
| `rule_set_status` equals the value read from the database | Contract assertion — this is the check that would have caught the `1405.1-VERIFIED` defect |
| Monetary fields are integers | Contract assertion |
| Rates are strings with explicit scale | Contract assertion |
| Errors match the error catalogue | Contract assertion |
| Idempotency: repeating a request with the same `Idempotency-Key` returns the same result | Contract assertion |
| `POST /api/v1/simulations/net-to-gross` responds in < 20 ms at p99 | Performance assertion (L12) |

---

## 8. Database, RLS and Isolation Tests (L6)

These constitute the **Phase 0 acceptance gate** ("100% automated test pass on multi-tenant RLS penetration suite; zero plaintext PII in database").

| ID | Test | Expectation |
| :-- | :--- | :--- |
| ISO-01 | Tenant A queries tenant B's row by primary key | 0 rows |
| ISO-02 | Tenant A inserts a row with tenant B's `tenant_id` | `WITH CHECK` violation |
| ISO-03 | No tenant context set | 0 rows, and an exception is raised — never all rows |
| ISO-04 | `SET LOCAL` does not leak across pooled connections | Subsequent query has no context |
| ISO-05 | Table owner path is blocked by `FORCE ROW LEVEL SECURITY` | Owner sees 0 rows without context |
| ISO-06 | Every tenant table has `tenant_id` and a policy | Catalogue introspection |
| ISO-07 | Every tenant table has `FORCE ROW LEVEL SECURITY` enabled | Catalogue introspection |
| ISO-08 | A composite `(tenant_id, id)` unique constraint exists on every FK target | Catalogue introspection |
| ISO-09 | A user with no membership in a tenant gets 403 (not 404) | API test |
| ISO-10 | A super-admin cross-tenant read is audited with both actor and affected tenant | Audit test |
| ISO-11 | A query with a stale/invalid `app.current_tenant_id` fails closed | Integration test |
| ISO-12 | A blob/JSONB column cannot be used to smuggle cross-tenant references | Schema review test |

### 8.1 Zero-plaintext-PII gate

Automated scan of the database and of the audit ledger:

| Pattern | Assertion |
| :--- | :--- |
| A 10-digit National Code in any `text`/`varchar`/`jsonb` column | Absent (except the masked form `001****345`) |
| An Iranian mobile number in any column | Absent |
| An IR/IBAN Sheba in any column | Absent |
| A 64-hex blind index whose input is recoverable by brute force over the National Code space | Not feasible — assert the pepper is not present in the database |

---

## 9. Encryption and Cryptography Tests (L7)

| ID | Test |
| :-- | :--- |
| CR-01 | A ciphertext never equals its plaintext for any input, including edge strings |
| CR-02 | The same plaintext encrypted twice yields **different** ciphertexts (random 96-bit IV) |
| CR-03 | A tampered ciphertext fails AES-GCM authentication (bit-flip, truncation, IV substitution) |
| CR-04 | The blind index for a given value is **deterministic** within a tenant |
| CR-05 | The blind index differs between tenants for the same plaintext (different peppers / salts) |
| CR-06 | `bindex` lookup returns exactly the matching row, in < 1 ms (B-Tree) |
| CR-07 | The blind-index pepper is not present anywhere in the database or in application logs |
| CR-08 | DEK rotation re-encrypts all of a tenant's PII and leaves every value decryptable and every blind index unchanged |
| CR-09 | An old DEK is unusable after rotation and after the grace window |
| CR-10 | The audit hash chain verifies end-to-end after N appends; a tampered row breaks the chain |
| CR-11 | `UPDATE` and `DELETE` on the audit ledger are rejected by the database |
| CR-12 | The session token stored in the database is a hash, never the token |
| CR-13 | No secret appears in a log line, an error message or a traceback |

---

## 10. Document Processing and OCR Tests (L8)

### 10.1 Accuracy gate (Phase 2)

| Metric | Target | Gate |
| :--- | :--- | :--- |
| Field extraction accuracy on 500 authentic Social Security slips | **> 95 %** | **Blocking** — Phase 2 gate |
| Per-field accuracy on the 8 forensic fields | ≥ 90 % each | Blocking |
| Document category classification | ≥ 95 % | Blocking |
| False-positive tamper flag rate | ≤ 5 % | Blocking |
| True-positive detection on a tampered set | ≥ 90 % | Blocking |
| Latency per page | 3.5–6.0 s on 4 vCPU; 1.2–1.8 s on T4 | Non-blocking (reported) |

### 10.2 Test corpus

| Corpus | Size | Status |
| :--- | :--: | :--- |
| Authentic Social Security slips (redacted with employer consent) | 500 | **BLOCKED** — acquisition is `P2-T16`; no synthetic substitute may be used to satisfy the gate |
| Degrees (MSRT / Azad) | 50 | Required for L8 |
| Employment letters | 50 | Required |
| Pay slips | 50 | Required |
| Deliberately tampered set (known ground truth) | 40 | Required for the ELA / structural detectors |
| Digital-signature set (Iranian CA-signed) | 20 | Required for pyHanko; depends on `FIND-ARCH-06` |

> **Honesty requirement.** `PHASE_1_RED_TEAM_AUDIT.md` List 3 records that the "98 %+ OCR accuracy" claim is **[UNVERIFIED — Requires Enterprise Pilot Dataset]**. The test suite must therefore report the measured accuracy on the pilot corpus and must not carry a hard-coded expectation of 98 %.

### 10.3 Non-determinism controls

OCR output is not bit-identical across library versions. Therefore:

- Field-level assertions are used, not byte-level text comparison.
- The extraction model version is pinned and recorded in the artifact.
- Every forensic artifact stores the model version, the library versions and the input `sha256`.

---

## 11. Frontend, E2E, Security and Performance Tests

### 11.1 Frontend component tests (L9)

| Area | Coverage |
| :--- | :--- |
| Numeral helpers | ASCII/Persian/Arabic-Indic conversion, round-trip, rejection of invalid characters |
| Jalali helpers | Leap years, Esfand 29/30, month names, Saturday-first week |
| Currency formatter | Rial/Toman, unit label always present, no decimals, correct separator |
| RTL layout | Snapshot tests at 360 / 768 / 1440 px |
| Directional icons | Mirror assertion per icon |
| Bidi isolation | A Persian paragraph containing Latin/email/URL/parenthetical renders with correct order |
| Accessibility | `jest-axe` on every component with an interactive surface |
| Forms | Simple/Advanced mode switching, validation messages in Persian |

### 11.2 End-to-end tests (L10)

| Journey | Assertion |
| :--- | :--- |
| Sign in → run a net-to-gross simulation → read the dual-scenario result | Completes; the displayed net equals the API response exactly; **< 3 s** end-to-end (Phase 3 gate) |
| Upload a document → observe the job → see the verification status | Job reaches a terminal state; status transitions are visible |
| Run a CTC simulation → export the Persian PDF | PDF renders; the PDF's gross equals the on-screen gross exactly |
| A rule set that is not `VERIFIED` | The UI shows the warning; the result is not presented as a quotable offer |
| Tenant isolation through the UI | A user cannot navigate to another tenant's simulation by URL manipulation |
| Persian numerals | The displayed amount converts back to the exact ASCII integer in the API response |

### 11.3 Security tests (L11)

| Check | Tool | Blocking |
| :--- | :--- | :--- |
| Dependency vulnerabilities | `pip-audit`, `npm audit` | Critical/High **Yes**; Medium No |
| SAST | `bandit`, `semgrep` | High **Yes** |
| Secret scanning | `gitleaks` over the full history | Any finding **Yes** |
| Container image scan | `trivy` | Critical/High **Yes** |
| Static security analysis of the frontend | `npm audit`, ESLint security rules | High **Yes** |
| OWASP Top 10 manual review (Phase 4) | External pentest | Gate |

### 11.4 Performance tests (L12)

| Budget | Target | Source |
| :--- | :--- | :--- |
| Net-to-gross inversion | **< 5 ms** | `REMEDIATED` §6 Scenario 1 |
| Fast-path API | **< 20 ms** p99 | `REMEDIATED` §5.1 |
| Full simulation E2E in the browser | **< 3 s** | Phase 3 gate |
| OCR per page | 3.5–6.0 s (4 vCPU) / 1.2–1.8 s (T4) | `FIND-ARCH-05` |
| API throughput | 50 rps sustained on the fast path | Load target |

Performance budgets are **correctness constraints**, not optimisations: the latency budget is part of the API contract.

---

## 12. Phase Acceptance Gates (reproduced verbatim — unchanged)

| Phase | Weeks | Gate |
| :-- | :-- | :--- |
| **Phase 0** — Security and Relational Foundation | 1–4 | 100% automated test pass on multi-tenant RLS penetration suite; zero plaintext PII in database |
| **Phase 1** — Deterministic Engine and Inverters | 5–8 | 10,000-case automated test suite matching certified tax accountant test vectors with < 1 Rial deviation |
| **Phase 2** — Document Forensics and Identity | 9–14 | Successful parsing of 500 authentic Social Security slips with > 95% field extraction accuracy |
| **Phase 3** — Pre-Hire Simulation and React SPA | 15–18 | Full end-to-end simulation completed in < 3 seconds via browser UI |
| **Phase 4** — Pilot Hardening & Compliance Sign-Off | 19–20 | External security penetration testing (OWASP Top 10 + multi-tenant isolation); external legal review sign-off by Iranian labor attorneys |

**Gate evidence mapping**

| Gate | Evidence |
| :--- | :--- |
| Phase 0 | L6 (ISO-01..ISO-12) all pass; L7 CR-01..CR-13 pass; L8 zero-plaintext scan clean; no unresolved Critical finding |
| Phase 1 | L3 golden corpus ≥ 10,000 cases, accountant-signed, 0 Rial deviation; L2 P-01..P-10 pass; L12 inversion < 5 ms; rule set `ACTIVE` and `VERIFIED` |
| Phase 2 | L8 accuracy metrics met on the 500-slip authentic corpus; L8 non-determinism controls in place |
| Phase 3 | L10 E2E < 3 s; L9 axe clean; PDF snapshot matches baseline |
| Phase 4 | External pentest report with no unresolved Critical/High; legal sign-off letter; all Phase 0–3 gates green |

---

## 13. Test Environments

| Environment | Purpose | Data | Isolation |
| :--- | :--- | :--- | :--- |
| **Local (developer)** | Feature work | Synthetic fixtures only; `statutory_rules_1404.yaml` | Local PostgreSQL in Docker; a local Ceph dev container (the storage engine is Ceph — MinIO is not used in any environment) |
| **CI** | Every push and PR | Seeded synthetic fixtures + the pinned golden corpus | Ephemeral containers per job; no shared state |
| **Integration** | Cross-service verification | Seeded synthetic + a scrubbed subset | Dedicated PostgreSQL instance; RLS policies active |
| **Staging** | Release candidate rehearsal | Scrubbed production-shaped data (PII scrubbed) | Full topology: PostgreSQL + Ceph/S3 (GOVERNANCE) + app + proxy |
| **Pilot (production)** | 3 design-partner corporations | Real | Full topology + monitoring + backup |

**No environment may contain real candidate PII except the pilot**, and the pilot only after the Phase 4 legal sign-off.

---

## 14. Test Data and Fixtures

| Fixture | Purpose | Source |
| :--- | :--- | :--- |
| `statutory_rules_1404.yaml` | Reference rule set for regression | `backend/data/seeds/` (hash-pinned; **must not be modified**) |
| `statutory_rules_1405.yaml` | Candidate rule set | `backend/data/seeds/` — **all values `null`; must remain inactive** |
| Golden vector corpus | Financial correctness | **Does not exist** — `P1-T15`, BLOCKED |
| Synthetic candidates | API and E2E tests | Generated fixtures with valid modulo-11 National Codes |
| Synthetic tenants | RLS tests | Fixture factory that creates N tenants × M rows |
| Masked PII | UI tests | `001****345` style; **never real** |
| Document corpus | OCR tests | See §10.2 — **BLOCKED** pending acquisition |

**Fixture rules**
- All National Codes in fixtures must pass the modulo-11 check, so validation tests are not bypassed by invalid data.
- No fixture may contain a real National Code, mobile number or Sheba. A secret-scan rule runs over the fixtures themselves.
- Fixtures are deterministic: no `random` without a fixed seed, no `datetime.now()`.

---

## 15. CI Execution Stages

```
Stage 0  (on every push, ~2 min)     format + lint + type check + secret scan
Stage 1  (on every push, ~3 min)     unit tests (L1) + coverage report
Stage 2  (on every push, ~6 min)     property-based tests (L2) with a reduced example count
Stage 3  (on every push, ~8 min)     golden vectors (L3) + regression (L13)
Stage 4  (on every PR,   ~15 min)    integration + contract (L4, L5)
Stage 5  (on every PR,   ~10 min)    isolation + cryptography (L6, L7)
Stage 6  (on every PR,   ~20 min)    frontend unit + accessibility (L9)
Stage 7  (on every PR,   ~12 min)    E2E (L10) against a containerised stack
Stage 8  (on every PR,   ~8 min)     security scans (L11)
Stage 9  (nightly)                   full property-based run (high example count)
Stage 10 (nightly)                   document pipeline suite (L8)
Stage 11 (pre-release)               performance/load (L12) + full L2 + full L8
Stage 12 (on release)                penetration re-test + migration dry-run + rollback rehearsal
```

**Gating rule.** Stages 0–8 gate every pull request. Stages 9–10 gate the nightly and must be green for 7 consecutive nights before a release. Stage 11 and 12 gate the release.

---

## 16. Blocking vs Non-Blocking Failures

### 16.1 Always blocking

- Any failure in L1 (unit), L3 (golden), L4 (integration), L6 (isolation), L7 (cryptography)
- Any monetary mismatch of **any** magnitude
- Any tenant-isolation escape
- Any plaintext PII found in the database or the ledger
- Any critical/high dependency vulnerability; any secret detected
- Any failure of the Persian digit round-trip or the PDF snapshot
- Any breach of a latency budget on the fast path

### 16.2 Blocking only at release

- L8 accuracy thresholds (blocking at the Phase 2 gate)
- L12 performance/load thresholds
- Accessibility findings above Level AA
- Medium dependency vulnerabilities

### 16.3 Non-blocking (reported, triaged)

- Non-accuracy document-pipeline metrics
- L2 property failures in the nightly run (blocking after 7 consecutive nights)
- Flaky-test detection: a test that fails intermittently **is a defect**; it is auto-quarantined with an owner and a 48-hour fix SLA, and it is a release blocker if the quarantined test covers a money path.

### 16.4 Never acceptable

- Quarantining a monetary test to unblock a release
- Skipping a stage with an "approved waiver" on a money, isolation or cryptography path
- Re-baselining a golden file without a reviewed change record

---

## 17. Coverage Expectations

| Area | Line | Branch | Notes |
| :--- | ---: | ---: | :--- |
| `backend/app/engines/**` | 95 % | 95 % | The money core. Uncovered branches require a written justification |
| `backend/app/core/security/**`, `.../crypto/**` | 95 % | 90 % | — |
| `backend/app/models/**`, `.../schemas/**` | 90 % | 85 % | — |
| `backend/app/services/**` | 85 % | 75 % | — |
| `backend/app/api/**` | 85 % | 75 % | Contract tests compensate |
| `frontend/src/**` | 85 % | 75 % | — |
| **Repository overall** | **85 %** | **75 %** | No global floor below these per-area floors |

Coverage is a **floor, not a target**. 100 % coverage of the money core is achievable and expected; coverage of `api` boilerplate is not worth chasing.

---

## 18. Release Approval Criteria

A release candidate may be approved only when **all** of the following hold:

1. Every Phase 0–3 gate (§12) is green with archived evidence.
2. The nightly full suite has been green for 7 consecutive nights.
3. No open Critical or High defect; no open Severity-1 or Severity-2 defect in the money, isolation or cryptography paths.
4. The golden corpus for the active rule year is accountant-signed and the CI golden gate reports 0 Rial deviation.
5. The active rule set status is `VERIFIED` and `ACTIVE`; the `statutory_rule_set_versions` row and its signature chain are archived in the legal file.
6. Dependency, SAST, secret and container scans are clean or have a time-boxed, approved exception for Medium findings.
7. The migration dry-run and the rollback rehearsal (§12, Stage 12) have both succeeded against a production-shaped database.
8. Monitoring, alerting and the on-call runbook are live (`docs/specs/DEPLOYMENT.md` §9).
9. The backup and restore drill has succeeded within the preceding 30 days.
10. For the pilot release: the external penetration test report has no unresolved Critical/High finding, **and** the Iranian labor-attorney legal sign-off letter is on file.

**Approvers:** CTO (technical), QA Lead (test evidence), Security Architect (security), Legal Counsel (compliance), Product Manager (scope). No single approver may grant a release that fails criteria 1–5.

---

## 19. Related Tasks

| Task | Phase | Title | Status |
| :--- | :--- | :--- | :--- |
| `P0-T14` | 0 | RLS penetration test suite | NOT_STARTED |
| `P0-T15` | 0 | Encryption and blind-index test suite | NOT_STARTED |
| `P0-T19` | 0 | CI pipeline for the Phase 0 gates | NOT_STARTED |
| `P1-T15` | 1 | Golden vector corpus (certified tax accountant) | **BLOCKED** (external) |
| `P1-T16` | 1 | Property-based test suite (Hypothesis) | NOT_STARTED |
| `P1-T21` | 1 | Performance benchmark suite | NOT_STARTED |
| `P2-T16` | 2 | OCR accuracy evaluation harness and 500-document corpus | **BLOCKED** (corpus acquisition) |
| `P2-T17` | 2 | Document forensics test suite | NOT_STARTED |
| `P3-T12` | 3 | Frontend component tests and accessibility audit | NOT_STARTED |
| `P3-T13` | 3 | End-to-end test suite | NOT_STARTED |
| `P4-T05` | 4 | Performance and load test at pilot scale | NOT_STARTED |
| `P4-T06` | 4 | External penetration test | NOT_STARTED |
