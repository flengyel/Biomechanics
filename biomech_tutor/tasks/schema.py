"""Instructor-authored task schema definitions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any


REQUIRED_TASK_FIELDS = (
    "id",
    "title",
    "status",
    "coverage_level",
    "source_worksheet",
    "level",
    "body_part_system",
    "joint_axis",
    "rotation_convention",
    "assumptions",
    "force_inventory",
    "student_actions",
    "allowed_equations",
    "missing_data_policy",
)

LEVEL_VALUES = {"introductory_physics", "intermediate", "advanced"}
COVERAGE_LEVEL_VALUES = {
    "metadata_only",
    "worksheet_scaffold",
    "diagnostic_scaffold",
    "executable",
}
FORCE_KIND_VALUES = {
    "external_load",
    "muscle_force",
    "joint_force",
    "contact_force",
    "weight",
    "direct_muscle_torque",
}
MISSING_DATA_POLICY_VALUES = {
    "executable",
    "requires_instructor_key",
    "requires_declared_geometry",
}


class TaskValidationError(ValueError):
    """Raised when an instructor-authored task file is structurally invalid."""


@dataclass(frozen=True)
class BodyPartSystemSpec:
    """Body-part system analyzed by a task."""

    id: str
    display_name: str

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "BodyPartSystemSpec":
        return cls(
            id=_required_text(data, "id", fixture_path),
            display_name=_required_text(data, "display_name", fixture_path),
        )


@dataclass(frozen=True)
class JointAxisSpec:
    """Joint axis used as the torque pivot."""

    id: str
    joint: str
    display_name: str
    visible_to_student: bool

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "JointAxisSpec":
        return cls(
            id=_required_text(data, "id", fixture_path),
            joint=_required_text(data, "joint", fixture_path),
            display_name=_required_text(data, "display_name", fixture_path),
            visible_to_student=_required_bool(data, "visible_to_student", fixture_path),
        )


@dataclass(frozen=True)
class RotationConventionSpec:
    """Task-specific sign labels for rotation and torque."""

    positive: str
    negative: str
    zero: str
    display_labels: tuple[str, ...]

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "RotationConventionSpec":
        display_labels = _required_text_sequence(data, "display_labels", fixture_path)
        return cls(
            positive=_required_text(data, "positive", fixture_path),
            negative=_required_text(data, "negative", fixture_path),
            zero=_required_text(data, "zero", fixture_path),
            display_labels=display_labels,
        )


@dataclass(frozen=True)
class AssumptionSpec:
    """Worksheet simplifications declared by an instructor."""

    planar: bool
    static: bool
    rigid_segments: bool
    ignored_forces: tuple[str, ...]
    simplifications: tuple[str, ...]

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "AssumptionSpec":
        return cls(
            planar=_required_bool(data, "planar", fixture_path),
            static=_required_bool(data, "static", fixture_path),
            rigid_segments=_required_bool(data, "rigid_segments", fixture_path),
            ignored_forces=_required_text_sequence(data, "ignored_forces", fixture_path),
            simplifications=_required_text_sequence(
                data, "simplifications", fixture_path
            ),
        )


@dataclass(frozen=True)
class ForceSpec:
    """Force or direct torque that appears in a worksheet task."""

    id: str
    display_name: str
    kind: str
    required_for_torque_balance: bool
    required_for_force_balance: bool
    student_must_draw_force: bool
    student_must_draw_line_of_action: bool
    student_must_draw_lever_arm: bool
    student_must_identify_torque_direction: bool
    student_must_select_sign: bool
    may_have_zero_torque: bool

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "ForceSpec":
        kind = _required_choice(data, "kind", FORCE_KIND_VALUES, fixture_path)
        return cls(
            id=_required_text(data, "id", fixture_path),
            display_name=_required_text(data, "display_name", fixture_path),
            kind=kind,
            required_for_torque_balance=_required_bool(
                data, "required_for_torque_balance", fixture_path
            ),
            required_for_force_balance=_required_bool(
                data, "required_for_force_balance", fixture_path
            ),
            student_must_draw_force=_required_bool(
                data, "student_must_draw_force", fixture_path
            ),
            student_must_draw_line_of_action=_required_bool(
                data, "student_must_draw_line_of_action", fixture_path
            ),
            student_must_draw_lever_arm=_required_bool(
                data, "student_must_draw_lever_arm", fixture_path
            ),
            student_must_identify_torque_direction=_required_bool(
                data, "student_must_identify_torque_direction", fixture_path
            ),
            student_must_select_sign=_required_bool(
                data, "student_must_select_sign", fixture_path
            ),
            may_have_zero_torque=_required_bool(
                data, "may_have_zero_torque", fixture_path
            ),
        )


@dataclass(frozen=True)
class StudentActionSpec:
    """Student-facing prompt or action expected by a worksheet."""

    id: str
    prompt_type: str
    description: str
    related_forces: tuple[str, ...]
    validation: str

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "StudentActionSpec":
        return cls(
            id=_required_text(data, "id", fixture_path),
            prompt_type=_required_text(data, "prompt_type", fixture_path),
            description=_required_text(data, "description", fixture_path),
            related_forces=_required_text_sequence(
                data, "related_forces", fixture_path
            ),
            validation=_required_choice(
                data, "validation", MISSING_DATA_POLICY_VALUES, fixture_path
            ),
        )


@dataclass(frozen=True)
class EquationSpec:
    """Allowed equation form under a task's declared assumptions."""

    id: str
    display: str
    uses_forces: tuple[str, ...]

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "EquationSpec":
        return cls(
            id=_required_text(data, "id", fixture_path),
            display=_required_text(data, "display", fixture_path),
            uses_forces=_required_text_sequence(data, "uses_forces", fixture_path),
        )


