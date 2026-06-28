"""Bone model primitives."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.core.frames import Frame


class AnatomyError(ValueError):
    """Raised when an anatomical model is internally inconsistent."""


@dataclass(frozen=True)
class Bone:
    """A rigid anatomical segment with an associated frame."""

    id: str
    display_name: str
    frame: Frame

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("bone id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("bone display_name must be non-empty")
