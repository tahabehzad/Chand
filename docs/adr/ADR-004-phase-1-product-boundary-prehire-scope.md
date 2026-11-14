# ADR-004: De-escalation of Phase 1 Scope to Pure Pre-Hire Simulation and Deferral of Post-Hire HRIS Operations

- **Status**: Accepted
- **Date**: 2026-11-13 (22 Aban 1405 SH)
- **Deciders**: Lead Product Manager, Chief Technology Officer, Head of Engineering
- **Consulted**: Sales Director, Enterprise Client Advisory Panel

## Context and Problem Statement
The Phase 1 Final Audit Brief incorporated features that bridged two radically distinct software categories:
1. **Core Pre-Hire Intelligence**: Candidate verification, statutory wage modeling, Net-to-Gross solving, and hiring offer simulation (*Hokm-e Kargozini*).
2. **Post-Hire Enterprise HRIS Operations**: Company-wide annual employee salary review budget optimization (Module 5 MCDA), continuous internal employee equity compression monitoring, and full operational exit settlement execution (*Tasviyeh Hesab*).

The Red-Team Audit (`FIND-PROD-01` and `FIND-PROD-02`) established that this scope creep inflated development timelines from 20 weeks to over 40 weeks, diffused engineering focus, and diluted the core market positioning of "Pish Hesabdari" (Pre-Accounting).

## Decision Drivers
1. **Speed to Market**: Deliver an enterprise-grade, validated MVP within 20 weeks.
2. **Unambiguous Value Proposition**: Establish Pish Hesabdari as the undisputed authority on pre-hire compensation defensibility and document forensics in Iran.
3. **Boundary Integrity**: Avoid direct competition with entrenched Iranian payroll/HRIS vendors (e.g. Charsoon, Hamkaran System, Rayvarz) until pre-hire market dominance is established.

## Considered Options
1. **Option 1**: Build all 8 modules concurrently in Phase 1 (Original proposal)
2. **Option 2**: Strict Phase 1 focus on Pre-Hire Decision Engine; defer post-hire annual reviews and operational exit execution to Phase 2
3. **Option 3**: Remove exit settlement modeling entirely

## Decision Outcome
Chosen option: **Option 2: Strict Phase 1 Pre-Hire Focus; Defer Post-Hire Enterprise Compensation & Operational Exit Execution to Phase 2**.

### Positive Consequences
- **Phase 1 Modules Focused on Core Mission**:
  1. *Module 1*: Deterministic Iranian Statutory Wage Engine (1405 SH active baseline + 1404 historical).
  2. *Module 2*: Piecewise Analytical Net-to-Gross & Gross-to-Net Inverter ($O(1)$).
  3. *Module 3*: Forensic Document Intelligence & Iranian Authenticity Verification (PP-Structure + pyHanko).
  4. *Module 4*: 4-Way Candidate Experience & Title Disambiguation.
  5. *Module 5*: Pre-Hire Compensation Benchmarking (Bühlmann-Kish Credibility Model).
  6. *Module 6*: Pre-Hire Total Cost to Employer (CTC) & Termination Liability Simulator.
  7. *Module 7*: Cryptographic Snapshot Ledger & SHA-256 Provenance Logging.
- **De-escalated Items Re-Scoped**:
  - *Tasviyeh Hesab*: Kept strictly as a *Pre-Hire Termination Liability Simulator* (projecting severance and exit costs), removing operational bank Sheba execution and dispute settlement advocacy.
  - *MCDA Salary Review*: Internal employee annual review budgeting spun off into a dedicated standalone Phase 2 enterprise product.
- **Engineering Timeline Protected**: Realistic 20-week milestone to production pilot.

### Negative Consequences / Trade-offs
- Enterprise clients seeking an end-to-end annual salary review tool must wait for Phase 2 (mitigated by offering CSV export of pre-hire benchmarks into existing HRIS platforms).

## Implementation Directives
1. Remove all MCDA company-wide salary adjustment endpoints from the Phase 1 OpenAPI specification.
2. Label Module 6 endpoints strictly as `/simulations/pre-hire-ctc` and `/simulations/termination-liability`.
3. Freeze core entities around `Candidate`, `Document`, `HokmSimulation`, and `StatutoryRuleSetVersion`.
