"""Deterministic statutory calculation engines.

The package exposes the exact Decimal money primitives and the Rial rounding
policy (WBS P1-T04) and, under ADR-008, the statutory payroll engine: the
fail-closed rule-set loader (P1-T01), the base decomposition (P1-T07), the
SSO engine (P1-T06), the progressive tax engine with the Article 137 dual
posture (P1-T05), the overtime engine (P1-T10), the Sanavat engine
(P1-T08), the Eydi engine (P1-T09), the employer-cost engine (P1-T11), the
termination simulator (P1-T12) and the error catalogue.  Engines are pure:
they never read the clock, randomness, the network or the environment.
Importing this package also sets the shared decimal context (``prec=34``,
``ROUND_HALF_UP``) once, as required by HB-NFR-010 and
``docs/EXECUTION_PLAN.md`` §7.2.

Authority: ``docs/PISH_HESABDARI_HOLY_BIBLE.md`` §13.8 rule 7; ADR-008.
"""

from __future__ import annotations

from app.engines.bases import Allowances, MozdDecomposition, decompose_bases
from app.engines.ctc import EmployerCostResult, compute_employer_cost
from app.engines.errors import (
    PayrollEngineError,
    PayrollInputError,
    RuleSetNotActive,
    StatutoryParameterUnavailable,
    TaxableBaseNegative,
)
from app.engines.eydi import EydiResult, compute_eydi
from app.engines.money import (
    MAX_RESIDUAL_RIAL_PER_LINE,
    MONEY_PRECISION,
    RIAL_QUANTUM,
    MoneyError,
    MoneyTypeError,
    MoneyValueError,
    RialAllocation,
    RoundingReport,
    RoundingResidualError,
    allocate_rial,
    quantize_rial,
    reconcile_lines,
    round_half_up,
    round_rial,
    round_total_rial,
    rounding_residual_rial,
    split_rial,
    to_decimal,
)
from app.engines.overtime import OvertimeResult, compute_overtime_premiums
from app.engines.rules import (
    ACTIVE_STATUTORY_YEARS,
    StatutoryRuleSet,
    TaxBracket,
    load_rule_set,
    validate_invariants,
)
from app.engines.severance import SeveranceAccrual, compute_monthly_severance_accrual
from app.engines.sso import SsoResult, compute_sso
from app.engines.tax import (
    POSTURE_CONSERVATIVE_INTA,
    POSTURE_COURT_PRECEDENT,
    PostureTaxResult,
    TaxPosture,
    art137_deduction_exact,
    compute_progressive_tax,
    compute_tax_for_posture,
    resolve_welfare_taxable,
    validate_posture,
)
from app.engines.termination import (
    MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR,
    MAX_PROBATION_MONTHS,
    TerminationResult,
    compute_termination_liability,
)

#: Engine identity carried by every response; also re-exported from the
#: composition service.  Bumped only with a changelog entry.
ENGINE_VERSION = "0.2.0-payroll-engine"

__all__ = (
    "ACTIVE_STATUTORY_YEARS",
    "ENGINE_VERSION",
    "MAX_LEAVE_CARRYOVER_DAYS_PER_YEAR",
    "MAX_PROBATION_MONTHS",
    "MAX_RESIDUAL_RIAL_PER_LINE",
    "MONEY_PRECISION",
    "POSTURE_CONSERVATIVE_INTA",
    "POSTURE_COURT_PRECEDENT",
    "RIAL_QUANTUM",
    "Allowances",
    "EmployerCostResult",
    "EydiResult",
    "MoneyError",
    "MoneyTypeError",
    "MoneyValueError",
    "MozdDecomposition",
    "OvertimeResult",
    "PayrollEngineError",
    "PayrollInputError",
    "PostureTaxResult",
    "RialAllocation",
    "RoundingReport",
    "RoundingResidualError",
    "RuleSetNotActive",
    "SeveranceAccrual",
    "SsoResult",
    "StatutoryParameterUnavailable",
    "StatutoryRuleSet",
    "TaxBracket",
    "TaxPosture",
    "TaxableBaseNegative",
    "TerminationResult",
    "allocate_rial",
    "art137_deduction_exact",
    "compute_employer_cost",
    "compute_eydi",
    "compute_monthly_severance_accrual",
    "compute_overtime_premiums",
    "compute_progressive_tax",
    "compute_sso",
    "compute_tax_for_posture",
    "compute_termination_liability",
    "decompose_bases",
    "load_rule_set",
    "quantize_rial",
    "reconcile_lines",
    "resolve_welfare_taxable",
    "round_half_up",
    "round_rial",
    "round_total_rial",
    "rounding_residual_rial",
    "split_rial",
    "to_decimal",
    "validate_invariants",
    "validate_posture",
)
