"""Tests for diagnostic ordering and feedback mapping."""

from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.signs import Sign
from biomech_tutor.diagnostics import (
    FailureType,
    diagnose_biceps_curl,
    feedback_for_report,
)
from biomech_tutor.diagnostics.failures import DIAGNOSTIC_PRIORITY
from biomech_tutor.learner import LearnerDiagram2D
from biomech_tutor.physics import (
    Force2D,
    ForceTorqueUnitCandidate2D,
    LeverArm2D,
    LeverArmCandidate2D,
    torque_sign_from_force,
)
from biomech_tutor.tasks import compile_biceps_curl_task


def test_diagnostic_priority_covers_every_failure_type_once() -> None:
    assert len(DIAGNOSTIC_PRIORITY) == len(FailureType)
    assert set(DIAGNOSTIC_PRIORITY) == set(FailureType)


def test_wrong_joint_axis_is_first_blocking_feedback() -> None:
    task = compile_biceps_curl_task()
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id="shoulder_axis",
        force_torque_units=(),
    )

    report = diagnose_biceps_curl(task.evaluate(diagram))
    feedback = feedback_for_report(report, hint_step=0)

    assert report.failure_types[:2] == (
        FailureType.WRONG_JOINT_AXIS,
        FailureType.MISSING_REQUIRED_FORCE,
    )
    assert feedback is not None
    assert feedback.failure_type is FailureType.WRONG_JOINT_AXIS
    assert "elbow" in feedback.message.lower()
    assert feedback.hint is not None
    assert feedback.suppressed_failure_count == len(report.failures) - 1


def test_missing_dumbbell_force_is_reported_before_its_downstream_parts() -> None:
    task = compile_biceps_curl_task()
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id=task.spec.joint_axis.id,
        force_torque_units=(),
    )

    report = diagnose_biceps_curl(task.evaluate(diagram))
    feedback = feedback_for_report(report)

    assert report.primary_failure is not None
    assert report.primary_failure.failure_type is FailureType.MISSING_REQUIRED_FORCE
    assert FailureType.MISSING_LEVER_ARM in report.failure_types
    assert feedback is not None
    assert feedback.failure_type is FailureType.MISSING_REQUIRED_FORCE
    assert "dumbbell force" in feedback.message.lower()


def test_nonperpendicular_lever_arm_suppresses_torque_feedback() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)
    bad_dumbbell_unit = ForceTorqueUnitCandidate2D(
        force_id="dumbbell_force",
        force=dumbbell,
        line_of_action=dumbbell.line_of_action,
        lever_arm=LeverArmCandidate2D(
            "dumbbell_force",
            task.pivot,
            Vector2D(task.pivot.frame, 0.0, 0.30),
        ),
        claimed_torque_direction="flexion",
        claimed_torque_sign=Sign.POSITIVE,
    )
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id=task.spec.joint_axis.id,
        force_torque_units=(bad_dumbbell_unit,),
    )

    report = diagnose_biceps_curl(task.evaluate(diagram))
    feedback = feedback_for_report(report)

    assert FailureType.LEVER_ARM_NOT_PERPENDICULAR in report.failure_types
    assert FailureType.LEVER_ARM_WRONG_LENGTH in report.failure_types
    assert FailureType.WRONG_TORQUE_DIRECTION in report.failure_types
    assert report.primary_failure is not None
    assert (
        FailureType.LEVER_ARM_WRONG_LENGTH
        in report.primary_failure.downstream_failures
    )
    assert feedback is not None
    assert feedback.failure_type is FailureType.LEVER_ARM_NOT_PERPENDICULAR
    assert "perpendicular" in feedback.message.lower()
    assert "torque direction" not in feedback.message.lower()


