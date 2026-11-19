"""Domain layer.

Authority
---------
``docs/adr/ADR-014-market-salary-reference-data-and-estimation.md`` §3 records
that the salary-estimation domain lives in ``app/domain/salary_estimation`` and
that ``docs/ARCHITECTURE.md`` §2's ``app/engines/estimation.py`` path was never
implemented.  The conflict is registered for the owner; this package marker only
makes the existing package importable as a regular package.

Related
-------
``app/engines`` — the statutory payroll engines (ADR-008/ADR-011), untouched.

Scope
-----
No calculation lives here.  Domain modules are imported by ``app.services``.
"""

from __future__ import annotations
