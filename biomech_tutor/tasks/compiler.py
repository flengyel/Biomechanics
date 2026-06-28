"""Task compiler and validation entry points."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

from biomech_tutor.tasks.schema import TaskSpec, TaskValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def iter_fixture_paths(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> tuple[Path, ...]:
    """Return YAML fixture paths in deterministic order."""

    if not fixture_dir.exists():
        raise TaskValidationError(f"fixture directory does not exist: {fixture_dir}")

    paths = tuple(sorted(fixture_dir.glob("*.yaml")))
    if not paths:
        raise TaskValidationError(f"fixture directory contains no YAML files: {fixture_dir}")
    return paths


def load_task_file(path: Path) -> TaskSpec:
    """Load and structurally validate one task fixture."""

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TaskValidationError(f"{path} contains invalid YAML: {exc}") from exc

    if raw is None:
        raw = {}
    return TaskSpec.from_mapping(raw, fixture_path=path)


def compile_task_file(path: Path, project_root: Path = PROJECT_ROOT) -> TaskSpec:
    """Compile one task fixture into a validated task spec."""

    spec = load_task_file(path)
    source_path = spec.source_path(project_root)
    if not source_path.exists():
        raise TaskValidationError(
            f"{path} source worksheet does not exist: {spec.source_worksheet}"
        )
    if not source_path.is_file():
        raise TaskValidationError(
            f"{path} source worksheet is not a file: {spec.source_worksheet}"
        )
    return spec


def compile_task_files(
    paths: Iterable[Path], project_root: Path = PROJECT_ROOT
) -> tuple[TaskSpec, ...]:
    """Compile multiple task fixtures into validated task specs."""

    return tuple(compile_task_file(path, project_root=project_root) for path in paths)


def compile_all_fixture_tasks(
    fixture_dir: Path = DEFAULT_FIXTURE_DIR, project_root: Path = PROJECT_ROOT
) -> tuple[TaskSpec, ...]:
    """Compile every packaged worksheet fixture."""

    return compile_task_files(iter_fixture_paths(fixture_dir), project_root=project_root)
