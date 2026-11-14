---
name: spec-driven-development
description: Translates product requirements and statutory laws into comprehensive, unambiguous specifications, OpenAPI contracts, BDD/Gherkin acceptance criteria, and exact mathematical test vectors.
---

# Spec-Driven Development (SDD) Skill

## Purpose
Ensure that no code is written before complete, verifiable, and mathematically validated specifications exist. Eliminate ambiguity between legal statutes and software implementation.

## Specification Deliverable Requirements
1. **Domain Terminology Glossaries**: Unambiguous definitions of Iranian labor concepts (e.g., *Mozd-e Mabna* vs *Mozd-e Saabet* vs *Hoghoogh*, *Sanavat*, *Eydi*, *Hagh-e Maskan*, *Bon-e Kharobar*).
2. **OpenAPI 3.1 Contract Definitions**: Exact request and response schemas, error structures, and validation rules.
3. **Deterministic Mathematical Formulas**: Full equations with all variables, bounds, and precision constraints (Rial rounding conventions).
4. **BDD / Gherkin Acceptance Scenarios**:
   ```gherkin
   Scenario: Calculate Gross from Net under 1405 SH Tax Brackets
     Given an employee with net salary 250,000,000 Rial
     And married with 1 child
     When the net-to-gross solver is executed
     Then the gross salary must be exactly within 1 Rial of theoretical inverse
     And employee SSO contribution must be capped at 7x daily minimum wage
   ```
5. **Exact Numerical Test Vectors**: Verified input-output pairs approved by certified tax accountants and labor lawyers.
