"""First executable worksheet path: static elbow biceps curl."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from pathlib import Path
from typing import Protocol

from biomech_tutor.anatomy.models import (
    ForearmHandElbowModel,
    build_forearm_hand_elbow_model,
)
from biomech_tutor.anatomy.muscles import MuscleSpan2D
from biomech_tutor.core.geometry import DEFAULT_TOLERANCE, Point2D
from biomech_tutor.core.signs import RotationConvention, Sign
from biomech_tutor.physics.constraints import (
    ForceTorqueUnitCandidate2D,
    ForceTorqueUnitCheck,
    ForceTorqueUnitRequirement,
    check_force_torque_unit,
)
from biomech_tutor.physics.forces import Force2D
from biomech_tutor.physics.lever_arms import LeverArm2D
from biomech_tutor.physics.statics import (
    force_magnitude_for_torque_balance,
    required_balancing_force_vector,
)
from biomech_tutor.physics.torques import torque_sign_from_force
from biomech_tutor.tasks.compiler import DEFAULT_FIXTURE_DIR, compile_task_file
from biomech_tutor.tasks.schema import ForceSpec, TaskSpec, TaskValidationError


BICEPS_CURL_TASK_ID = "elbow_biceps_curl_2d"


class BicepsCurlDiagram(Protocol):
    """Structural input accepted by the task without importing the learner layer."""

    task_id: str
    body_part_system_id: str
    joint_axis_id: str
    force_torque_units: tuple[ForceTorqueUnitCandidate2D, ...]
    counter_torque_muscle_id: str | None

    def force_unit(self, force_id: str) -> ForceTorqueUnitCandidate2D | None: ...


@dataclass(frozen=True)
class BicepsCurlEvaluation:
    """Raw task evidence consumed by the later diagnostic adapter."""

    task_matches: bool
    body_part_system_matches: bool
    joint_axis_matches: bool
    dumbbell_unit: ForceTorqueUnitCheck
    counter_torque_muscle_matches: bool | None
    muscle_unit: ForceTorqueUnitCheck | None
    muscle_force_matches_anatomy: bool | None

    @property
    def satisfies_current_slice(self) -> bool:
        return (
            self.task_matches
            and self.body_part_system_matches
            and self.joint_axis_matches
            and self.dumbbell_unit.satisfies_requirements
            and self.counter_torque_muscle_matches is True
            and self.muscle_unit is not None
            and self.muscle_unit.satisfies_requirements
            and self.muscle_force_matches_anatomy is True
        )


@dataclass(frozen=True)
class CompiledBicepsCurlTask:
    """Validated fixture plus hidden elbow geometry and formal constraints."""

    spec: TaskSpec
    anatomy: ForearmHandElbowModel
    force_requirements: tuple[ForceTorqueUnitRequirement, ...]

    @property
    def pivot(self) -> Point2D:
        return self.anatomy.elbow_joint.axis.point

    @property
    def rotation_convention(self) -> RotationConvention:
        return RotationConvention(
            positive_label=self.spec.rotation_convention.positive,
            negative_label=self.spec.rotation_convention.negative,
            zero_label=self.spec.rotation_convention.zero,
        )

    def requirement(self, force_id: str) -> ForceTorqueUnitRequirement:
        try:
            return next(
                item for item in self.force_requirements if item.force_id == force_id
            )
        except StopIteration as exc:
            raise TaskValidationError(
                f"{self.spec.id}: unknown force requirement '{force_id}'"
            ) from exc

    def check_force_unit(
        self,
        force_id: str,
        candidate: ForceTorqueUnitCandidate2D | None,
    ) -> ForceTorqueUnitCheck:
        return check_force_torque_unit(
            self.requirement(force_id),
            self.pivot,
            self.rotation_convention,
            candidate,
        )

    def muscle_force(self, muscle_id: str, tension: float) -> Force2D:
        """Return a geometry-derived muscle force on the forearm insertion."""

        return self._muscle(muscle_id).force_on_insertion(tension)

    def muscle_force_matches_anatomy(
        self, muscle_id: str, force: Force2D
    ) -> bool:
        """Check insertion placement and tension direction against anatomy."""

        muscle = self._muscle(muscle_id)
        if not muscle.insertion_region.contains(force.application_point):
            return False
        expected_direction = force.application_point.vector_to(
            muscle.origin_region.center
        ).normalized()
        received_direction = force.vector.normalized()
        return isclose(
            expected_direction.cross_z(received_direction),
            0.0,
            abs_tol=DEFAULT_TOLERANCE,
        ) and expected_direction.dot(received_direction) > 0.0

    def counter_torque_muscle_ids(self, external_force: Force2D) -> tuple[str, ...]:
        """Compute counter-torque choices from geometry, not inverse labels."""

        external_sign = torque_sign_from_force(self.pivot, external_force)
        if external_sign is Sign.ZERO:
            return ()

        candidates = (self.anatomy.biceps.id, self.anatomy.triceps.id)
        return tuple(
            muscle_id
            for muscle_id in candidates
            if torque_sign_from_force(
                self.pivot, self.muscle_force(muscle_id, 1.0)
            ).value
            == -external_sign.value
        )

    def required_muscle_tension(
        self, external_force: Force2D, muscle_id: str
    ) -> float:
        """Solve the declared static torque balance for muscle tension."""

        if muscle_id not in self.counter_torque_muscle_ids(external_force):
            raise TaskValidationError(
                f"{muscle_id} does not counter the declared external torque"
            )
        external_arm = LeverArm2D(self.pivot, external_force.line_of_action).length
        unit_muscle_force = self.muscle_force(muscle_id, 1.0)
        muscle_arm = LeverArm2D(
            self.pivot, unit_muscle_force.line_of_action
        ).length
        return force_magnitude_for_torque_balance(
            external_force.magnitude,
            external_arm,
            muscle_arm,
        )

    def required_joint_force(
        self, external_force: Force2D, muscle_force: Force2D
    ) -> Force2D:
        """Return the elbow force required by the declared force balance."""

        vector = required_balancing_force_vector((external_force, muscle_force))
        if isclose(vector.magnitude(), 0.0, abs_tol=DEFAULT_TOLERANCE):
            raise TaskValidationError(
                "declared external and muscle forces need no balancing joint force"
            )
        return Force2D(self.pivot, vector)

    def evaluate(self, diagram: BicepsCurlDiagram) -> BicepsCurlEvaluation:
        """Evaluate the executable construction without selecting feedback prose."""

        dumbbell = diagram.force_unit("dumbbell_force")
        dumbbell_check = self.check_force_unit("dumbbell_force", dumbbell)

        muscle_matches = None
        muscle_check = None
        muscle_force_matches_anatomy = None
        if dumbbell is not None and dumbbell.force is not None:
            counter_ids = self.counter_torque_muscle_ids(dumbbell.force)
            muscle_matches = diagram.counter_torque_muscle_id in counter_ids
            if diagram.counter_torque_muscle_id == self.anatomy.biceps.id:
                submitted_muscle = diagram.force_unit("biceps_muscle_force")
                muscle_check = self.check_force_unit(
                    "biceps_muscle_force",
                    submitted_muscle,
                )
                if (
                    submitted_muscle is not None
                    and submitted_muscle.force is not None
                ):
                    muscle_force_matches_anatomy = self.muscle_force_matches_anatomy(
                        self.anatomy.biceps.id, submitted_muscle.force
                    )
            elif diagram.counter_torque_muscle_id == self.anatomy.triceps.id:
                submitted_muscle = diagram.force_unit("triceps_muscle_force")
                muscle_check = self.check_force_unit(
                    "triceps_muscle_force",
                    submitted_muscle,
                )
                if (
                    submitted_muscle is not None
                    and submitted_muscle.force is not None
                ):
                    muscle_force_matches_anatomy = self.muscle_force_matches_anatomy(
                        self.anatomy.triceps.id, submitted_muscle.force
                    )

        return BicepsCurlEvaluation(
            task_matches=diagram.task_id == self.spec.id,
            body_part_system_matches=(
                diagram.body_part_system_id == self.spec.body_part_system.id
            ),
            joint_axis_matches=diagram.joint_axis_id == self.spec.joint_axis.id,
            dumbbell_unit=dumbbell_check,
            counter_torque_muscle_matches=muscle_matches,
            muscle_unit=muscle_check,
            muscle_force_matches_anatomy=muscle_force_matches_anatomy,
        )

    def _muscle(self, muscle_id: str) -> MuscleSpan2D:
        if muscle_id == self.anatomy.biceps.id:
            return self.anatomy.biceps
        if muscle_id == self.anatomy.triceps.id:
            return self.anatomy.triceps
        raise TaskValidationError(f"{self.spec.id}: unknown muscle '{muscle_id}'")


def compile_biceps_curl_task(
    fixture_path: Path = DEFAULT_FIXTURE_DIR / f"{BICEPS_CURL_TASK_ID}.yaml",
) -> CompiledBicepsCurlTask:
    """Compile the biceps fixture and bind its hidden declared anatomy."""

    spec = compile_task_file(fixture_path)
    if spec.id != BICEPS_CURL_TASK_ID:
        raise TaskValidationError(
            f"expected task '{BICEPS_CURL_TASK_ID}', received '{spec.id}'"
        )
    if not spec.assumptions.static:
        raise TaskValidationError(f"{spec.id}: executable biceps task must be static")

    anatomy = build_forearm_hand_elbow_model()
    if spec.body_part_system.id != anatomy.forearm_hand_system.id:
        raise TaskValidationError(
            f"{spec.id}: body-part system does not match declared anatomy"
        )
    if spec.joint_axis.id != anatomy.elbow_joint.axis.id:
        raise TaskValidationError(
            f"{spec.id}: joint axis does not match declared anatomy"
        )

    requirements = tuple(_compile_force_requirement(item) for item in spec.force_inventory)
    return CompiledBicepsCurlTask(spec, anatomy, requirements)


def _compile_force_requirement(force: ForceSpec) -> ForceTorqueUnitRequirement:
    return ForceTorqueUnitRequirement(
        force_id=force.id,
        display_name=force.display_name,
        require_force=force.student_must_draw_force,
        require_line_of_action=force.student_must_draw_line_of_action,
        require_lever_arm=force.student_must_draw_lever_arm,
        require_torque_direction=force.student_must_identify_torque_direction,
        require_torque_sign=force.student_must_select_sign,
        required_for_torque_balance=force.required_for_torque_balance,
        required_for_force_balance=force.required_for_force_balance,
        may_have_zero_torque=force.may_have_zero_torque,
    )
