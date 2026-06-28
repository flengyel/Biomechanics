"""Torque calculations."""

from __future__ import annotations

from biomech_tutor.core.frames import require_same_frame
from biomech_tutor.core.geometry import Point2D, Vector2D
from biomech_tutor.core.signs import Sign, sign_of
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lines_of_action import LineOfAction2D


def torque_z_about_point(
    pivot: Point2D, application_point: Point2D, force: Vector2D
) -> float:
    """Return the 2D z-component of torque from r x F."""

    require_same_frame(pivot.frame, application_point.frame)
    require_same_frame(pivot.frame, force.frame)
    radius = pivot.vector_to(application_point)
    return radius.cross_z(force)


def torque_sign_about_point(
    pivot: Point2D, application_point: Point2D, force: Vector2D
) -> Sign:
    return sign_of(torque_z_about_point(pivot, application_point, force))


def torque_z_from_force(pivot: Point2D, force: Force2D) -> float:
    return torque_z_about_point(pivot, force.application_point, force.vector)


def torque_sign_from_force(pivot: Point2D, force: Force2D) -> Sign:
    return sign_of(torque_z_from_force(pivot, force))


def torque_z_from_line_of_action(
    pivot: Point2D, line_of_action: LineOfAction2D, force_magnitude: float = 1.0
) -> float:
    """Return torque using any point on the force line of action."""

    direction = line_of_action.unit_direction.scale(force_magnitude)
    return torque_z_about_point(pivot, line_of_action.point, direction)


def torque_sign_from_line_of_action(
    pivot: Point2D, line_of_action: LineOfAction2D, force_magnitude: float = 1.0
) -> Sign:
    return sign_of(
        torque_z_from_line_of_action(
            pivot,
            line_of_action,
            force_magnitude=force_magnitude,
        )
    )
