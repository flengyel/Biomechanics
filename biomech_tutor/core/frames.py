"""Coordinate frame primitives."""

from __future__ import annotations

from dataclasses import dataclass


class FrameError(ValueError):
    """Raised when frame-compatible operations are used incorrectly."""


@dataclass(frozen=True)
class Frame:
    """A named coordinate frame for typed points and vectors."""

    id: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise FrameError("frame id must be a non-empty string")
        if self.display_name is not None and not self.display_name.strip():
            raise FrameError("frame display_name must be non-empty when provided")

    @property
    def label(self) -> str:
        return self.display_name or self.id


def require_same_frame(left: Frame, right: Frame) -> None:
    """Reject operations that mix quantities from different frames."""

    if left != right:
        raise FrameError(f"frame mismatch: {left.id} != {right.id}")
