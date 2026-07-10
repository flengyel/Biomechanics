"""Executable text path for the elbow biceps curl task."""

from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.diagnostics import diagnose_biceps_curl, feedback_for_report
from biomech_tutor.learner import LearnerDiagram2D
from biomech_tutor.physics import (
    Force2D,
    ForceTorqueUnitCandidate2D,
    LeverArm2D,
    LeverArmCandidate2D,
    torque_sign_from_force,
)
from biomech_tutor.tasks import compile_biceps_curl_task


def _complete_unit(task, force_id: str, force: Force2D) -> ForceTorqueUnitCandidate2D:
    torque_sign = torque_sign_from_force(task.pivot, force)
    lever = LeverArm2D(task.pivot, force.line_of_action)
    return ForceTorqueUnitCandidate2D(
        force_id=force_id,
        force=force,
        line_of_action=force.line_of_action,
        lever_arm=LeverArmCandidate2D(force_id, task.pivot, lever.vector),
        claimed_torque_direction=task.rotation_convention.label_for(torque_sign),
        claimed_torque_sign=torque_sign,
    )


def main() -> None:
    task = compile_biceps_curl_task()
    frame = task.pivot.frame

    # These are explicit demonstration inputs, not values inferred from the slide.
    dumbbell = Force2D(
        Point2D(frame, 0.30, 0.0),
        Vector2D(frame, 0.0, -10.0),
    )
    counter_muscles = task.counter_torque_muscle_ids(dumbbell)
    muscle_id = counter_muscles[0]
    muscle_tension = task.required_muscle_tension(dumbbell, muscle_id)
    muscle_force = task.muscle_force(muscle_id, muscle_tension)
    joint_force = task.required_joint_force(dumbbell, muscle_force)

    diagram = LearnerDiagram2D(
        task_id=task.spec.id,
        body_part_system_id=task.spec.body_part_system.id,
        joint_axis_id=task.spec.joint_axis.id,
        force_torque_units=(
            _complete_unit(task, "dumbbell_force", dumbbell),
            _complete_unit(task, "biceps_muscle_force", muscle_force),
        ),
        counter_torque_muscle_id=muscle_id,
    )
    evaluation = task.evaluate(diagram)
    feedback = feedback_for_report(diagnose_biceps_curl(evaluation))

    print(f"Task: {task.spec.title}")
    print("Declared example: 10 force units downward at 0.30 length units")
    print(f"Geometry-selected counter-torque muscle: {muscle_id}")
    print(f"Required muscle tension: {muscle_tension:.3f} force units")
    print(
        "Required elbow joint force: "
        f"({joint_force.vector.x:.3f}, {joint_force.vector.y:.3f})"
    )
    print(f"Current executable construction passes: {evaluation.satisfies_current_slice}")
    print(
        "Diagnostic: no blocking errors"
        if feedback is None
        else f"Diagnostic: {feedback.message}"
    )


if __name__ == "__main__":
    main()
