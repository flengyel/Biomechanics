"""Student-facing course-language diagnostic messages."""

from __future__ import annotations

from typing import Mapping

from biomech_tutor.diagnostics.failures import ConstraintFailure


MESSAGE_CATALOG: Mapping[str, Mapping[str, str]] = {
    "task_mismatch": {
        "default": "This work belongs to a different task. Reopen the current activity before continuing."
    },
    "wrong_body_part_system": {
        "default": "Analyze the forearm and hand as the selected body part for this task."
    },
    "wrong_joint_axis": {
        "default": "Use the elbow as the joint axis for the forearm/hand torque diagram."
    },
    "missing_required_force": {
        "default": "Add the {force_name} to the forearm/hand diagram."
    },
    "missing_line_of_action": {
        "default": "Draw the line of action for the {force_name}."
    },
    "wrong_line_of_action": {
        "default": "The line of action must follow the direction of the {force_name}."
    },
    "missing_lever_arm": {
        "default": "Draw a lever arm from the elbow to the {force_name}'s line of action."
    },
    "lever_arm_wrong_force": {
        "default": "Associate this lever arm with the {force_name}."
    },
    "lever_arm_wrong_pivot": {
        "default": "Draw the {force_name} lever arm from the elbow joint axis."
    },
    "lever_arm_not_perpendicular": {
        "default": "The lever arm for the {force_name} must be perpendicular to its line of action."
    },
    "lever_arm_wrong_length": {
        "default": "Use the shortest distance from the elbow to the {force_name}'s line of action."
    },
    "wrong_torque_direction": {
        "default": "Recheck whether the {force_name} causes flexion or extension about the elbow."
    },
    "wrong_torque_sign": {
        "default": "Match the sign of the {force_name} torque to the task's flexion/extension convention."
    },
    "wrong_counter_torque_muscle": {
        "default": "Choose the muscle whose pull produces torque opposite the dumbbell torque."
    },
    "wrong_muscle_attachment": {
        "default": "Place the selected muscle force at its forearm attachment."
    },
    "wrong_muscle_force_direction": {
        "default": "A muscle pulls its insertion toward its origin. Redraw the selected muscle force in that direction."
    },
}


def message_for_failure(
    failure: ConstraintFailure,
    *,
    level: str = "introductory_physics",
    overrides: Mapping[str, str] | None = None,
) -> str:
    """Render one failure using level or instructor-supplied wording."""

    if overrides is not None and failure.message_key in overrides:
        template = overrides[failure.message_key]
    else:
        variants = MESSAGE_CATALOG.get(failure.message_key)
        if variants is None:
            raise KeyError(
                f"no student message registered for '{failure.message_key}'"
            )
        template = variants.get(level, variants["default"])
    return template.format_map(failure.formal_details)
