"""Pish Hesabdari — pre-employment compensation intelligence platform.

The package is deliberately empty of logic at this level.  Everything that
carries behaviour lives in a sub-package that names its authority:

* `app.core`    — configuration, logging, security primitives, tenancy, audit
* `app.engines` — the statutory calculation engines (never a `float`)
* `app.models`  — SQLAlchemy 2.0 models
* `app.schemas` — Pydantic v2 request and response schemas
* `app.services`— domain services
* `app.api`     — HTTP routers
"""
