## Summary of Changes

A concise description of what this PR does and why.

## Related Issues / Decisions / ADRs

- WBS / Task:
- ADR reference (if applicable):
- Closes #

## Invariant Conformance Checklist

Please verify that none of the non-negotiable invariants (per `AGENTS.md` §2) are violated:

### Financial & Numerical Integrity
- [ ] No `float` used in monetary calculations (only `Decimal` with `ROUND_HALF_UP` and `prec = 34`).
- [ ] No `round()` on monetary figures.
- [ ] Rounding residuals tracked where line items sum to a total.
- [ ] Pure functions for calculation paths (no clock/random/network inside calculations).

### Domain Integrity
- [ ] Refusal invariant respected: the engine returns `insufficient_data` instead of fabricating salary numbers.
- [ ] AI / LLM is restricted to text and document analysis, never generating salary figures.
- [ ] Statutory requirements treated as hard constraints.

### Security & Privacy
- [ ] No credentials, secrets, National IDs, mobile numbers, or real salary figures in code, fixtures, or logs.
- [ ] Tenant data isolation respected (RLS where applicable).
- [ ] Sensitive personal data encrypted with AES-256-GCM / HMAC blind indexed.

## Verification Executed

- [ ] `backend`: `uv run ruff check .` (PASS)
- [ ] `backend`: `uv run mypy --strict app tests` (PASS)
- [ ] `backend`: `uv run pytest -q` (PASS)
- [ ] `frontend`: `pnpm lint` (PASS)
- [ ] `frontend`: `pnpm typecheck` (PASS)
- [ ] `frontend`: `pnpm test` (PASS)
- [ ] `frontend`: `pnpm build` (PASS)
