"""Body-part system definitions."""

from __future__ import annotations

from dataclasses import dataclass

from biomech_tutor.anatomy.bones import AnatomyError, Bone


@dataclass(frozen=True)
class BodyPartSystem:
    """A selected anatomical system for a worksheet free-body diagram."""

    id: str
    display_name: str
    included_segments: tuple[Bone, ...]

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise AnatomyError("body-part system id must be non-empty")
        if not self.display_name.strip():
            raise AnatomyError("body-part system display_name must be non-empty")
        if not self.included_segments:
            raise AnatomyError("body-part system must include at least one segment")

    @property
    def included_segment_ids(self) -> tuple[str, ...]:
        return tuple(segment.id for segment in self.included_segments)
