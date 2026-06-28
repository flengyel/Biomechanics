# Project Proposal: Constraint-Aware Diagnostic Biomechanics Tutor

**Version:** Milestone 1 Worksheet-Pack Diagnostic Core


## 1. Working Title

**Biomechanics Diagnostic Tutor**

Alternative internal name: **Biomech Tutor**

---

## 2. Executive Summary

This project will develop an interactive tutoring system for undergraduate biological physics and biomechanics. Students will manipulate body parts, joints, muscles, force arrows, lines of action, lever arms, torque directions, equation signs, force-balance equations, torque-balance equations, and numerical estimates. The system will diagnose not only whether an answer is right or wrong, but why it is wrong: missing force, wrong joint axis, incorrect force direction, missing lever arm, wrong lever-arm geometry, wrong torque direction, wrong sign convention, incorrect counter-torque muscle, missing equation term, wrong body-weight scaling, wrong angular-acceleration relation, algebraic error, or unit error.

The technical foundation is a hidden typed anatomical and physical constraint engine. Internally, the system represents anatomical coordinate frames as a groupoid of invertible transforms. Physical quantities such as points, vectors, forces, torques, wrenches, lines of action, and lever arms are typed over those frames. Muscles are represented either as constrained anatomical spans with origins, insertions, paths, and tension-only force constraints, or, in early qualitative tasks, as direct joint-torque labels when the classroom worksheet asks only for torque direction.

Above this formal layer, instructors author pedagogical tasks; students interact only with lesson-level objects appropriate to their course level. The design goal is a diagnostic biomechanics tutor that would be difficult to reproduce by retrofitting an ordinary simulator or anatomy viewer, because the student’s work is represented as a structured biomechanical diagram rather than as a final answer alone.

The first coding path is a static biceps curl task, because it exercises the essential loop: force inventory, force arrows, lever arms, torque directions, torque-balance equations, lever-arm ratio estimates, force equilibrium, joint force, diagnostics, and feedback. However, the first project milestone is the **Worksheet-Pack Diagnostic Core**: all uploaded scenario worksheet families must be represented as task fixtures, compile successfully, and provide executable or instructor-key-gated diagnostics at worksheet fidelity. The lower-leg jump worksheet is included in Milestone 1 as qualitative rotational dynamics with signs of omega, alpha, net torque, muscle dominance, and `± tau_M ± tau_n = ± I alpha`; it is not full continuous dynamic simulation.

---

## 3. Educational Problem

Undergraduate students often learn biological physics and biomechanics through simplified force and torque problems. The uploaded classroom worksheets emphasize repeated reasoning patterns:

- select the body-part system;
- identify the joint axis;
- draw every relevant force;
- draw the lever arm for each force;
- identify torque direction for each force;
- choose the muscle that supplies counter-torque;
- estimate force ratios from lever-arm ratios;
- resize vectors to show relative magnitudes;
- write signed torque-balance equations;
- write signed force-balance equations;
- compute joint forces after muscle forces are estimated;
- reason about angular velocity, angular acceleration, and muscle dominance in dynamic phases.

Current educational workflows often split these skills apart:

- anatomy viewers show body structures;
- physics homework systems grade equations or numbers;
- biomechanics simulators compute outputs from prebuilt models;
- classroom slides and worksheets ask students to reason through diagrams manually.

The missing system is a tutor that lets students construct the biomechanical situation and receives precise diagnostic feedback on that construction.

The system should answer questions such as:

```text
Did the student identify the correct body-part system?
Did the student choose the correct joint axis?
Did the student identify every relevant force?
Did the student include an irrelevant force?
Did the force point in the right direction?
Did the student draw the lever arm for each force?
Was each lever arm perpendicular to the correct force line of action?
Did the student identify the torque direction for each force?
Did the sign convention match the task convention?
Did the student choose the correct counter-torque muscle?
Did the net torque direction match angular acceleration?
Was the equation wrong because of a conceptual setup error or algebra?
Was the final number correct for the wrong reason?
```

This requires more than simulation. It requires a formal diagnostic representation of the learner’s work.

---

## 4. Source-Grounded Scenario Inventory