@dataclass(frozen=True)
class MissingDataPolicySpec:
    """How a task handles values not declared in the fixture."""

    default: str
    notes: tuple[str, ...]

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "MissingDataPolicySpec":
        return cls(
            default=_required_choice(
                data, "default", MISSING_DATA_POLICY_VALUES, fixture_path
            ),
            notes=_required_text_sequence(data, "notes", fixture_path),
        )


@dataclass(frozen=True)
class TaskSpec:
    """Validated metadata for an instructor-authored task fixture."""

    id: str
    title: str
    status: str
    coverage_level: str
    source_worksheet: str
    level: str
    body_part_system: BodyPartSystemSpec
    joint_axis: JointAxisSpec
    rotation_convention: RotationConventionSpec
    assumptions: AssumptionSpec
    force_inventory: tuple[ForceSpec, ...]
    student_actions: tuple[StudentActionSpec, ...]
    allowed_equations: tuple[EquationSpec, ...]
    missing_data_policy: MissingDataPolicySpec
    fixture_path: Path | None = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mapping(
        cls, data: Mapping[str, Any], fixture_path: Path | None = None
    ) -> "TaskSpec":
        if not isinstance(data, Mapping):
            source = _display_path(fixture_path)
            raise TaskValidationError(f"{source} must contain a YAML mapping")

        for field_name in REQUIRED_TASK_FIELDS:
            if field_name not in data:
                raise TaskValidationError(
                    f"{_display_path(fixture_path)} missing required field "
                    f"'{field_name}'"
                )

        spec = cls(
            id=_required_text(data, "id", fixture_path),
            title=_required_text(data, "title", fixture_path),
            status=_required_text(data, "status", fixture_path),
            coverage_level=_required_choice(
                data, "coverage_level", COVERAGE_LEVEL_VALUES, fixture_path
            ),
            source_worksheet=_required_text(data, "source_worksheet", fixture_path),
            level=_required_choice(data, "level", LEVEL_VALUES, fixture_path),
            body_part_system=BodyPartSystemSpec.from_mapping(
                _required_mapping(data, "body_part_system", fixture_path), fixture_path
            ),
            joint_axis=JointAxisSpec.from_mapping(
                _required_mapping(data, "joint_axis", fixture_path), fixture_path
            ),
            rotation_convention=RotationConventionSpec.from_mapping(
                _required_mapping(data, "rotation_convention", fixture_path),
                fixture_path,
            ),
            assumptions=AssumptionSpec.from_mapping(
                _required_mapping(data, "assumptions", fixture_path), fixture_path
            ),
            force_inventory=tuple(
                ForceSpec.from_mapping(item, fixture_path)
                for item in _required_mapping_sequence(
                    data, "force_inventory", fixture_path
                )
            ),
            student_actions=tuple(
                StudentActionSpec.from_mapping(item, fixture_path)
                for item in _required_mapping_sequence(
                    data, "student_actions", fixture_path
                )
            ),
            allowed_equations=tuple(
                EquationSpec.from_mapping(item, fixture_path)
                for item in _required_mapping_sequence(
                    data, "allowed_equations", fixture_path
                )
            ),
            missing_data_policy=MissingDataPolicySpec.from_mapping(
                _required_mapping(data, "missing_data_policy", fixture_path),
                fixture_path,
            ),
            fixture_path=fixture_path,
            raw=MappingProxyType(dict(data)),
        )
        spec._validate_fixture_identity()
        spec._validate_collections()
        spec._validate_force_references()
        spec._validate_static_torque_prompts()
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

    def _validate_collections(self) -> None:
        if not self.force_inventory:
            raise TaskValidationError(f"{self.id}: force_inventory must not be empty")
        if not self.student_actions:
            raise TaskValidationError(f"{self.id}: student_actions must not be empty")
        if not self.allowed_equations:
            raise TaskValidationError(f"{self.id}: allowed_equations must not be empty")

        _validate_unique_ids(self.id, "force_inventory", self.force_inventory)
        _validate_unique_ids(self.id, "student_actions", self.student_actions)
        _validate_unique_ids(self.id, "allowed_equations", self.allowed_equations)

    def _validate_force_references(self) -> None:
        declared_force_ids = {force.id for force in self.force_inventory}
        for action in self.student_actions:
            _validate_known_ids(
                self.id,
                f"student action '{action.id}' related_forces",
                action.related_forces,
                declared_force_ids,
            )
        for equation in self.allowed_equations:
            _validate_known_ids(
                self.id,
                f"equation '{equation.id}' uses_forces",
                equation.uses_forces,
                declared_force_ids,
            )

    def _validate_static_torque_prompts(self) -> None:
        if not self.assumptions.static:
            return

        for force in self.force_inventory:
            if (
                force.required_for_torque_balance
                and force.kind != "direct_muscle_torque"
                and (
                    not force.student_must_draw_lever_arm
                    or not force.student_must_identify_torque_direction
                )
            ):
                raise TaskValidationError(
                    f"{self.id}: static torque force '{force.id}' must require "
                    "a lever arm and torque-direction prompt"
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


def _required_choice(
    data: Mapping[str, Any],
    field_name: str,
    allowed_values: set[str],
    fixture_path: Path | None,
) -> str:
    value = _required_text(data, field_name, fixture_path)
    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise TaskValidationError(
            f"{_display_path(fixture_path)} field '{field_name}' must be one "
            f"of: {allowed}"
        )
    return value


def _required_bool(
    data: Mapping[str, Any], field_name: str, fixture_path: Path | None
) -> bool:
    if field_name not in data:
        raise TaskValidationError(
            f"{_display_path(fixture_path)} missing required field '{field_name}'"
        )

    value = data[field_name]
    if not isinstance(value, bool):
        raise TaskValidationError(
            f"{_display_path(fixture_path)} field '{field_name}' must be a boolean"
        )
    return value


def _required_mapping(
    data: Mapping[str, Any], field_name: str, fixture_path: Path | None
) -> Mapping[str, Any]:
    if field_name not in data:
        raise TaskValidationError(
            f"{_display_path(fixture_path)} missing required field '{field_name}'"
        )

    value = data[field_name]
    if not isinstance(value, Mapping):
        raise TaskValidationError(
            f"{_display_path(fixture_path)} field '{field_name}' must be a mapping"
        )
    return value


def _required_text_sequence(
    data: Mapping[str, Any], field_name: str, fixture_path: Path | None
) -> tuple[str, ...]:
    if field_name not in data:
        raise TaskValidationError(
            f"{_display_path(fixture_path)} missing required field '{field_name}'"
        )

    value = data[field_name]
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise TaskValidationError(
            f"{_display_path(fixture_path)} field '{field_name}' must be a list"
        )

    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise TaskValidationError(
                f"{_display_path(fixture_path)} field '{field_name}' must contain "
                "only non-empty strings"
            )
        items.append(item.strip())
    return tuple(items)


def _required_mapping_sequence(
    data: Mapping[str, Any], field_name: str, fixture_path: Path | None
) -> tuple[Mapping[str, Any], ...]:
    if field_name not in data:
        raise TaskValidationError(
            f"{_display_path(fixture_path)} missing required field '{field_name}'"
        )

    value = data[field_name]
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise TaskValidationError(
            f"{_display_path(fixture_path)} field '{field_name}' must be a list"
        )

    items: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise TaskValidationError(
                f"{_display_path(fixture_path)} field '{field_name}' must contain "
                "only mappings"
            )
        items.append(item)
    return tuple(items)


def _validate_unique_ids(
    task_id: str, collection_name: str, items: tuple[Any, ...]
) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = item.id
        if item_id in seen:
            raise TaskValidationError(
                f"{task_id}: duplicate id '{item_id}' in {collection_name}"
            )
        seen.add(item_id)


def _validate_known_ids(
    task_id: str,
    source_label: str,
    referenced_ids: tuple[str, ...],
    declared_ids: set[str],
) -> None:
    unknown_ids = sorted(set(referenced_ids) - declared_ids)
    if unknown_ids:
        unknown = ", ".join(unknown_ids)
        raise TaskValidationError(
            f"{task_id}: {source_label} references unknown force id(s): {unknown}"
        )


def _display_path(path: Path | None) -> str:
    return str(path) if path is not None else "task fixture"
