"""Architectural layer boundary rules.

These rules guard against leaky abstractions. They intentionally constrain
dependency direction, not what each layer may represent internally.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LayerBoundaryRule:
    """Forbidden import prefixes for one package boundary."""

    package: str
    forbidden_import_prefixes: tuple[str, ...]
    reason: str


BOUNDARY_RULES = (
    LayerBoundaryRule(
        package="biomech_tutor.core",
        forbidden_import_prefixes=(
            "biomech_tutor.anatomy",
            "biomech_tutor.demo",
            "biomech_tutor.diagnostics",
            "biomech_tutor.instructor",
            "biomech_tutor.learner",
            "biomech_tutor.physics",
            "biomech_tutor.student_projection",
            "biomech_tutor.tasks",
        ),
        reason="Core primitives must not depend on higher-level packages.",
    ),
    LayerBoundaryRule(
        package="biomech_tutor.physics",
        forbidden_import_prefixes=(
            "biomech_tutor.demo",
            "biomech_tutor.diagnostics",
            "biomech_tutor.instructor",
            "biomech_tutor.learner",
            "biomech_tutor.student_projection",
            "biomech_tutor.tasks",
        ),
        reason="Physics is engine-level and must not depend on task or UI layers.",
    ),
    LayerBoundaryRule(
        package="biomech_tutor.anatomy",
        forbidden_import_prefixes=(
            "biomech_tutor.demo",
            "biomech_tutor.diagnostics",
            "biomech_tutor.instructor",
            "biomech_tutor.learner",
            "biomech_tutor.student_projection",
            "biomech_tutor.tasks",
        ),
        reason="Anatomy is engine-level and must not depend on task or UI layers.",
    ),
    LayerBoundaryRule(
        package="biomech_tutor.tasks",
        forbidden_import_prefixes=(
            "biomech_tutor.demo",
            "biomech_tutor.diagnostics",
            "biomech_tutor.instructor",
            "biomech_tutor.learner",
            "biomech_tutor.student_projection",
        ),
        reason="The task compiler may target engine objects but not presentation layers.",
    ),
    LayerBoundaryRule(
        package="biomech_tutor.diagnostics",
        forbidden_import_prefixes=(
            "biomech_tutor.demo",
            "biomech_tutor.instructor",
            "biomech_tutor.learner",
            "biomech_tutor.student_projection",
        ),
        reason=(
            "Diagnostics may consume task evidence but must remain independent of "
            "interaction and presentation layers."
        ),
    ),
    LayerBoundaryRule(
        package="biomech_tutor.instructor",
        forbidden_import_prefixes=(
            "biomech_tutor.anatomy",
            "biomech_tutor.core",
            "biomech_tutor.demo",
            "biomech_tutor.diagnostics",
            "biomech_tutor.learner",
            "biomech_tutor.physics",
            "biomech_tutor.student_projection",
        ),
        reason="Instructor authoring should speak task vocabulary, not engine internals.",
    ),
    LayerBoundaryRule(
        package="biomech_tutor.student_projection",
        forbidden_import_prefixes=(
            "biomech_tutor.anatomy",
            "biomech_tutor.core",
            "biomech_tutor.demo",
            "biomech_tutor.diagnostics",
            "biomech_tutor.learner",
            "biomech_tutor.physics",
        ),
        reason="Student projections must not expose engine-internal abstractions.",
    ),
)


STUDENT_PROJECTION_FORBIDDEN_TERMS = (
    "Frame",
    "FrameGroupoid",
    "Point2D",
    "QuantityBundle",
    "RigidTransform",
    "Torque2D",
    "Transport",
    "TransportArrow",
    "Vector2D",
    "Wrench",
    "WrenchMap",
)
