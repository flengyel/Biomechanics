"""Instructor-authored task schema definitions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any


REQUIRED_TASK_FIELDS = ("id", "status", "source_worksheet", "coverage_level")


class TaskValidationError(ValueError):
    """Raised when an instructor-authored task file is structurally invalid."""


@dataclass(frozen=True)
class TaskSpec:
    """Validated metadata for an instructor-authored task fixture."""

    id: str
    status: str
    source_worksheet: str
    coverage_level: str
    fixture_path: Path | None = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "TaskSpec":
        if not isinstance(data, Mapping):
            source = _display_path(fixture_path)
            raise TaskValidationError(f"{source} must contain a YAML mapping")

        values = {
            field_name: _required_text(data, field_name, fixture_path)
            for field_name in REQUIRED_TASK_FIELDS
        }

        spec = cls(
            id=values["id"],
            status=values["status"],
            source_worksheet=values["source_worksheet"],
            coverage_level=values["coverage_level"],
            fixture_path=fixture_path,
            raw=MappingProxyType(dict(data)),
        )
        spec._validate_fixture_identity()
        return spec

    def source_path(self, project_root: Path) -> Path:
        """Return the repository-local source worksheet path."""

        source = Path(self.source_worksheet)
        if source.is_absolute():
            raise TaskValidationError(
                f"{self.id}: source_worksheet must be repository-relative"
            )

        root = project_root.resolve()
        resolved = (root / source).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise TaskValidationError(
                f"{self.id}: source_worksheet must stay inside the repository"
            ) from exc
        return resolved

    def _validate_fixture_identity(self) -> None:
        if self.fixture_path is None:
            return

        expected = self.fixture_path.stem
        if self.id != expected:
            raise TaskValidationError(
                f"{_display_path(self.fixture_path)} id must match fixture "
                f"filename stem '{expected}'"
            )


def _required_text(
    data: Mapping[str, Any], field_name: str, fixture_path: Path | None
) -> str:
    if field_name not in data:
        raise TaskValidationError(
            f"{_display_path(fixture_path)} missing required field '{field_name}'"
        )

    value = data[field_name]
    if not isinstance(value, str) or not value.strip():
        raise TaskValidationError(
            f"{_display_path(fixture_path)} field '{field_name}' must be "
            "a non-empty string"
        )
    return value.strip()


def _display_path(path: Path | None) -> str:
    return str(path) if path is not None else "task fixture"
