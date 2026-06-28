"""Muscle and force attachment region primitives."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.anatomy.bones import AnatomyError
from biomech_tutor.core.geometry import Point2D


@dataclass(frozen=True)
class AttachmentRegion2D:
    """Approximate circular attachment region for worksheet-level geometry."""

    id: str
    display_name: str
    center: Point2D
    radius: float = 0.0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("attachment region id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("attachment region display_name must be non-empty")
        if self.radius < 0.0:
            raise AnatomyError("attachment region radius must be non-negative")

    @property
    def frame(self):
        return self.center.frame

    def contains(self, point: Point2D) -> bool:
        return self.center.vector_to(point).magnitude() <= self.radius