The project’s initial scenario set is based on the uploaded classroom worksheets. The proposal does not invent numerical answer keys for missing worksheet values; any missing standards values, lever-arm ratios, or geometry must be supplied by instructors or generated from a declared simplified model.

| Source worksheet | Scenario | Core student work |
|---|---|---|
| `Activity Biceps Curl2d.pptx` | Static biceps curl, forearm/hand about elbow, arm weight neglected at first. | Draw dumbbell force, lever arm, torque direction; choose biceps/triceps counter-torque; draw muscle force and lever arm; estimate muscle force from lever-arm ratio; compute elbow joint force from force equilibrium. |
| `Activity overhead extension 3.pptx` | Overhead extension, forearm/hand about elbow. | Draw dumbbell and forearm/hand weight torques and lever arms; choose triceps/biceps; use extension-positive/flexion-negative signs; estimate muscle force; compute joint force; later include arm weight. |
| `Activity Leg Extension3.pptx` | Leg-extension machine, lower leg/foot or lower leg about knee. | Draw padded-bar force on top of foot, knee joint, lever arm, torque direction; choose quadriceps/hamstrings counter-torque; estimate muscle force from lever-arm ratio and body-weight scaling. |
| `Activity Leg press 3b.pptx` | Leg press, whole leg about hip. | Draw platform force and muscle force; choose psoas/gluteus maximus; draw lever arms; estimate lever-arm ratio; compute muscle force in terms of body weight. |
| `Squat with barbell Jc.pptx` | Squat with barbell; whole-person force equilibrium and hip/knee/ankle torque analyses. | Compute floor normals with barbell `3 Wbody` and equal left/right normals; identify torque direction of floor normal about hip/knee/ankle; choose glute/psoas, quads/hamstrings, Achilles/calf/tibialis; estimate muscle force ratios. |
| `Activity Foot - upside down seesawc.pptx` | Foot as an upside-down seesaw about ankle. | Identify floor-normal torque as dorsiflexion/plantarflexion; choose Achilles/calf or tibialis; estimate Achilles force from lever-arm ratio; critique a publication diagram by torque balance; compute ankle joint force using force balance. |
| `Activity Head as seesawb.pptx` | Head as seesaw about atlanto-occipital joint. | Estimate neck muscle force from head weight and lever-arm ratio; estimate joint force from force equilibrium. |
| `Activity Which muscle when lower leg knee partially done.pptx` | Lower leg-foot rotation about knee during jump take-off/landing. | Use flexion-negative/extension-positive convention; read omega/alpha signs; identify floor, quadriceps, and hamstring torque directions; choose force/muscle needed for alpha; assign signs in `± tau_M ± tau_n = ± I alpha`; mark quadriceps/hamstring dominance intervals. |

---

## 5. Proposed Solution

The system will be built around five architectural layers:

```text
1. Engine model
2. Task compiler
3. Instructor authoring layer
4. Student interaction layer
5. Diagnostic/pedagogical adapter
```

The core principle is:

```text
Students manipulate pedagogical force-torque diagrams.
Instructors configure visible learning tasks.
The engine validates typed biomechanical diagrams.
The diagnostic adapter translates formal failures into useful feedback.
```

The student should not need to see coordinate-frame machinery, wrench transport, or internal type constraints. Those structures exist to make the tutoring system accurate, extensible, and difficult to duplicate by retrofitting a conventional simulator.

---

## 6. Technical Foundation

## 6.1 Frame Groupoid

For each pose `q`, the engine maintains a frame groupoid:

```text
G_q
```

Objects are anatomical frames:

```text
WorldFrame
HumerusFrame
RadiusFrame
UlnaFrame
HandFrame
FemurFrame
TibiaFrame
FootFrame
PelvisFrame
HeadFrame
ElbowFrame
KneeFrame
HipFrame
AnkleFrame
AtlantoOccipitalFrame
```

Arrows are rigid transforms:

```text
T[A <- B](q): B -> A
```

They satisfy identity, inverse, and composition laws. This machinery ensures coordinate consistency. It prevents errors such as applying a force expressed in one frame to a point expressed in another, computing a torque about the wrong origin, or mixing local and global quantities.

