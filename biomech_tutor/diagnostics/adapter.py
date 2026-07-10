"""Adapters from structured failures to instructional feedback."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass

from biomech_tutor.diagnostics.failures import (
    DiagnosticReport,
    FailureSeverity,
    FailureType,
)
from biomech_tutor.diagnostics.hints import hint_for_failure
from biomech_tutor.diagnostics.message_catalog import message_for_failure


@dataclass(frozen=True)
class StudentFeedback:
    """One pedagogically relevant message with downstream failures suppressed."""

    failure_type: FailureType
    severity: FailureSeverity
    message: str
    hint: str | None
    suppressed_failure_count: int


def feedback_for_report(
    report: DiagnosticReport,
    *,
    level: str = "introductory_physics",
    visible_failure_types: Collection[FailureType] | None = None,
    message_overrides: Mapping[str, str] | None = None,
    hint_step: int | None = None,
) -> StudentFeedback | None:
    """Return only the earliest visible blocking failure for a learner."""

    failure = next(
        (
            item
            for item in report.failures
            if item.severity is FailureSeverity.BLOCKING
            and (
                visible_failure_types is None
                or item.failure_type in visible_failure_types
            )
        ),
        None,
    )
    if failure is None:
        return None

    hint = None if hint_step is None else hint_for_failure(failure, hint_step)
    return StudentFeedback(
        failure_type=failure.failure_type,
        severity=failure.severity,
        message=message_for_failure(
            failure,
            level=level,
            overrides=message_overrides,
        ),
        hint=hint,
        suppressed_failure_count=max(len(report.failures) - 1, 0),
    )
