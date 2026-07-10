# Design Contract

## Scope

Build a Python package that represents student biomechanics work as structured force-torque diagrams and returns structured diagnostic failures.

## Current Guardrails

- Do not begin with a graphical UI, full-body simulation, finite element analysis, machine learning, reinforcement learning, or a game engine.
- Do not infer answer keys from slide appearance alone.
- Treat external standards pages as metadata references unless an instructor explicitly supplies values.
- Keep student-facing language separate from the diagnostic engine.
- Report the earliest blocking conceptual error before downstream errors.

## Layer Boundaries

- Engine packages (`core`, `physics`, and `anatomy`) may use formal internal types, but must not import task, instructor, learner, diagnostics, student-projection, or demo layers.
- The task compiler may target engine objects, but must not depend on student projection, learner interaction, diagnostics, instructor UI, or demos.
- Instructor authoring code should depend on task vocabulary rather than engine internals.
- Student projection code may consume compiled task specs, but must not import or expose frame, transform, wrench, or transport terminology.
- Diagnostics consume raw task evidence and produce ordered structured failures without depending on learner interaction or presentation packages.
- Only the diagnostic adapter and message catalog translate failures into student-facing worksheet and course language.

These are dependency and visibility boundaries, not expressiveness limits. The engine can remain mathematically rich while outer layers receive controlled projections.
