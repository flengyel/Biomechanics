"""Structured diagnostic failures and task-specific evidence translation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from types import MappingProxyType
from typing import Iterable, Mapping

from biomech_tutor.physics.constraints import ForceTorqueUnitCheck
from biomech_tutor.tasks.biceps_curl import BicepsCurlEvaluation


class FailureType(Enum):
    """Stable diagnostic categories shared by tasks and feedback adapters."""

    TASK_UNSOLVABLE = auto()
    MISSING_BODY_PART_SYSTEM = auto()
    WRONG_BODY_PART_SYSTEM = auto()
    MISSING_JOINT_AXIS = auto()
    WRONG_JOINT_AXIS = auto()
    MISSING_REQUIRED_FORCE = auto()
    EXTRA_IRRELEVANT_FORCE = auto()
    INVALID_ATTACHMENT_REGION = auto()
    WRONG_MUSCLE_ATTACHMENT = auto()
    WRONG_FORCE_APPLICATION_POINT = auto()
    WRONG_FORCE_DIRECTION = auto()
    MISSING_LINE_OF_ACTION = auto()
    WRONG_LINE_OF_ACTION = auto()
    MISSING_LEVER_ARM = auto()
    LEVER_ARM_WRONG_FORCE = auto()
    LEVER_ARM_WRONG_PIVOT = auto()
    LEVER_ARM_NOT_PERPENDICULAR = auto()
    LEVER_ARM_WRONG_LENGTH = auto()
    WRONG_TORQUE_DIRECTION = auto()
    WRONG_TORQUE_SIGN = auto()
    WRONG_NET_TORQUE_DIRECTION = auto()
    WRONG_COUNTER_TORQUE_MUSCLE = auto()
    MISSING_TORQUE_TERM = auto()
    EXTRA_TORQUE_TERM = auto()
    EQUATION_NOT_EQUIVALENT = auto()
    WRONG_EQUATION_SIGN = auto()
    WRONG_FORCE_BALANCE_TERM = auto()
    WRONG_JOINT_FORCE_DIRECTION = auto()
    WRONG_JOINT_FORCE_MAGNITUDE = auto()
    WRONG_BODY_WEIGHT_SCALING = auto()
    NUMERIC_ERROR = auto()
    UNIT_ERROR = auto()
    WRONG_ANGULAR_VELOCITY_SIGN = auto()
    WRONG_ANGULAR_ACCELERATION_SIGN = auto()
    WRONG_TORQUE_ALPHA_RELATION = auto()
    WRONG_MUSCLE_DOMINANCE = auto()
    WRONG_SPEED_UP_SLOW_DOWN_CLASSIFICATION = auto()
    WRONG_CONCENTRIC_ECCENTRIC_CLASSIFICATION = auto()
    FRAME_TYPE_ERROR = auto()
    INTERNAL_CONSTRAINT_ERROR = auto()


class FailureSeverity(str, Enum):
    """Whether a failure blocks grading of downstream work."""

    BLOCKING = "blocking"
    NON_BLOCKING = "non_blocking"


@dataclass(frozen=True)
class ConstraintFailure:
    """Formal failure data with no student-facing prose."""

    failure_type: FailureType
    severity: FailureSeverity
    message_key: str
    formal_details: Mapping[str, object]
    downstream_failures: tuple[FailureType, ...] = ()

    def __post_init__(self) -> None:
        if not self.message_key.strip():
            raise ValueError("diagnostic message_key must be non-empty")
        object.__setattr__(
            self,
            "formal_details",
            MappingProxyType(dict(self.formal_details)),
        )
        object.__setattr__(
            self,
            "downstream_failures",
            tuple(self.downstream_failures),
        )


@dataclass(frozen=True)
class DiagnosticReport:
    """Ordered failure stack for one task evaluation."""

    failures: tuple[ConstraintFailure, ...]

    @property
    def is_correct(self) -> bool:
        return not self.failures

    @property
    def primary_failure(self) -> ConstraintFailure | None:
        return next(
            (
                failure
                for failure in self.failures
                if failure.severity is FailureSeverity.BLOCKING
            ),
            None,
        )

    @property
    def failure_types(self) -> tuple[FailureType, ...]:
        return tuple(failure.failure_type for failure in self.failures)


DIAGNOSTIC_PRIORITY = (
    FailureType.TASK_UNSOLVABLE,
    FailureType.MISSING_BODY_PART_SYSTEM,
    FailureType.WRONG_BODY_PART_SYSTEM,
    FailureType.MISSING_JOINT_AXIS,
    FailureType.WRONG_JOINT_AXIS,
    FailureType.MISSING_REQUIRED_FORCE,
    FailureType.EXTRA_IRRELEVANT_FORCE,
    FailureType.WRONG_FORCE_APPLICATION_POINT,
    FailureType.WRONG_FORCE_DIRECTION,
    FailureType.MISSING_LINE_OF_ACTION,
    FailureType.WRONG_LINE_OF_ACTION,
    FailureType.MISSING_LEVER_ARM,
    FailureType.LEVER_ARM_WRONG_FORCE,
    FailureType.LEVER_ARM_WRONG_PIVOT,
    FailureType.LEVER_ARM_NOT_PERPENDICULAR,
    FailureType.LEVER_ARM_WRONG_LENGTH,
    FailureType.WRONG_TORQUE_DIRECTION,
    FailureType.WRONG_TORQUE_SIGN,
    FailureType.WRONG_COUNTER_TORQUE_MUSCLE,
    FailureType.INVALID_ATTACHMENT_REGION,
    FailureType.WRONG_MUSCLE_ATTACHMENT,
    FailureType.MISSING_TORQUE_TERM,
    FailureType.EXTRA_TORQUE_TERM,
    FailureType.EQUATION_NOT_EQUIVALENT,
    FailureType.WRONG_EQUATION_SIGN,
    FailureType.WRONG_FORCE_BALANCE_TERM,
    FailureType.WRONG_JOINT_FORCE_DIRECTION,
    FailureType.WRONG_JOINT_FORCE_MAGNITUDE,
    FailureType.WRONG_BODY_WEIGHT_SCALING,
    FailureType.NUMERIC_ERROR,
    FailureType.UNIT_ERROR,
    FailureType.WRONG_ANGULAR_VELOCITY_SIGN,
    FailureType.WRONG_ANGULAR_ACCELERATION_SIGN,
    FailureType.WRONG_NET_TORQUE_DIRECTION,
    FailureType.WRONG_TORQUE_ALPHA_RELATION,
    FailureType.WRONG_MUSCLE_DOMINANCE,
    FailureType.WRONG_SPEED_UP_SLOW_DOWN_CLASSIFICATION,
    FailureType.WRONG_CONCENTRIC_ECCENTRIC_CLASSIFICATION,
    FailureType.FRAME_TYPE_ERROR,
    FailureType.INTERNAL_CONSTRAINT_ERROR,
)

_PRIORITY_INDEX = {
    failure_type: index for index, failure_type in enumerate(DIAGNOSTIC_PRIORITY)
}


def diagnostic_report(
    failures: Iterable[ConstraintFailure],
) -> DiagnosticReport:
    """Return a deterministically ordered diagnostic report."""

    ordered = tuple(
        sorted(
            failures,
            key=lambda failure: _PRIORITY_INDEX[failure.failure_type],
        )
    )
    return DiagnosticReport(ordered)


def diagnose_biceps_curl(evaluation: BicepsCurlEvaluation) -> DiagnosticReport:
    """Translate biceps task evidence into a complete ordered failure stack."""

    failures: list[ConstraintFailure] = []
    if not evaluation.task_matches:
        failures.append(
            _failure(
                FailureType.TASK_UNSOLVABLE,
                "task_mismatch",
                {},
                (FailureType.INTERNAL_CONSTRAINT_ERROR,),
            )
        )
    if not evaluation.body_part_system_matches:
        failures.append(
            _failure(
                FailureType.WRONG_BODY_PART_SYSTEM,
                "wrong_body_part_system",
                {"expected_body_part_system": "forearm_hand"},
                (
                    FailureType.WRONG_JOINT_AXIS,
                    FailureType.MISSING_REQUIRED_FORCE,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                ),
            )
        )
    if not evaluation.joint_axis_matches:
        failures.append(
            _failure(
                FailureType.WRONG_JOINT_AXIS,
                "wrong_joint_axis",
                {"expected_joint_axis": "elbow_axis"},
                (
                    FailureType.LEVER_ARM_WRONG_PIVOT,
                    FailureType.WRONG_TORQUE_DIRECTION,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                ),
            )
        )

    failures.extend(
        _force_unit_failures(
            evaluation.dumbbell_unit,
            force_name="dumbbell force",
        )
    )

    if evaluation.counter_torque_muscle_matches is False:
        failures.append(
            _failure(
                FailureType.WRONG_COUNTER_TORQUE_MUSCLE,
                "wrong_counter_torque_muscle",
                {"external_force_name": "dumbbell force"},
                (
                    FailureType.WRONG_FORCE_DIRECTION,
                    FailureType.MISSING_LEVER_ARM,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                    FailureType.NUMERIC_ERROR,
                ),
            )
        )

    if (
        evaluation.counter_torque_muscle_matches is True
        and evaluation.muscle_unit is not None
    ):
        if evaluation.muscle_force_application_matches is False:
            failures.append(
                _failure(
                    FailureType.WRONG_MUSCLE_ATTACHMENT,
                    "wrong_muscle_attachment",
                    {"force_name": "selected muscle force"},
                    (
                        FailureType.LEVER_ARM_WRONG_LENGTH,
                        FailureType.EQUATION_NOT_EQUIVALENT,
                    ),
                )
            )
        if evaluation.muscle_force_direction_matches is False:
            failures.append(
                _failure(
                    FailureType.WRONG_FORCE_DIRECTION,
                    "wrong_muscle_force_direction",
                    {"force_name": "selected muscle force"},
                    (
                        FailureType.WRONG_TORQUE_DIRECTION,
                        FailureType.EQUATION_NOT_EQUIVALENT,
                    ),
                )
            )
        failures.extend(
            _force_unit_failures(
                evaluation.muscle_unit,
                force_name="selected muscle force",
            )
        )

    return diagnostic_report(failures)


def _force_unit_failures(
    check: ForceTorqueUnitCheck,
    *,
    force_name: str,
) -> tuple[ConstraintFailure, ...]:
    details = {"force_id": check.force_id, "force_name": force_name}
    failures: list[ConstraintFailure] = []
    if not check.force_present:
        failures.append(
            _failure(
                FailureType.MISSING_REQUIRED_FORCE,
                "missing_required_force",
                details,
                (
                    FailureType.MISSING_LINE_OF_ACTION,
                    FailureType.MISSING_LEVER_ARM,
                    FailureType.WRONG_TORQUE_DIRECTION,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                    FailureType.NUMERIC_ERROR,
                ),
            )
        )
    if not check.line_of_action_present:
        failures.append(
            _failure(
                FailureType.MISSING_LINE_OF_ACTION,
                "missing_line_of_action",
                details,
                (
                    FailureType.MISSING_LEVER_ARM,
                    FailureType.WRONG_TORQUE_DIRECTION,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                ),
            )
        )
    if check.line_of_action_matches_force is False:
        failures.append(
            _failure(
                FailureType.WRONG_LINE_OF_ACTION,
                "wrong_line_of_action",
                details,
                (
                    FailureType.LEVER_ARM_WRONG_LENGTH,
                    FailureType.WRONG_TORQUE_DIRECTION,
                ),
            )
        )
    if not check.lever_arm_present:
        failures.append(
            _failure(
                FailureType.MISSING_LEVER_ARM,
                "missing_lever_arm",
                details,
                (
                    FailureType.EQUATION_NOT_EQUIVALENT,
                    FailureType.NUMERIC_ERROR,
                ),
            )
        )
    if check.lever_arm_uses_force is False:
        failures.append(
            _failure(
                FailureType.LEVER_ARM_WRONG_FORCE,
                "lever_arm_wrong_force",
                details,
                (FailureType.EQUATION_NOT_EQUIVALENT,),
            )
        )
    if check.lever_arm_uses_pivot is False:
        failures.append(
            _failure(
                FailureType.LEVER_ARM_WRONG_PIVOT,
                "lever_arm_wrong_pivot",
                details,
                (FailureType.LEVER_ARM_WRONG_LENGTH,),
            )
        )
    if check.lever_arm_is_perpendicular is False:
        failures.append(
            _failure(
                FailureType.LEVER_ARM_NOT_PERPENDICULAR,
                "lever_arm_not_perpendicular",
                details,
                (
                    FailureType.LEVER_ARM_WRONG_LENGTH,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                    FailureType.NUMERIC_ERROR,
                ),
            )
        )
    if check.lever_arm_matches_geometry is False:
        failures.append(
            _failure(
                FailureType.LEVER_ARM_WRONG_LENGTH,
                "lever_arm_wrong_length",
                details,
                (
                    FailureType.EQUATION_NOT_EQUIVALENT,
                    FailureType.NUMERIC_ERROR,
                ),
            )
        )
    if check.torque_direction_matches is False:
        failures.append(
            _failure(
                FailureType.WRONG_TORQUE_DIRECTION,
                "wrong_torque_direction",
                details,
                (
                    FailureType.WRONG_TORQUE_SIGN,
                    FailureType.EQUATION_NOT_EQUIVALENT,
                ),
            )
        )
    if check.torque_sign_matches is False:
        failures.append(
            _failure(
                FailureType.WRONG_TORQUE_SIGN,
                "wrong_torque_sign",
                details,
                (FailureType.WRONG_EQUATION_SIGN,),
            )
        )
    return tuple(failures)


def _failure(
    failure_type: FailureType,
    message_key: str,
    formal_details: Mapping[str, object],
    downstream_failures: tuple[FailureType, ...] = (),
) -> ConstraintFailure:
    return ConstraintFailure(
        failure_type=failure_type,
        severity=FailureSeverity.BLOCKING,
        message_key=message_key,
        formal_details=formal_details,
        downstream_failures=downstream_failures,
    )
