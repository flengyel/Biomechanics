"""Ordered course-language hints for blocking failures."""

from __future__ import annotations

from typing import Mapping

from biomech_tutor.diagnostics.failures import ConstraintFailure


HINT_CATALOG: Mapping[str, tuple[str, ...]] = {
    "wrong_body_part_system": (
        "Isolate the body part named in the prompt before listing its forces.",
    ),
    "wrong_joint_axis": (
        "The pivot must be the joint connecting the forearm to the upper arm.",
    ),
    "missing_required_force": (
        "List every external object that pushes or pulls on the forearm/hand.",
    ),
    "missing_line_of_action": (
        "Extend the force arrow in both directions to identify its line of action.",
    ),
    "missing_lever_arm": (
        "Start at the elbow and find the shortest path to the force's line of action.",
    ),
    "lever_arm_not_perpendicular": (
        "A shortest distance to a line meets that line at a right angle.",
    ),
    "wrong_torque_direction": (
        "Imagine the force acting alone and decide which way the forearm would rotate.",
    ),
    "wrong_counter_torque_muscle": (
        "The balancing muscle must rotate the forearm opposite the dumbbell's tendency.",
    ),
    "wrong_muscle_attachment": (
        "Place the force where the selected muscle attaches to the forearm.",
    ),
    "wrong_muscle_force_direction": (
        "Muscle tension pulls the insertion toward the origin; it does not push.",
    ),
}


def hint_for_failure(
    failure: ConstraintFailure,
    step: int = 0,
) -> str | None:
    """Return one staged hint, or ``None`` when no hint is configured."""

    if step < 0:
        raise ValueError("hint step must be non-negative")
    hints = HINT_CATALOG.get(failure.message_key, ())
    if not hints:
        return None
    return hints[min(step, len(hints) - 1)]