## 6.2 Typed Quantity Bundles

Each frame supports typed physical quantities:

```text
Point[Frame]
Vector[Frame]
Force[Frame]
Torque[Frame]
Wrench[Frame]
LineOfAction[Frame]
LeverArm[Frame]
JointAxis[Frame]
```

Operations are valid only when their inputs are frame-compatible or explicitly transported into a common frame.

For a force `F` applied at point `p`, torque about pivot or joint point `o` is:

```text
tau = (p - o) × F
```

For introductory lessons, this is projected to:

```text
tau = F * r_perp
```

where `r_perp` is the perpendicular lever arm from the joint axis or pivot to the force’s line of action.

## 6.3 Force-Torque Units

The fundamental student-facing object should be a force-torque unit, not just a force arrow.

Each force-torque unit contains:

```text
force identity
force direction
line of action
application point or attachment region
lever arm
torque direction
torque sign
equation term
```

This design directly follows the classroom requirement that students draw the lever arm and identify torque direction for every relevant force.

## 6.4 Muscles as Constrained Anatomical Spans or Direct Torque Labels

For geometry-based tasks, a muscle is represented as:

```text
origin region
insertion region
muscle path
line of action
tension variable
constraint F_i >= 0
```

For early qualitative dynamics tasks, a muscle may be represented as a direct joint-torque label if the worksheet asks only whether quadriceps or hamstrings produce flexion or extension torque. The task specification must declare which representation is being used.

## 6.5 Static Equilibrium

Static tasks support:

```text
sum(torques) = 0
sum(forces) = 0
```

The worksheets repeatedly use:

```text
tau_muscle = tau_external
M * r_perp_M = F_external * r_perp_external
M = F_external * (r_perp_external / r_perp_M)
```

Force equilibrium is used after torque equilibrium to estimate joint forces:

```text
sum(F) = 0
J = signed combination of the other forces
```

## 6.6 Rotational Dynamics

The lower-leg jump worksheet requires:

```text
sum(tau) = I * alpha
```

The engine must support:

```text
angular velocity sign
angular acceleration sign
torque sign
net torque direction
muscle dominance
ignore-in-air intervals
```

The task uses the convention:

```text
flexion negative
extension positive
```

The tutor should diagnose whether the student confuses:

```text
torque direction with motion direction
torque direction with angular acceleration direction
speeding up with slowing down
quadriceps dominance with hamstring dominance
```

---

## 7. Student, Instructor, and Engine Separation

## 7.1 Student Layer

Students work with:

```text
body part
joint axis
muscle
force arrow
line of action
lever arm
torque direction
rotation label
equation sign
equation term
unknown force
joint force
angular velocity marker
angular acceleration marker
phase interval
```

Students should not see:

```text
FrameGroupoid
TransportArrow
WrenchMap
QuantityBundle
TaskGroupoid
CanonicalSolutionDiagram
```

unless a future advanced mode deliberately exposes those concepts.

## 7.2 Instructor Layer

Instructors author tasks declaratively. They specify:

```text
source worksheet
learning goals
body-part system
joint axis
rotation convention
force inventory
required lever arms
required torque directions
allowed muscles
allowed equations
difficulty level
hint sequence
diagnostic priority
rubric
simplifying assumptions
external data references
```

The instructor should not need to author frame transforms or typed internal diagrams.

## 7.3 Engine Layer

The engine compiles the instructor’s lesson into a formal biomechanical constraint problem. It validates student work as a typed learner diagram.

Example student action:

```text
Student draws a dumbbell force arrow and lever arm about the elbow.
```

Internal representation:

```text
ForceTorqueUnitCandidate:
  force_id: dumbbell_force
  line_of_action: LineOfAction[WorldFrame]
  lever_arm: LeverArm[WorldFrame]
  joint_axis: JointAxis[ElbowFrame]
  claimed_torque_direction: flexion or extension
```

The engine then checks:

```text
Is the force required for this task?
Is the line of action correct?
Is the lever arm attached to the correct force?
Is the lever arm perpendicular to the force line of action?
Does the torque direction match geometry and sign convention?
Does the equation use the correct torque term and sign?
Does the numerical answer follow from the accepted setup?
```

