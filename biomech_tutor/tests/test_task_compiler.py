"""Tests for task compiler validation."""

from pathlib import Path

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
        assert spec.status == "scaffold"
        assert spec.coverage_level == "metadata_only"
        assert set(REQUIRED_TASK_FIELDS).issubset(spec.raw)
        assert Path(spec.source_worksheet).parts[0] == "Activities"
        assert spec.source_path(PROJECT_ROOT).is_file()


def test_compile_task_rejects_missing_required_field(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        "\n".join(
            [
                "id: example_task",
                "status: scaffold",
                'source_worksheet: "Activities/source.pptx"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="coverage_level"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_id_filename_mismatch(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        "\n".join(
            [
                "id: different_task",
                "status: scaffold",
                "coverage_level: metadata_only",
                'source_worksheet: "Activities/source.pptx"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="id must match fixture"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_missing_source_worksheet(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        "\n".join(
            [
                "id: example_task",
                "status: scaffold",
                "coverage_level: metadata_only",
                'source_worksheet: "Activities/missing.pptx"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="source worksheet does not exist"):
        compile_task_file(fixture_path, project_root=tmp_path)


def test_compile_task_rejects_source_paths_outside_project(tmp_path: Path) -> None:
    fixture_path = tmp_path / "example_task.yaml"
    fixture_path.write_text(
        "\n".join(
            [
                "id: example_task",
                "status: scaffold",
                "coverage_level: metadata_only",
                'source_worksheet: "../outside.pptx"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(TaskValidationError, match="inside the repository"):
        compile_task_file(fixture_path, project_root=tmp_path)
