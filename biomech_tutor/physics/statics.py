"""Static equilibrium checks."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import isclose

from biomech_tutor.core.frames import FrameError, require_same_frame
from biomech_tutor.core.geometry import DEFAULT_TOLERANCE, Point2D, Vector2D
from biomech_tutor.core.quantities import Torque2D
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.torques import torque_z_from_force


class StaticEquilibriumError(ValueError):
    """Raised when a static-equilibrium helper receives invalid input."""


@dataclass(frozen=True)
class ForceBalanceResult:
    """Residual for a force-equilibrium check."""

    residual: Vector2D
    tolerance: float = DEFAULT_TOLERANCE

    @property
    def is_balanced(self) -> bool:
        return (
            isclose(self.residual.x, 0.0, abs_tol=self.tolerance)
            and isclose(self.residual.y, 0.0, abs_tol=self.tolerance)
        )

    @property
    def required_balancing_vector(self) -> Vector2D:
        return self.residual.scale(-1.0)


@dataclass(frozen=True)
class TorqueBalanceResult:
    """Residual for a torque-equilibrium check about a pivot."""

    residual: Torque2D
    tolerance: float = DEFAULT_TOLERANCE

    @property
    def is_balanced(self) -> bool:
        return isclose(self.residual.z, 0.0, abs_tol=self.tolerance)

    @property
    def required_balancing_torque(self) -> Torque2D:
        return Torque2D(self.residual.frame, -self.residual.z, self.residual.unit)


@dataclass(frozen=True)
class StaticEquilibriumResult:
    """Force and torque residuals for a static body diagram."""

    force_balance: ForceBalanceResult
    torque_balance: TorqueBalanceResult

    @property
    def is_balanced(self) -> bool:
        return self.force_balance.is_balanced and self.torque_balance.is_balanced


def sum_force_vectors(vectors: Iterable[Vector2D]) -> Vector2D:
    """Sum force vectors after enforcing a common frame."""

    vector_tuple = tuple(vectors)
    if not vector_tuple:
        raise StaticEquilibriumError("at least one force vector is required")

    frame = vector_tuple[0].frame
    total = Vector2D(frame, 0.0, 0.0)
    for vector in vector_tuple:
        require_same_frame(frame, vector.frame)
        total = total + vector
    return total


def sum_forces(forces: Iterable[Force2D]) -> Vector2D:
    """Return the net force vector for a collection of forces."""

    force_tuple = tuple(forces)
    if not force_tuple:
        raise StaticEquilibriumError("at least one force is required")
    return sum_force_vectors(force.vector for force in force_tuple)


def force_balance(forces: Iterable[Force2D]) -> ForceBalanceResult:
    """Return the force-equilibrium residual."""

    return ForceBalanceResult(sum_forces(forces))


def required_balancing_force_vector(forces: Iterable[Force2D]) -> Vector2D:
    """Return the vector that would make the supplied forces sum to zero."""

    return force_balance(forces).required_balancing_vector


def sum_torques_about_point(pivot: Point2D, forces: Iterable[Force2D]) -> Torque2D:
    """Return the net torque about a pivot from all forces."""

    force_tuple = tuple(forces)
    total = 0.0
    for force in force_tuple:
        try:
            require_same_frame(pivot.frame, force.frame)
        except FrameError:
            raise
        total += torque_z_from_force(pivot, force)
    return Torque2D(pivot.frame, total)


def torque_balance_about_point(
    pivot: Point2D, forces: Iterable[Force2D]
) -> TorqueBalanceResult:
    """Return the torque-equilibrium residual about a pivot."""

    return TorqueBalanceResult(sum_torques_about_point(pivot, forces))


def required_balancing_torque_about_point(
    pivot: Point2D, forces: Iterable[Force2D]
) -> Torque2D:
    """Return the torque that would make the supplied torques sum to zero."""

    return torque_balance_about_point(pivot, forces).required_balancing_torque


def static_equilibrium_about_point(
    pivot: Point2D, forces: Iterable[Force2D]
) -> StaticEquilibriumResult:
    """Return force and torque residuals for a static body diagram."""

    force_tuple = tuple(forces)
    return StaticEquilibriumResult(
        force_balance=force_balance(force_tuple),
        torque_balance=torque_balance_about_point(pivot, force_tuple),
    )


def force_magnitude_for_torque_balance(
    external_force_magnitude: float,
    external_lever_arm: float,
    muscle_lever_arm: float,
    tolerance: float = DEFAULT_TOLERANCE,
) -> float:
    """Return M from M*r_M = F_external*r_external using magnitudes."""

    if external_force_magnitude < 0.0:
        raise StaticEquilibriumError("external force magnitude must be non-negative")
    if external_lever_arm < 0.0:
        raise StaticEquilibriumError("external lever arm must be non-negative")
    if muscle_lever_arm < 0.0 or isclose(
        muscle_lever_arm, 0.0, abs_tol=tolerance
    ):
        raise StaticEquilibriumError("muscle lever arm must be positive")
    return external_force_magnitude * external_lever_arm / muscle_lever_arm
