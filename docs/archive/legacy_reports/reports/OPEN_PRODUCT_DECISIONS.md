# OPEN_PRODUCT_DECISIONS.md

Open Product Decisions — Pish Hesabdari

Decisions requiring product-owner input. Each decision includes the issue, why it matters, recommended option, alternatives, and the specific question to ask.

## D-02: Authentication on Salary Estimation Endpoint

**Status:** OPEN

**Issue:** The `POST /api/v1/simulations/salary-estimation` endpoint has no authentication dependency. It is publicly accessible.

**Why it matters:** Without authentication, anyone can submit candidate salary estimation requests. For an internal management tool, this may be acceptable behind a corporate network, but for any externally accessible deployment, authentication is required.

**Recommended option:** Keep unauthenticated for MVP (single manager, internal use only). Add authentication in next stage when multi-user support is needed.

**Alternatives:**
1. Add session-based authentication now (delays MVP)
2. Add API key authentication (adds complexity)
3. Keep open, rely on network-level security (recommended for MVP)

**Question:** Should the salary estimation endpoint require authentication for the MVP, or can it remain unauthenticated for internal manager use?

---

## DEC-01: Market Data Source

**Status:** OPEN

**Issue:** The engine uses mock seed data (`MOCK_MARKET_DATA`, `EXTENDED_MOCK_MARKET_DATA`) with limited coverage (Tehran, Saveh, Isfahan only; 5 job titles). A licensed `MarketDataRepository` is proposed but not approved.

**Why it matters:** Without reliable market data, the engine cannot provide accurate recommendations for most cities and job titles. The 409 refusal correctly handles this, but the product is limited in usefulness.

**Recommended option:** Approve mock seed data as MVP placeholder with clear "seed data" labeling. Require licensed repository for production launch.

**Alternatives:**
1. Use mock data with clear labeling (recommended for MVP)
2. License a market data repository now (delays MVP, requires budget approval)
3. Integrate with public salary APIs (data quality/provenance concerns)

**Question:** Can we proceed with mock seed data for the MVP, clearly labeled as such, or is a licensed market data repository required before launch?

---

## ADR-005: Background Job Queue

**Status:** Proposed (not accepted)

**Issue:** software-architecture skill and REMEDIATED §3.1 name BackgroundTasks for slow-path execution, but ADR-005 is proposed and P2-T04 remains blocked.

**Why it matters:** The current calculation is synchronous and fast. A job queue is not needed for MVP but may be needed for future async processing.

**Recommended option:** Do not implement. Keep the JobQueue interface boundary; do not treat a proposed queue as approved.

**Question:** Confirm that ADR-005 should NOT be implemented for MVP.

---

## Navigation Duplication (UI Bug)

**Status:** OPEN (pre-existing)

**Issue:** The "بازار حقوق" link appears twice in the main navigation (in both `PRIMARY_NAV_ITEMS` and `NAV_ITEMS`).

**Why it matters:** Minor UI confusion. Does not affect the core salary estimation workflow.

**Recommended option:** Fix in P3 (product quality phase), not P0/P1.

**Question:** Confirm this can be deferred to P3.

---

## Agreed Salary and Decision Recording

**Status:** NOT STARTED (P1 next stage)

**Issue:** The MVP shows the market recommendation but does not allow the manager to record an agreed salary or an Accept/Modify/Reject decision.

**Why it matters:** Per the product definition, the manager must be able to distinguish the agreed salary from the recommendation.

**Recommended option:** Implement agreed salary input and decision recording in the next stage (P1).

**Question:** Confirm that agreed salary and decision recording are P1 next-stage tasks, not MVP blockers.