def test_wrong_counter_torque_muscle_blocks_muscle_geometry_feedback() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)
    triceps_force = task.muscle_force("triceps", 20.0)
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id=task.spec.joint_axis.id,
        force_torque_units=(
            _complete_unit(task, "dumbbell_force", dumbbell),
            _complete_unit(task, "triceps_muscle_force", triceps_force),
        ),
        counter_torque_muscle_id="triceps",
    )

    report = diagnose_biceps_curl(task.evaluate(diagram))
    feedback = feedback_for_report(report)

    assert report.failure_types == (FailureType.WRONG_COUNTER_TORQUE_MUSCLE,)
    assert feedback is not None
    assert feedback.failure_type is FailureType.WRONG_COUNTER_TORQUE_MUSCLE
    assert "opposite" in feedback.message.lower()


def test_wrong_muscle_direction_uses_anatomy_evidence() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)
    wrong_muscle_force = Force2D(
        task.anatomy.biceps.insertion_region.center,
        Vector2D(task.pivot.frame, 0.0, -20.0),
    )
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id=task.spec.joint_axis.id,
        force_torque_units=(
            _complete_unit(task, "dumbbell_force", dumbbell),
            _complete_unit(
                task,
                "biceps_muscle_force",
                wrong_muscle_force,
            ),
        ),
        counter_torque_muscle_id="biceps",
    )

    report = diagnose_biceps_curl(task.evaluate(diagram))
    feedback = feedback_for_report(report)

    assert report.primary_failure is not None
    assert report.primary_failure.failure_type is FailureType.WRONG_FORCE_DIRECTION
    assert feedback is not None
    assert "pulls" in feedback.message.lower()


def test_correct_biceps_construction_has_no_feedback() -> None:
    task = compile_biceps_curl_task()
    dumbbell = _dumbbell_force(task)
    tension = task.required_muscle_tension(dumbbell, "biceps")
    muscle_force = task.muscle_force("biceps", tension)
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id=task.spec.joint_axis.id,
        force_torque_units=(
            _complete_unit(task, "dumbbell_force", dumbbell),
            _complete_unit(task, "biceps_muscle_force", muscle_force),
        ),
        counter_torque_muscle_id="biceps",
    )

    report = diagnose_biceps_curl(task.evaluate(diagram))

    assert report.is_correct
    assert feedback_for_report(report) is None


def test_visibility_policy_and_instructor_wording_override_are_outer_controls() -> None:
    task = compile_biceps_curl_task()
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id="shoulder_axis",
        force_torque_units=(),
    )
    report = diagnose_biceps_curl(task.evaluate(diagram))

    feedback = feedback_for_report(
        report,
        visible_failure_types={FailureType.MISSING_REQUIRED_FORCE},
        message_overrides={
            "missing_required_force": "Worksheet reminder: add the {force_name}."
        },
    )

    assert feedback is not None
    assert feedback.failure_type is FailureType.MISSING_REQUIRED_FORCE
    assert feedback.message == "Worksheet reminder: add the dumbbell force."


def test_student_feedback_does_not_expose_formal_engine_vocabulary() -> None:
    task = compile_biceps_curl_task()
    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id="shoulder_axis",
        force_torque_units=(),
    )

    feedback = feedback_for_report(
        diagnose_biceps_curl(task.evaluate(diagram))
    )

    assert feedback is not None
    forbidden_terms = (
        "framegroupoid",
        "transportarrow",
        "wrenchnaturality",
        "fiber",
        "constraintfailure",
    )
    assert all(term not in feedback.message.lower() for term in forbidden_terms)


def _dumbbell_force(task) -> Force2D:
    return Force2D(
        Point2D(task.pivot.frame, 0.30, 0.0),
        Vector2D(task.pivot.frame, 0.0, -10.0),
    )


def _complete_unit(task, force_id: str, force: Force2D) -> ForceTorqueUnitCandidate2D:
    sign = torque_sign_from_force(task.pivot, force)
    lever = LeverArm2D(task.pivot, force.line_of_action)
    return ForceTorqueUnitCandidate2D(
        force_id=force_id,
        force=force,
        line_of_action=force.line_of_action,
        lever_arm=LeverArmCandidate2D(force_id, task.pivot, lever.vector),
        claimed_torque_direction=task.rotation_convention.label_for(sign),
        claimed_torque_sign=sign,
    )
