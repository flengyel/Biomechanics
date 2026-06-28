"""Tests that guard architectural layer boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

from biomech_tutor.layers import (
    BOUNDARY_RULES,
    STUDENT_PROJECTION_FORBIDDEN_TERMS,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_layer_import_boundaries_are_respected() -> None:
    violations: list[str] = []
    for rule in BOUNDARY_RULES:
        for source_path in _python_files_for_package(rule.package):
            for imported_module in _imported_modules(source_path):
                if _matches_forbidden_prefix(
                    imported_module, rule.forbidden_import_prefixes
                ):
                    violations.append(
                        f"{source_path.relative_to(PACKAGE_ROOT)} imports "
                        f"{imported_module}: {rule.reason}"
                    )

    assert violations == []


def test_student_projection_public_code_avoids_engine_terms() -> None:
    violations: list[str] = []
    for source_path in _python_files_for_package("biomech_tutor.student_projection"):
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_path))
        public_text = "\n".join(
            ast.get_source_segment(source, node) or ""
            for node in ast.walk(tree)
            if isinstance(
                node,
                (
                    ast.ClassDef,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.AnnAssign,
                ),
            )
        )
        for forbidden_term in STUDENT_PROJECTION_FORBIDDEN_TERMS:
            if forbidden_term in public_text:
                violations.append(
                    f"{source_path.relative_to(PACKAGE_ROOT)} exposes "
                    f"'{forbidden_term}' in student projection code"
                )

    assert violations == []


def _python_files_for_package(package: str) -> tuple[Path, ...]:
    relative_parts = package.split(".")[1:]
    package_path = PACKAGE_ROOT.joinpath(*relative_parts)
    if package_path.is_file():
        return (package_path,)
    return tuple(sorted(package_path.rglob("*.py")))


def _imported_modules(source_path: Path) -> tuple[str, ...]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    return tuple(imported_modules)


def _matches_forbidden_prefix(
    imported_module: str, forbidden_prefixes: tuple[str, ...]
) -> bool:
    return any(
        imported_module == prefix or imported_module.startswith(f"{prefix}.")
        for prefix in forbidden_prefixes
    )