---

## 8. Diagnostic Model

The system must record student work structurally, not just as a final number.

A submission should include:

```text
selected body-part system
selected joint axis
force inventory
force arrows
lines of action
lever arms
torque directions
torque signs
equation terms
numeric answers
units or body-weight scaling
```

The diagnostic engine should use a blocking-error hierarchy:

```text
wrong body-part system
wrong joint axis
missing force
wrong force direction
missing lever arm
lever arm not perpendicular
wrong torque direction
wrong muscle selected
wrong equation sign
wrong numeric answer
```

The diagnostic adapter converts structured failures into student-facing feedback.

Example:

```text
The lever arm for the floor force must be perpendicular to the floor force's line of action.
```

rather than:

```text
The internal lever-arm constraint failed.
```

The system should report the earliest blocking conceptual error first, suppressing downstream failures until the earlier error is corrected.

---

## 9. Initial Milestones

## Milestone 0: Source-Material Encoding

Deliverables:

```text
source-grounded task inventory
canonical label map
scenario worksheet metadata
list of prompt types across all uploaded worksheets
list of external data placeholders
list of explicit constants found in worksheets
missing-data policy for each worksheet prompt
task fixture skeletons for every uploaded worksheet
```

This milestone prevents omissions and hallucinated task content.

## Milestone 1: Worksheet-Pack Diagnostic Core

Milestone 1 is the first project milestone. It is broader than a single polished task and shallower than a full simulator. It must encode the uploaded worksheet pack at worksheet fidelity.

Required worksheet fixtures:

```text
elbow_biceps_curl_2d
elbow_overhead_extension_2d
knee_leg_extension_2d
hip_leg_press_2d
squat_barbell_multi_joint_2d
ankle_foot_upside_down_seesaw_2d
head_atlanto_occipital_seesaw_2d
knee_lower_leg_jump_dynamics
```

Required formal capabilities:

```text
Python package skeleton
frame and transform system
typed physical quantities
force line-of-action model
lever-arm model
torque direction and sign calculation
force-torque-unit learner diagram
static torque-balance checker
static force-balance checker
joint-force representation
body-part system selection
joint-axis selection
rotation-label and sign-convention model
lever-arm ratio model
external-reference and instructor-key placeholders
qualitative rotational-dynamics sign model
structured diagnostic failure hierarchy
diagnostic adapter
task compiler validation
unit tests across all worksheet fixtures
```

Required static worksheet diagnostics:

```text
missing required force
extra irrelevant force
wrong body-part system
wrong joint axis
wrong force placement or direction
missing lever arm
lever arm associated with wrong force
lever arm drawn from wrong pivot or joint axis
lever arm not perpendicular to force line of action
wrong torque direction
wrong torque sign convention
wrong counter-torque muscle
wrong lever-arm ratio relation
wrong torque-balance equation
wrong force-balance equation
wrong joint-force direction or sign
wrong units or body-weight scaling
correct setup but wrong arithmetic
```

Required qualitative dynamics diagnostics:

```text
wrong omega sign
wrong alpha sign
wrong floor-force torque direction
wrong quadriceps torque direction
wrong hamstrings torque direction
wrong force or muscle selected for required alpha
wrong signs in ± tau_M ± tau_n = ± I alpha
wrong speed-up/slow-down classification when enabled
wrong concentric/eccentric classification when enabled
wrong quadriceps/hamstrings dominance interval
```

Acceptance rule:

```text
Biceps curl must run as the first complete text demo.
Lower-leg qualitative dynamics must run as the second text demo.
Every other worksheet fixture must compile, expose its prompt structure, declare its missing-data policy, and diagnose at least one representative wrong answer for every prompt type it contains.
The compiler must reject under-specified answer-key generation instead of inventing values.
```

## Milestone 2: Classroom-Aligned Visual Prototype

Only after Milestone 1 passes, build a visual interface that supports:

```text
dragging joint axes
drawing force arrows
drawing lever arms
selecting torque directions
resizing force vectors
rearranging equation terms
selecting phase intervals on time graphs
receiving targeted feedback
```

