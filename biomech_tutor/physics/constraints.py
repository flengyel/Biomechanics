"""Formal constraint inputs and raw evaluation evidence."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from biomech_tutor.core.frames import require_same_frame
from biomech_tutor.core.geometry import DEFAULT_TOLERANCE, Point2D, Vector2D
from biomech_tutor.core.signs import RotationConvention, Sign
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lever_arms import LeverArm2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D
from biomech_tutor.physics.torques import torque_sign_from_force


class ConstraintInputError(ValueError):
    """Raised when a formal constraint input is internally inconsistent."""


@dataclass(frozen=True)
class ForceTorqueUnitRequirement:
    """Compiled requirements for one force in a task inventory."""

    force_id: str
    display_name: str
    require_force: bool
    require_line_of_action: bool
    require_lever_arm: bool
    require_torque_direction: bool
    require_torque_sign: bool
    required_for_torque_balance: bool
    required_for_force_balance: bool
    may_have_zero_torque: bool = False

    def __post_init__(self) -> None:
        if not self.force_id.strip():
            raise ConstraintInputError("force requirement id must be non-empty")
        if not self.display_name.strip():
            raise ConstraintInputError(
                "force requirement display_name must be non-empty"
            )


@dataclass(frozen=True)
class LeverArmCandidate2D:
    """A learner-drawn lever arm that may or may not satisfy the geometry."""

    force_id: str
    pivot: Point2D
    vector: Vector2D

    def __post_init__(self) -> None:
        if not self.force_id.strip():
            raise ConstraintInputError("lever-arm force id must be non-empty")
        require_same_frame(self.pivot.frame, self.vector.frame)


@dataclass(frozen=True)
class ForceTorqueUnitCandidate2D:
    """Formal engine representation of one learner-constructed force unit."""

    force_id: str
    force: Force2D | None = None
    line_of_action: LineOfAction2D | None = None
    lever_arm: LeverArmCandidate2D | None = None
    claimed_torque_direction: str | None = None
    claimed_torque_sign: Sign | None = None
    equation_term_id: str | None = None

    def __post_init__(self) -> None:
        if not self.force_id.strip():
            raise ConstraintInputError("force candidate id must be non-empty")


@dataclass(frozen=True)
class ForceTorqueUnitCheck:
    """Raw constraint evidence for later diagnostic interpretation."""

    force_id: str
    force_present: bool
    line_of_action_present: bool
    line_of_action_matches_force: bool | None
    lever_arm_present: bool
    lever_arm_uses_force: bool | None
    lever_arm_uses_pivot: bool | None
    lever_arm_is_perpendicular: bool | None
    lever_arm_matches_geometry: bool | None
    torque_direction_matches: bool | None
    torque_sign_matches: bool | None

    @property
    def satisfies_requirements(self) -> bool:
        """Return whether every applicable raw check passed."""

        return all(
            value is not False
            for value in (
                self.force_present,
                self.line_of_action_present,
                self.line_of_action_matches_force,
                self.lever_arm_present,
                self.lever_arm_uses_force,
                self.lever_arm_uses_pivot,
                self.lever_arm_is_perpendicular,
                self.lever_arm_matches_geometry,
                self.torque_direction_matches,
                self.torque_sign_matches,
            )
        )


def check_force_torque_unit(
    requirement: ForceTorqueUnitRequirement,
    pivot: Point2D,
    rotation_convention: RotationConvention,
    candidate: ForceTorqueUnitCandidate2D | None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> ForceTorqueUnitCheck:
    """Evaluate a learner force unit without choosing pedagogical feedback."""

    if candidate is not None and candidate.force_id != requirement.force_id:
        raise ConstraintInputError(
            f"candidate force id '{candidate.force_id}' does not match "
            f"requirement '{requirement.force_id}'"
        )

    force = None if candidate is None else candidate.force
    line = None if candidate is None else candidate.line_of_action
    lever_arm = None if candidate is None else candidate.lever_arm

    force_present = force is not None or not requirement.require_force
    line_present = line is not None or not requirement.require_line_of_action
    lever_present = lever_arm is not None or not requirement.require_lever_arm

    line_matches_force = None
    if force is not None and line is not None:
        line_matches_force = _same_unoriented_line(
            force.line_of_action, line, tolerance
        )

    lever_uses_force = None
    lever_uses_pivot = None
    lever_is_perpendicular = None
    lever_matches_geometry = None
    if lever_arm is not None:
        lever_uses_force = lever_arm.force_id == requirement.force_id
        lever_uses_pivot = _same_point(lever_arm.pivot, pivot, tolerance)
        reference_line = line
        if reference_line is None and force is not None:
            reference_line = force.line_of_action
        if reference_line is not None:
            lever_is_perpendicular = lever_arm.vector.is_perpendicular_to(
                reference_line.direction, tolerance
            )
        if force is not None:
            expected = LeverArm2D(pivot, force.line_of_action).vector
            lever_matches_geometry = _same_vector(
                lever_arm.vector, expected, tolerance
            )

    torque_direction_matches = None
    torque_sign_matches = None
    if force is not None:
        expected_sign = torque_sign_from_force(pivot, force)
        if candidate is not None and candidate.claimed_torque_direction is not None:
            torque_direction_matches = (
                candidate.claimed_torque_direction
                == rotation_convention.label_for(expected_sign)
            )
        elif requirement.require_torque_direction:
            torque_direction_matches = False

        if candidate is not None and candidate.claimed_torque_sign is not None:
            torque_sign_matches = candidate.claimed_torque_sign is expected_sign
        elif requirement.require_torque_sign:
            torque_sign_matches = False

    return ForceTorqueUnitCheck(
        force_id=requirement.force_id,
        force_present=force_present,
        line_of_action_present=line_present,
        line_of_action_matches_force=line_matches_force,
        lever_arm_present=lever_present,
        lever_arm_uses_force=lever_uses_force,
        lever_arm_uses_pivot=lever_uses_pivot,
        lever_arm_is_perpendicular=lever_is_perpendicular,
        lever_arm_matches_geometry=lever_matches_geometry,
        torque_direction_matches=torque_direction_matches,
        torque_sign_matches=torque_sign_matches,
    )


def _same_point(left: Point2D, right: Point2D, tolerance: float) -> bool:
    require_same_frame(left.frame, right.frame)
    return isclose(left.x, right.x, abs_tol=tolerance) and isclose(
        left.y, right.y, abs_tol=tolerance
    )


def _same_vector(left: Vector2D, right: Vector2D, tolerance: float) -> bool:
    require_same_frame(left.frame, right.frame)
    return isclose(left.x, right.x, abs_tol=tolerance) and isclose(
        left.y, right.y, abs_tol=tolerance
    )


def _same_unoriented_line(
    left: LineOfAction2D, right: LineOfAction2D, tolerance: float
) -> bool:
    require_same_frame(left.frame, right.frame)
    directions_are_parallel = isclose(
        left.unit_direction.cross_z(right.unit_direction),
        0.0,
        abs_tol=tolerance,
    )
    return (
        directions_are_parallel
        and left.contains_point(right.point, tolerance)
        and right.contains_point(left.point, tolerance)
    )
