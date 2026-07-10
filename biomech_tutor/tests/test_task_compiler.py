"""Tests for task compiler validation."""

from pathlib import Path
from textwrap import dedent

import pytest

from biomech_tutor.tasks.compiler import (
    PROJECT_ROOT,
    compile_all_fixture_tasks,
    compile_task_file,
    iter_fixture_paths,
)
from biomech_tutor.tasks.schema import REQUIRED_TASK_FIELDS, TaskValidationError


def test_all_packaged_fixtures_compile() -> None:
    specs = compile_all_fixture_tasks()
    fixture_paths = iter_fixture_paths()

    assert len(specs) == 8
    assert {spec.id for spec in specs} == {path.stem for path in fixture_paths}

    for spec in specs:
        if spec.id == "elbow_biceps_curl_2d":
            assert spec.status == "in_progress"
            assert spec.coverage_level == "executable"
        else:
            assert spec.status == "scaffold"
            assert spec.coverage_level == "worksheet_scaffold"
        assert spec.title
        assert spec.level == "introductory_physics"
        assert set(REQUIRED_TASK_FIELDS).issubset(spec.raw)
        assert Path(spec.source_worksheet).parts[0] == "Activities"
        assert spec.source_path(PROJECT_ROOT).is_file()
        assert spec.body_part_system.id
        assert spec.joint_axis.visible_to_student
        assert spec.rotation_convention.display_labels
        assert spec.assumptions.planar
        assert spec.force_inventory
        assert spec.student_actions
        assert spec.allowed_equations
        assert spec.missing_data_policy.default in {
            "executable",
            "requires_instructor_key",
            "requires_declared_geometry",
        }

        declared_force_ids = {force.id for force in spec.force_inventory}
        for action in spec.student_actions:
            assert set(action.related_forces).issubset(declared_force_ids)
        for equation in spec.allowed_equations:
            assert set(equation.uses_forces).issubset(declared_force_ids)

        if spec.assumptions.static:
            torque_forces = [
                force
                for force in spec.force_inventory
                if force.required_for_torque_balance
                and force.kind != "direct_muscle_torque"
            ]
            assert torque_forces
            for force in torque_forces:
                assert force.student_must_draw_lever_arm
                assert force.student_must_identify_torque_direction


def test_compile_task_rejects_missing_required_field(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        _valid_fixture_text().replace(
            "coverage_level: worksheet_scaffold\n", ""
        ),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="coverage_level"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_id_filename_mismatch(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(_valid_fixture_text(task_id="different_task"), encoding="utf-8")

    with pytest.raises(TaskValidationError, match="id must match fixture"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_missing_source_worksheet(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(_valid_fixture_text(), encoding="utf-8")

    with pytest.raises(TaskValidationError, match="source worksheet does not exist"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_source_paths_outside_project(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        _valid_fixture_text(source_worksheet="../outside.pptx"), encoding="utf-8"
    )

    with pytest.raises(TaskValidationError, match="inside the repository"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_unknown_force_references(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        _valid_fixture_text(uses_forces="[external_force, missing_force]"),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="unknown force id"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_static_torque_force_without_lever_prompt(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        _valid_fixture_text(student_must_draw_lever_arm="false"),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="lever arm and torque-direction"):
        compile_task_file(fixture_path, project_root=tmp_path)


def _valid_fixture_text(
    *,
    task_id: str = "example_task",
    source_worksheet: str = "Activities/source.pptx",
    uses_forces: str = "[external_force, muscle_force]",
    student_must_draw_lever_arm: str = "true",
) -> str:
    return dedent(
        f"""
        id: {task_id}
        title: Example task
        status: scaffold
        coverage_level: worksheet_scaffold
        source_worksheet: "{source_worksheet}"
        level: introductory_physics
        body_part_system:
          id: example_segment
          display_name: Example segment
        joint_axis:
          id: example_axis
          joint: example_joint
          display_name: Example axis
          visible_to_student: true
        rotation_convention:
          positive: extension
          negative: flexion
          zero: zero torque
          display_labels: [extension, flexion, zero]
        assumptions:
          planar: true
          static: true
          rigid_segments: true
          ignored_forces: []
          simplifications: [held still]
        force_inventory:
          - id: external_force
            display_name: External force
            kind: external_load
            required_for_torque_balance: true
            required_for_force_balance: false
            student_must_draw_force: true
            student_must_draw_line_of_action: true
            student_must_draw_lever_arm: {student_must_draw_lever_arm}
            student_must_identify_torque_direction: true
            student_must_select_sign: true
            may_have_zero_torque: false
          - id: muscle_force
            display_name: Muscle force
            kind: muscle_force
            required_for_torque_balance: true
            required_for_force_balance: false
            student_must_draw_force: true
            student_must_draw_line_of_action: true
            student_must_draw_lever_arm: true
            student_must_identify_torque_direction: true
            student_must_select_sign: true
            may_have_zero_torque: false
        student_actions:
          - id: identify_torque
            prompt_type: torque_direction
            description: Identify torque direction.
            related_forces: [external_force]
            validation: requires_declared_geometry
        allowed_equations:
          - id: torque_balance
            display: "sum(tau) = 0"
            uses_forces: {uses_forces}
        missing_data_policy:
          default: requires_declared_geometry
          notes: [Example task must declare geometry.]
        """
    ).strip()