The visual interface should reproduce the classroom interaction patterns without exposing engine machinery.

## Milestone 3: Expanded Lesson Authoring and Reuse

Deliverables:

```text
instructor authoring templates
rubric templates
hint templates
common misconception library
task variants derived from the worksheet fixtures
exportable classroom activities
```

## Milestone 4: Later Simulation Extensions

Only after the diagnostic worksheet core is stable, consider:

```text
3D graphics
pose-dependent moment arms
multi-muscle redundancy
inverse dynamics
OpenSim or MuJoCo interoperability
contact/friction modules
finite element demonstrations for tissue stress
```

These are not part of Milestone 1.

---

## 10. Relationship to Existing Systems

Existing musculoskeletal simulators and anatomy tools are not the initial target. The distinctive goal here is diagnostic tutoring through typed learner construction. The system should be evaluated by whether it can diagnose a student’s force-torque diagram, not by whether it can simulate full-body movement.

The proposed architecture is strongest when it can say:

```text
The final number is wrong because the student used the radius vector instead of the perpendicular lever arm.
```

or:

```text
The selected muscle is wrong because its torque direction does not counter the external torque under the task's rotation convention.
```

or:

```text
The rotational equation has the wrong sign because flexion is negative and extension is positive in this task.
```

Those are tutoring diagnostics, not ordinary simulation outputs.

---

## 11. Research and Development Questions

The project should answer these early:

1. Can a classroom biomechanics worksheet be represented as a typed learner diagram without making authoring burdensome?
2. Can the engine distinguish missing force, wrong lever arm, wrong torque direction, wrong muscle choice, wrong equation sign, and wrong arithmetic?
3. Can instructor-authored task specifications compile into valid formal constraint problems?
4. Can the same hidden formal model support multiple student levels through projections?
5. Can the system accept equivalent correct solution paths rather than hard-coding one answer?
6. Can diagnostics remain useful without leaking formal machinery into the student interface?
7. Can qualitative dynamics tasks be represented with the same force-torque-unit structure plus angular-velocity and angular-acceleration signs?

---

## 12. Evaluation Plan

Technical evaluation:

```text
unit tests for frame transforms
unit tests for typed quantities
line-of-action and lever-arm tests
torque-direction and sign-convention tests
known-answer statics tests from declared task geometry
task compiler validation tests
diagnostic ordering tests
equivalent solution acceptance tests
rotational-dynamics sign tests
```

Pedagogical evaluation:

```text
compare system diagnostics to instructor expectations
use wrong answers implied by worksheets as regression tests
verify hint ordering
check whether feedback matches course vocabulary
verify that external-data placeholders are not silently filled
measure whether students can correct errors after feedback
```

The uploaded worksheets should become regression tests: every prompt type in the worksheets should map to a task schema, student action, or diagnostic category.

---

## 13. Risk Assessment

## Risk: Scope Creep

The largest risk is premature expansion into full-body simulation, dynamics beyond the worksheets, high-fidelity anatomy, or graphical game development.

Mitigation:

```text
complete source-grounded task fixtures first
use biceps curl as the first coding path, but accept Milestone 1 only when the worksheet-pack diagnostic core passes
use text or notebook demo before graphical UI
postpone full-body and high-fidelity dynamics
```

## Risk: Leaky Abstractions

The formal engine may expose frame, transport, or wrench language to students too early.

Mitigation:

```text
diagnostic adapter
visibility policy
difficulty-level projections
student-facing feedback templates
worksheet-language aliases
```

## Risk: Instructor Authoring Burden

If lesson creation requires engine-level formalism, the system will not scale.

Mitigation:

```text
declarative task schema
compiler validation
instructor-level error messages
reusable task templates
source-grounded fixtures
```

## Risk: Weak Diagnostics from Final Answers Alone

If students only enter numbers, the system cannot diagnose reasoning.

Mitigation:

```text
record force-torque diagrams
require force, line of action, lever arm, torque direction, equation, and number
separate conceptual setup from arithmetic result
```

## Risk: Hallucinated Data

