"""AST checks for SQLAlchemy migration storage declarations (P0-T04).

Catalogue checks complement this lint: PostgreSQL has already normalized a
lengthless CHAR into CHAR(1), so that defect must be caught before execution.
This is a declaration lint, not a parser for arbitrary raw SQL.
"""

from __future__ import annotations

import ast


def lint_migration(source: str) -> list[str]:
    """Return deterministic storage violations with one-based source lines."""
    violations: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (
            func.attr
            if isinstance(func, ast.Attribute)
            else (func.id if isinstance(func, ast.Name) else "")
        )
        options = {kw.arg: kw.value for kw in node.keywords}
        reason = ""
        if name in {"CHAR", "VARCHAR", "String"}:
            length = node.args[0] if node.args else options.get("length")
            if (
                not isinstance(length, ast.Constant)
                or type(length.value) is not int
                or length.value <= 0
            ):
                reason = "explicit positive string length required"
        elif name in {"Float", "FLOAT", "REAL", "DOUBLE_PRECISION", "Double"}:
            reason = "floating-point storage forbidden"
        elif name in {"DateTime", "TIMESTAMP"}:
            timezone = options.get("timezone")
            if not isinstance(timezone, ast.Constant) or timezone.value is not True:
                reason = "timezone=True required"
        if reason:
            violations.append(f"line {node.lineno}: {name}: {reason}")
    return violations
