"""Validate all scaffolded task fixtures."""

from __future__ import annotations

import sys

from biomech_tutor.tasks.compiler import compile_all_fixture_tasks
from biomech_tutor.tasks.schema import TaskValidationError


def main() -> int:
    try:
        specs = compile_all_fixture_tasks()
    except TaskValidationError as exc:
        print(f"Task fixture validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Validated {len(specs)} task fixtures.")
    for spec in specs:
        print(f"- {spec.id}: {spec.status}, {spec.coverage_level}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