Worksheets reference external standards and contain placeholders. Silent filling of values would create unreliable tasks.

Mitigation:

```text
treat standards pages as external metadata
require instructor-supplied values or declared test fixtures
reject tasks with missing required numeric data
record explicit constants separately from placeholders
```

## Risk: Overfitting to One Worksheet

The first task may work but fail to generalize.

Mitigation:

```text
maintain all worksheet-derived task fixtures from the beginning
extract common force-torque-unit schema
extract reusable templates for elbow, knee, hip, ankle, and head tasks
```

---

## 14. Proposed Repository Structure

```text
biomech-tutor/
  README.md
  DESIGN_CONTRACT.md
  PROJECT_PROPOSAL.md
  pyproject.toml

  biomech_tutor/
    core/
      frames.py
      transforms.py
      quantities.py
      units.py
      geometry.py
      signs.py

    anatomy/
      bones.py
      joints.py
      muscles.py
      attachment_regions.py
      body_part_systems.py
      models.py

    physics/
      forces.py
      lines_of_action.py
      lever_arms.py
      torques.py
      wrenches.py
      statics.py
      rotational_dynamics.py
      constraints.py

    tasks/
      schema.py
      compiler.py
      fixtures/
        elbow_biceps_curl_2d.yaml
        elbow_overhead_extension_2d.yaml
        knee_leg_extension_2d.yaml
        hip_leg_press_2d.yaml
        squat_barbell_multi_joint_2d.yaml
        ankle_foot_upside_down_seesaw_2d.yaml
        head_atlanto_occipital_seesaw_2d.yaml
        knee_lower_leg_jump_dynamics.yaml

    learner/
      actions.py
      diagrams.py
      submissions.py
      equation_inputs.py
      graph_inputs.py

    diagnostics/
      failures.py
      adapter.py
      hints.py
      rubrics.py
      message_catalog.py

    instructor/
      authoring_schema.py
      validation.py
      external_references.py

    student_projection/
      projection.py
      labels.py
      feedback_language.py
      source_aliases.py

    demo/
      elbow_biceps_curl_2d.py
      knee_lower_leg_jump_dynamics.py

    tests/
      test_frame_groupoid.py
      test_quantity_typing.py
      test_line_of_action.py
      test_lever_arm.py
      test_torque_direction.py
      test_static_equilibrium.py
      test_force_equilibrium.py
      test_rotational_dynamics.py
      test_task_compiler.py
      test_elbow_biceps_curl_2d.py
      test_elbow_overhead_extension_2d.py
      test_knee_leg_extension_2d.py
      test_hip_leg_press_2d.py
      test_squat_barbell_multi_joint_2d.py
      test_ankle_foot_upside_down_seesaw_2d.py
      test_head_atlanto_occipital_seesaw_2d.py
      test_knee_lower_leg_jump_dynamics.py
      test_diagnostics.py
```

The first runnable milestone should support:

```bash
pytest
python -m biomech_tutor.tasks.validate_all
python -m biomech_tutor.demo.elbow_biceps_curl_2d
python -m biomech_tutor.demo.knee_lower_leg_jump_dynamics
```

The demos need not cover every worksheet. The tests and `validate_all` command must cover every worksheet fixture.

---

## 15. Summary

This project should begin with a formal diagnostic core, not a graphical simulator. The key deliverable is a system that can represent student biomechanics work as a structured force-torque diagram, validate it against hidden anatomical and physical constraints, and return useful feedback at the student’s instructional level.

The uploaded worksheets refine the core product requirement: for each relevant force, students must identify the force, line of action, lever arm, torque direction, sign, and equation term. The architecture must therefore treat a force-torque unit as the fundamental student-work object.

The first coding path, static biceps curl, is sufficient to test the essential diagnostic loop, but it is not sufficient to complete the first milestone. Milestone 1 is complete only when the full uploaded worksheet pack is represented as compiler-validated fixtures, with executable or instructor-key-gated diagnostics at worksheet fidelity. The lower-leg jump worksheet is included in Milestone 1 as qualitative rotational dynamics with angular velocity, angular acceleration, net torque, equation signs, and muscle dominance.
