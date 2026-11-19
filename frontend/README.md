# Pish Hesabdari — Persian frontend foundation

Client-side SPA per **ADR-001** (React + Vite + TypeScript, no SSR). This directory
contains the bounded portion of **P3-T01** and the unblocked work of **P3-T02**,
**P3-T04**, **P3-T05** and **P3-T06**.

> **Status: the WBS tasks are not complete.** P3-T01's dependency (`P1-T19`,
> the simulation API) is not delivered, and P3-T03 is gated by the open
> decision **DEC-006**. A rendered scaffold is not task completion
> (`AGENTS.md` §4, Holy Bible §13.8 rule 8).

## Commands

`pnpm` is the mandated package manager (`SPEC-OPS-001` §2.4; an npm lockfile is
rejected by `.gitignore`). If `pnpm` is not on `PATH`, run it through `npx`
without installing anything globally:

```bash
npx --yes pnpm@9 install
npx --yes pnpm@9 dev          # http://127.0.0.1:5273
npx --yes pnpm@9 run build    # tsc --noEmit && vite build
npx --yes pnpm@9 run typecheck
npx --yes pnpm@9 run lint     # the physical-direction-utility gate
npx --yes pnpm@9 test
```

Configuration: one build-time public variable, `VITE_API_BASE_URL` (service
origin, e.g. `http://localhost:8000`). See [`.env.example`](.env.example). No
secret may ever be placed in a `VITE_*` variable — it is compiled into the bundle.

## What is implemented

### MVP 0.1 local demo (2026-11-15)

The owner-requested demo adds `/` (summary cards, chart and recent transactions),
`/transactions` (read-only synthetic rows), and `/settings` (session-only Rial/Toman
display preference). Fixtures live in `src/data/demo-accounting.ts`; existing
exact formatting helpers are reused. Amounts are explicitly synthetic, not
statutory outputs or fallback API responses. The previous overview and real health
query are preserved at `/system`; earlier modules remain in expandable navigation.
No backend, authentication, production financial workflow or dependency was added.
This demo does not complete broader WBS tasks or change their gates.

If the host pnpm wrapper attempts to reinstall existing dependencies before a
script, these command-local options avoid that check without global changes:

```powershell
pnpm --config.manage-package-manager-versions=false --config.verify-deps-before-run=false run dev --host 127.0.0.1
pnpm --config.manage-package-manager-versions=false --config.verify-deps-before-run=false run typecheck
pnpm --config.manage-package-manager-versions=false --config.verify-deps-before-run=false run build
```

With dependencies installed, `node node_modules/vite/bin/vite.js --host 127.0.0.1`
also starts the local demo at `http://127.0.0.1:5273/`.

| Area | State |
| :--- | :--- |
| Vite + React 19 + TS + Tailwind v4 + Shadcn-style primitives (`cva` + Radix Slot) | done |
| TanStack Query v5, Zustand, route-level `React.lazy` splitting | done |
| Single RTL declaration at the document root (`lang="fa" dir="rtl"`) | done |
| Logical-property CSS only + a gate that rejects physical utilities | done, tested |
| Vazirmatn, self-hosted `.woff2` from the app origin, OFL | done |
| Three-layer numeral policy (display / input / machine) | done, tested |
| Rial + Toman formatting with a mandatory unit label; no fractional Rial; Toman refused when not divisible by 10 | done, tested |
| Rate-as-string percentage formatting (one decimal, U+066B, U+066A) | done, tested |
| Icon inventory with recorded directionality and `rtl:-scale-x-100` mirroring | done, tested |
| Typed API client: correlation id, error catalogue, 4xx/5xx/network/malformed mapping, 401 → session-expiry route | done, tested |
| `rule_set_status` warning surface and provenance footer | done, tested |
| RTL app shell: skip link, landmarks, navigation for all approved modules, responsive drawer, Rial/Toman display toggle | done, tested |
| Accessible loading / skeleton / empty / error states | done, tested |
| Presentation-only sign-in, MFA and session-expiry screens | done — **no token storage, no session semantics, no request** |
| Development-only labelled fixture preview at `/dev/preview` | done — the route is not registered in a production build (verified: no `dev/preview` route in the built bundle) |

