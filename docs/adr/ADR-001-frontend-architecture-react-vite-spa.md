# ADR-001: Selection of React + Vite SPA over Next.js SSR for Enterprise Client Application

- **Status**: Accepted
- **Date**: 2026-11-13 (22 Aban 1405 SH)
- **Deciders**: Enterprise Architect, Frontend Lead, Security Architect
- **Consulted**: DevOps Lead, Product Manager

## Context and Problem Statement
The Pish Hesabdari platform requires an interactive, high-performance web interface for corporate executives (CEOs, CFOs, HR Directors) to simulate compensation packages, inspect forensic document analyses, and review pre-hire risk dossiers. 

The original specification (`PHASE_1_FINAL_AUDIT_BRIEF.md`) recommended **Next.js 14+ with React 18**. However, our Red-Team Audit (`FIND-ARCH-01`) challenged this choice, identifying unnecessary Node.js server overhead, complex deployment in restricted Iranian enterprise intranets, and severe security attack surfaces for an application that is strictly authenticated and has zero public-facing content.

## Decision Drivers
1. **Zero SEO Requirements**: The platform is an authenticated enterprise B2B dashboard. No pages are indexed by search engines.
2. **Operational Simplicity in Iranian Intranets**: Many Iranian enterprise clients require air-gapped or private cloud deployments where maintaining long-running Node.js application servers alongside Python/PostgreSQL adds substantial maintenance burden.
3. **Security Attack Surface**: Eliminating server-side JavaScript execution (Node.js runtime) closes vulnerabilities related to SSR injection, Node dependency bloat, and server action compromises.
4. **Build & Startup Performance**: Fast sub-second Hot Module Replacement (HMR) and instantaneous static asset delivery via Nginx or CDN.

## Considered Options
1. **Option 1**: Next.js 14+ (App Router, Server-Side Rendering & Server Components)
2. **Option 2**: React 18/19 + Vite + TypeScript + Tailwind CSS (Pure Client-Side SPA)
3. **Option 3**: Remix / React Router v7 (SSR-first)

## Decision Outcome
Chosen option: **Option 2: React 18/19 + Vite + TypeScript (Pure Client-Side SPA)**.

### Positive Consequences
- **Static Asset Serving**: The frontend compiles to static HTML, CSS, and JS bundles that can be served directly from Nginx, Traefik, or an S3 bucket with zero server runtime overhead.
- **Trivial On-Premise Deployment**: Iranian enterprise clients can deploy the entire frontend container using a minimal 25MB Nginx Alpine image.
- **Zero Hydration Mismatches**: Eliminates client-server state divergence bugs that plague complex analytical dashboards in Next.js.
- **Independent API Decoupling**: Enforces strict REST/JSON contract separation with the FastAPI backend.

### Negative Consequences / Trade-offs
- Initial bundle download must be optimized via route-level code splitting (`React.lazy`).
- Client-side token storage must be securely managed using in-memory state and HTTP-only Secure SameSite cookies.

## Pros and Cons of Considered Options

### Option 1: Next.js 14+
- *Pros*: Excellent ecosystem, built-in routing, API routes.
- *Cons*: Requires dedicated Node.js server fleet, high memory footprint, complex Docker images, severe overkill for authenticated dashboards, dependency on Vercel-oriented conventions.

### Option 2: React + Vite SPA (Chosen)
- *Pros*: Ultra-lightweight, sub-second builds, pure static deployment, zero Node.js production maintenance, rock-solid stability in air-gapped intranets.
- *Cons*: No built-in SSR (irrelevant for internal enterprise tools).

## Implementation Directives
1. Scaffold frontend using `npm create vite@latest frontend -- --template react-ts`.
2. UI Component Library: Shadcn/UI (Radix UI primitives) styled with Tailwind CSS and RTL support for Persian typography (Vazirmatn font).
3. State & Server Cache: TanStack Query v5 (React Query) for API synchronization; Zustand for lightweight UI state.
4. Production Dockerfile: Multi-stage build (Node 20 builder -> Nginx 1.25 Alpine runner).
