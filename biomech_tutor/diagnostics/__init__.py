"""Diagnostic failure and feedback mapping package."""

from biomech_tutor.diagnostics.adapter import StudentFeedback, feedback_for_report
from biomech_tutor.diagnostics.failures import (
    ConstraintFailure,
    DiagnosticReport,
    FailureSeverity,
    FailureType,
    diagnose_biceps_curl,
    diagnostic_report,
)

__all__ = [
    "ConstraintFailure",
    "DiagnosticReport",
    "FailureSeverity",
    "FailureType",
    "StudentFeedback",
    "diagnose_biceps_curl",
    "diagnostic_report",
    "feedback_for_report",
]