## What is deliberately **not** implemented

- **Any financial or statutory calculation.** The browser never recomputes a
  figure; displayed values must be byte-identical to the API response.
- **Jalali conversion.** `src/lib/calendar.ts` exposes a `JalaliConverter` port
  and formats Jalali *parts*; it registers no implementation, because DEC-006
  (`L-1`) is open and hand-rolling the algorithm is forbidden
  (`SPEC-FE-001` §5.1). The picker (P3-T03) is therefore not built.
- **Authentication.** `POST /auth/login` and `/auth/mfa/verify` do not exist.
  The screens are disabled and say so. No token, cookie or session policy is
  invented, and no route guard is added — a client-side guard against a
  non-existent session would imply a security control the product does not have.
- **Any endpoint beyond `GET /health/live`.** `src/api/contracts.ts` is an
  inventory of delivered versus `awaiting-backend` contracts; screens that need
  an undelivered contract state the owning task instead of faking data.
- **PDF output, charts, benchmark visualisation** (P3-T10, P3-T11) — gated by
  DEC-006 and by undelivered APIs.

## Missing dependencies and open decisions

| Item | Effect |
| :--- | :--- |
| `P1-T19` simulation API | Blocks P3-T01 completion, P3-T07, P3-T08 |
| `P0-T18` session/auth API | Blocks P3-T06; screens stay presentation-only |
| `P2-T02`/`P2-T10`, `P1-T18` | Block P3-T09 and P3-T10 |
| **DEC-006** (Jalali library, PDF pipeline, chart library, numeric column alignment) | Blocks P3-T02's calendar portion, P3-T03, P3-T10, P3-T11 |
| Backend error catalogue (`app/api/errors.py`) | `src/api/errors.ts` maps HTTP status to a **provisional** catalogue until the real one lands |

## Notable implementation decisions

- **Shadcn/UI** was applied as its conventions (`cva`, `clsx`, `tailwind-merge`,
  Radix `Slot`), not via its CLI: the primitives in `src/components/ui/` are
  ours, carry no vendor directory, and are therefore fully subject to the
  logical-utility gate.
- The gate skips string literals inside comments, permits `rtl:`/`ltr:` scoped
  physical utilities (as `SPEC-FE-001` §2.3 requires), and supports one explicit
  opt-out marker used only by its own tests.
- `formatMoney` accepts ASCII machine values only; Persian digits are folded by
  the input layer first, so the display layer can never disagree with the bytes
  in the database.
- Table numeric alignment inside RTL tables is **not** finalised — that is
  unresolved item `L-4` (QB-08), not a silent choice.

## Verification performed

See the handoff report in the delivery message: `typecheck`, `lint`, `test`
(123 tests, 14 files, current baseline) and `build` were run, and the running app was inspected at
1440 px and 360 px in the browser (direction, navigation, drawer state, unit
labels, refusal of Toman for a non-divisible amount, no horizontal overflow).

Not verified: any authenticated flow, any real API response other than the
health probe (the backend was not running), axe (P3-T12), and any PDF output.

Fresh adoption verification (2026-11-15, BOOTSTRAP_CHANGELOG §19): **123 tests
across 14 files PASS**, typecheck via production build PASS, logical-utility
gate PASS. Independent review found and verified repairs to short/integer rate
percentage formatting and unsafe JavaScript number inputs. Exact string/bigint
amounts remain supported. Misleading session-expiry and base-URL comments were
corrected; no session policy was implemented. Backend liveness/CORS/correlation
and frontend HTTP/RTL-root smoke checks passed with both local services running;
this session did not perform visual/axe/E2E verification. The paragraph above
describes historical baseline checks, not the current backend process.

Note on the preview bundle: the bundler still emits an *orphan* chunk for
`routes/dev-preview-page.tsx` (no importer references it, and the route is not
registered in production). It contains only the labelled synthetic fixtures —
no real data — but it does exist in `dist/`. Removing it entirely would need a
build-time alias, which was judged out of scope for this bounded task.
