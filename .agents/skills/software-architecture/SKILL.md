---
name: software-architecture
description: Designs modular monolith and distributed architectures, separates synchronous fast paths from asynchronous compute workers, enforces clean boundaries, and evaluates change costs.
---

# Software Architecture Skill

## Purpose
Architect robust, maintainable, and high-performance backend and frontend systems for Iranian enterprise workloads, ensuring proper separation of concerns, scalability, and operational simplicity.

## Core Architectural Principles for Pish Hesabdari
1. **Modular Monolith First**: Avoid premature microservices. Keep domain logic (Statutory, Forensics, Compensation, Tenancy) in cleanly bounded Python modules within a single FastAPI repository.
2. **Strict Fast-Path / Slow-Path Separation**:
   - *Fast Path (Synchronous, <20ms)*: Deterministic statutory wage calculation, net-to-gross closed-form inversion, range penetration analytics. Handled directly by FastAPI worker threads.
   - *Slow Path (Asynchronous Tasks, 1s-10s)*: PDF rasterization, hybrid OCR (PaddleOCR local + Google Gemini API), pyHanko cryptographic verification, ELA image forensics. Dispatched via FastAPI `BackgroundTasks` (eliminating Redis/Celery operational complexity on Windows).
3. **Decoupled Frontend**: Use pure client-side SPA (React + Vite + Tailwind CSS) served locally. Completely avoid Node.js SSR runtime complexity for internal B2B dashboards.
4. **Fail-Closed Security**: Default all multi-tenant queries to zero results unless a verified tenant context is injected.
