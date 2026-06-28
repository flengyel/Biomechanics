"""Physics operations for forces, torques, and constraints."""

from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lever_arms import LeverArm2D, lever_arm_for_line
from biomech_tutor.physics.lines_of_action import LineOfAction2D
from biomech_tutor.physics.statics import (
    ForceBalanceResult,
    StaticEquilibriumError,
    StaticEquilibriumResult,
    TorqueBalanceResult,
    force_balance,
    force_magnitude_for_torque_balance,
    required_balancing_force_vector,
    required_balancing_torque_about_point,
    static_equilibrium_about_point,
    sum_force_vectors,
    sum_forces,
    sum_torques_about_point,
    torque_balance_about_point,
)
from biomech_tutor.physics.torques import (
    torque_sign_about_point,
    torque_sign_from_force,
    torque_sign_from_line_of_action,
    torque_z_about_point,
    torque_z_from_force,
    torque_z_from_line_of_action,
)
from biomech_tutor.physics.wrenches import Wrench2D

__all__ = [
    "Force2D",
    "LeverArm2D",
    "LineOfAction2D",
    "ForceBalanceResult",
    "StaticEquilibriumError",
    "StaticEquilibriumResult",
    "TorqueBalanceResult",
    "Wrench2D",
    "force_balance",
    "force_magnitude_for_torque_balance",
    "lever_arm_for_line",
    "required_balancing_force_vector",
    "required_balancing_torque_about_point",
    "static_equilibrium_about_point",
    "sum_force_vectors",
    "sum_forces",
    "sum_torques_about_point",
    "torque_balance_about_point",
    "torque_sign_about_point",
    "torque_sign_from_force",
    "torque_sign_from_line_of_action",
    "torque_z_about_point",
    "torque_z_from_force",
    "torque_z_from_line_of_action",
]
