# Codex Project Instructions: Constraint-Aware Diagnostic Biomechanics Tutor

**Version:** Milestone 1 Worksheet-Pack Diagnostic Core


## 0. Project Thesis

Build a diagnostic biomechanics tutoring system in which students manipulate visible pedagogical objects—body parts, joints, muscles, force arrows, lines of action, lever arms, torque directions, signs, force-balance equations, torque-balance equations, angular-velocity and angular-acceleration indicators, and numerical estimates—while a hidden typed constraint engine validates those actions using anatomical frame groupoids, typed physical quantities, anatomical relations, and constrained mechanics.

The system is not primarily a musculoskeletal research simulator. It is an educational diagnostic engine. Its core value is the ability to diagnose how a student constructed a biomechanical situation, not merely whether a final answer matches.

The first implementation must be a Python package with a text-based demo and unit tests. Do not begin with graphical UI, full-body simulation, finite element analysis, machine learning, reinforcement learning, or a game engine.

---

## 1. Source-Grounding Rules for Codex

These instructions incorporate the current chat design plus the uploaded classroom scenario worksheets. Codex must treat the uploaded worksheets as source material for initial task families and must not invent missing numerical values, answer keys, or biomechanics facts that are not present in the task specifications.

### 1.1 Uploaded Scenario Worksheets to Represent

The initial task family is grounded in these uploaded files:

| Source file | Required task family extracted from it |
|---|---|
| `Activity Biceps Curl2d.pptx` | Static biceps curl, forearm/hand about elbow, dumbbell torque, biceps/triceps counter-torque choice, lever-arm ratio, muscle force estimate, elbow joint force from force equilibrium. |
| `Activity overhead extension 3.pptx` | Static overhead triceps extension, forearm/hand about elbow, dumbbell and forearm/hand weight torques, extension-positive/flexion-negative sign convention, triceps/biceps choice, lever-arm ratio, joint force, optional inclusion of arm weight. |
| `Activity Leg Extension3.pptx` | Static leg extension, lower leg/foot or lower leg about knee, padded bar force on top of foot, quadriceps/hamstrings counter-torque choice, lever-arm ratio, body-weight scaling. |
| `Activity Leg press 3b.pptx` | Static leg press, whole leg about hip, platform force, psoas/gluteus maximus counter-torque choice, lever-arm ratio, body-weight scaling with per-leg platform force. |
| `Squat with barbell Jc.pptx` | Squat/barbell scenario, whole-person force equilibrium, equal left/right floor normals, floor-normal torque direction about hip/knee/ankle, counter-torque muscles at hip/knee/ankle, lever-arm ratio estimates. |
| `Activity Foot - upside down seesawc.pptx` | Foot/ankle static equilibrium, floor normal and Achilles/calf or tibialis counter-torque, Achilles force estimate by lever-arm ratio, critique of a published diagram by torque-balance reasoning, ankle joint force from force balance, force components and simplified vertical-force approximation. |
| `Activity Head as seesawb.pptx` | Head about atlanto-occipital joint, head weight and neck muscle force, lever-arm ratio, head weight estimate, joint force from force equilibrium. |
| `Activity Which muscle when lower leg knee partially done.pptx` | Lower leg-foot rotation about knee during jump take-off and landing, flexion-negative/extension-positive convention, angular velocity, angular acceleration, floor-normal torque, quadriceps/hamstrings torque directions, muscle dominance, `± τ_M ± τ_n = ± I α`, concentric/eccentric and speed-up/slow-down classifications. |

### 1.2 Do Not Hallucinate Values

The worksheets contain several placeholders such as `? Wbody`, `? lbs`, `?`, and references to external strength standards. Do not hard-code values for those placeholders unless they appear explicitly in a task file authored for the project.

Allowed explicit constants from the worksheets include only those that are directly present in the worksheet text, such as:

- `Fbarbell = 3 Wbody` in the squat worksheet;
- `nfloor = Wbody` in the foot/ankle worksheet;
- `dumbbell = 10 lb` in biceps-curl/overhead-extension prompts where stated;
- `dumbbell = 0.45 Wbody` in the overhead-extension body-weight prompt where stated;
- `Warm = 0.02 * 115 lb` in the overhead-extension arm-weight prompt where stated.

Any external standards page should be represented as an `ExternalReference` or instructor-provided data slot. Do not fetch or encode current standards in the initial package.

### 1.3 Answer Keys Must Be Generated or Explicitly Provided

Do not infer answer keys from slide appearance alone. Correctness must come from one of:

1. a formal geometric/physical model declared in the task specification;
2. an explicit instructor-provided answer key;
3. a deterministic simplification declared in the task specification.

If a task has insufficient geometry to compute a torque direction, lever-arm ratio, or joint force, the task compiler must reject the task or mark the relevant answer as `requires_instructor_key`.

### 1.4 Preserve Source Wording as Labels, Normalize Internally

The worksheets use labels such as `forearm/hand`, `lower leg/foot`, `whole leg`, `foot`, `head`, `hip`, `knee`, `ankle`, `elbow`, and `atlanto-occipital joint`.

Preserve these as instructor/student-facing labels where appropriate. Internally normalize labels to safe canonical identifiers:

```text
forearm_hand
lower_leg_foot
whole_leg
foot
head
hip
knee
ankle
elbow
atlanto_occipital_joint
```

Normalize spelling variants and typos in source materials, for example `Doriflexion` to `dorsiflexion`, but keep optional display aliases so worksheet language can be reproduced.

---

## 2. Non-Negotiable Design Principles

### 2.1 Separate Formal Engine from Student Interface

The system must strictly separate:

1. **Engine model**
2. **Task compiler**
3. **Instructor authoring layer**
4. **Student interaction layer**
5. **Diagnostic/pedagogical adapter**

Students do not see frame groupoids, transport arrows, typed fibers, wrench maps, or solution groupoids unless an advanced mode is explicitly enabled later.

Instructors author lessons using pedagogical terms and course concepts, not engine-internal formalism.

The engine remains mathematically strict. The student and instructor layers are controlled projections of the engine.

### 2.2 Every Force Requires a Force-Torque Unit

Every task must declare a force inventory. For every force acting on the selected body part, the student must identify or supply the subset required by the task:

1. the force;
2. the force direction;
3. the line of action;
4. the force application point or attachment region, when applicable;
5. the lever arm about the selected joint axis or pivot;
6. the torque direction;
7. the torque sign under the task convention;
8. the corresponding equation term, when equations are part of the task.

The learner’s equation and numerical answer must not be graded as complete until the required force-level torque diagram is complete.

If a force has zero torque, the student must explicitly identify the zero lever arm and zero torque when the task requires it.

### 2.3 Student Work Must Be Structural

Do not treat student work as a final number only. A student solution must be represented as a structured learner diagram containing the student’s choices for forces, lever arms, torque directions, signs, equations, body-weight scaling, and numerical answers.

This is required so the system can distinguish:

- missing required force;
- extra irrelevant force;
- wrong body-part system;
- wrong joint axis;
- wrong force placement or attachment;
- wrong force direction;
- missing lever arm;
- lever arm associated with the wrong force;
- lever arm drawn from the wrong pivot or joint axis;
- lever arm not perpendicular to the force line of action;
- wrong torque direction;
- wrong torque sign convention;
- wrong net torque direction;
- wrong angular-acceleration relation;
- wrong muscle selected as counter-torque;
- wrong equation term;
- wrong equation sign;
- correct setup but algebra error;
- correct number from wrong reasoning;
- wrong units or body-weight scaling.

### 2.4 First Project Milestone Is Worksheet-Pack Compatibility

The first coding path may be the static biceps curl task, but the first project milestone is **not** a single static vertical slice. The uploaded scenario worksheets are the source material for the first project milestone.

The first milestone is:

```text
Milestone 1: Worksheet-Pack Diagnostic Core
```

Milestone 1 must represent the full worksheet pack at worksheet fidelity. It must encode every uploaded worksheet family as a task fixture, compile every fixture, and provide at least one executable diagnostic path for each prompt type that can be checked from declared geometry, declared simplifications, or an instructor-provided answer key.

Required worksheet families in Milestone 1:

```text
1. Static biceps curl / elbow statics.
2. Overhead extension / elbow statics with optional arm-weight term.
3. Leg extension / knee statics.
4. Leg press / hip statics.
5. Squat with barbell / whole-person force balance plus hip, knee, and ankle torque analyses.
6. Foot upside-down seesaw / ankle torque and joint force.
7. Head seesaw / atlanto-occipital torque and joint force.
8. Lower-leg jump / worksheet-level qualitative rotational dynamics.
```

The first coding path should still be:

```text
elbow_biceps_curl_2d
```

because it exercises the essential loop: force inventory, force arrows, lever arms, torque directions, torque balance, lever-arm ratios, force equilibrium, joint force, diagnostics, and feedback. But biceps curl alone does not complete Milestone 1.

Milestone 1 includes worksheet-level qualitative dynamics from the lower-leg jump material:

```text
omega sign
alpha sign
net torque sign
floor-force torque direction
quadriceps/hamstrings torque direction
muscle dominance
signs in ± tau_M ± tau_n = ± I alpha
```

Milestone 1 does **not** include full dynamic simulation, gait simulation, finite element analysis, real-time control, reinforcement learning, high-fidelity anatomy meshes, or OpenSim/MuJoCo integration.

---

## 3. Layer Contracts

## 3.1 Engine Model

The engine is the formal substrate. It owns:

- anatomical frames;
- invertible rigid transforms between frames;
- typed quantities over frames;
- body-part systems;
- joint axes;
- force inventories;
- anatomical attachment regions;
- muscle origin/path/insertion data;
- force, line-of-action, lever-arm, torque, and wrench operations;
- static force equilibrium constraints;
- static torque equilibrium constraints;
- rotational-dynamics constraints;
- inequality constraints;
- solution-equivalence rules;
- structured diagnostic failures.

The engine speaks in internal types such as:

```text
Frame
Transform[A <- B]
Point[A]
Vector[A]
Force[A]
Torque[A]
Wrench[A]
LineOfAction[A]
LeverArm[A]
MuscleTension[Muscle]
AttachmentRegion[Frame]
BodyPartSystem
JointAxis[Frame]
ForceTorqueUnit
LearnerDiagram
ConstraintFailure
```

The engine must not produce final student-facing prose as its primary output. It must produce structured diagnostic objects.

Example:

```json
{
  "failure_type": "LEVER_ARM_NOT_PERPENDICULAR",
  "severity": "blocking",
  "force_id": "dumbbell_force",
  "joint_axis_id": "elbow_axis",
  "formal_details": {
    "expected": "lever arm perpendicular to dumbbell force line of action",
    "received": "learner lever arm angle differs from perpendicular by more than tolerance"
  },
  "downstream_failures": [
    "WRONG_TORQUE_MAGNITUDE",
    "EQUATION_NOT_EQUIVALENT",
    "NUMERIC_ERROR"
  ]
}
```

## 3.2 Task Compiler

The task compiler converts instructor-authored lesson specifications into formal engine constraints.

Input: declarative task specification.

Output:

- typed learner-action schema;
- hidden frame and anatomy constraints;
- visible student objects;
- hidden engine objects;
- force inventory;
- force-torque-unit requirements;
- allowed equations;
- allowed solution diagrams;
- equivalence rules;
- sign convention;
- lever-arm convention;
- diagnostic priority;
- hint policy;
- grading/rubric policy.

The compiler must reject invalid tasks before students see them.

Example invalid task:

```text
The instructor requires the student to draw the lever arm for the dumbbell force,
but the task has no joint axis or pivot specified.
```

Instructor-level compiler error:

```text
This task is unsolvable because a lever arm is required but no joint axis or pivot is visible or declared.
```

Not:

```text
No admissible morphism exists from ForceTorqueUnit to LeverArmConstraint.
```

## 3.3 Instructor Authoring Layer

The instructor authors lessons using educational terms, not engine terms.

Instructor-facing vocabulary:

```text
learning goal
scenario source
body-part system
joint axis
visible anatomy
hidden anatomy
force inventory
required lever arms
required torque directions
required sign convention
allowed muscles
allowed equations
difficulty level
hint sequence
diagnostic priority
rubric
simplifying assumptions
external data reference
```

The instructor should be able to author tasks declaratively in YAML or JSON.

## 3.4 Student Interaction Layer

The student manipulates lesson-level objects.

Student-facing objects:

```text
body part
joint axis
muscle
force arrow
line of action
lever arm
pivot
torque direction
rotation direction label
equation term
body weight
unknown force
joint force
angular velocity marker
angular acceleration marker
phase interval
```

Student-facing actions:

```text
select body-part system
click or drag joint axis
draw or drag force arrow
draw force line of action
draw or drag lever arm
choose torque direction
choose sign
choose counter-torque muscle
resize force vector to show relative magnitude
estimate lever-arm ratio
write or rearrange torque equation
write or rearrange force equation
enter numerical answer
select force-balance yes/no
select speed-up/slow-down classification
select concentric/eccentric classification
drag and resize muscle-dominance interval on a time graph
```

Student-facing language must not include internal engine terms such as:

```text
FrameGroupoid
TransportArrow
WrenchNaturality
Fiber
TaskGroupoid
CanonicalSolutionDiagram
```

unless an explicitly advanced mode is later implemented.

Each student action must be compiled into a typed learner diagram.

Example:

```text
Student action:
  Draws a dumbbell force arrow and a lever arm about the elbow.

Internal representation:
  ForceTorqueUnitCandidate {
    force_id: "dumbbell_force",
    applied_at: Point[HandOrDumbbellFrame],
    line_of_action: LineOfAction[WorldFrame],
    lever_arm: LeverArm[WorldFrame],
    joint_axis: JointAxis[ElbowFrame],
    claimed_torque_direction: "extension" or "flexion",
    displayed_as: StudentDiagramElements
  }
```

## 3.5 Diagnostic/Pedagogical Adapter

The diagnostic adapter maps engine failures to level-appropriate feedback.

The engine may detect a stack of formal failures:

```text
missing lever arm
lever arm not perpendicular
wrong torque direction
wrong equation sign
wrong numeric answer
```

The student should usually see only the earliest pedagogically relevant blocking error:

```text
The lever arm for the dumbbell force must be perpendicular to the dumbbell force's line of action.
```

After the student fixes that, the system may expose the next error:

```text
With extension defined as positive, this torque term should have a positive sign.
```

The adapter must support:

- diagnostic priority;
- difficulty-level language;
- hidden/visible constraint policy;
- hint sequencing;
- suppression of downstream errors;
- acceptance of equivalent correct methods;
- source-worksheet wording when an instructor wants the digital task to match a worksheet.

---

## 4. Internal Mathematical Foundation

## 4.1 Frame Groupoid

For each pose `q`, define a frame groupoid:

```text
FrameGroupoid(q)
```

Objects:

```text
WorldFrame
HumerusFrame
RadiusFrame
UlnaFrame
HandFrame
DumbbellFrame
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
AttachmentFrame
```

Arrows:

```text
Transform[A <- B](q)
```

Required laws:

```text
identity:   Transform[A <- A]
inverse:    inverse(Transform[A <- B]) = Transform[B <- A]
compose:    Transform[A <- B] composed with Transform[B <- C] = Transform[A <- C]
```

This is internal machinery for coordinate consistency and constraint validation.

## 4.2 Typed Quantity Bundles

Each frame has typed quantities over it:

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

The system must not permit operations on incompatible frames unless a valid transform is supplied.

Valid examples:

```text
Point[RadiusFrame] -> transport -> Point[WorldFrame]
Force[RadiusFrame] -> transport -> Force[WorldFrame]
LineOfAction[FootFrame] -> transport -> LineOfAction[WorldFrame]
LeverArm[WorldFrame] associated with JointAxis[AnkleFrame] after transport
```

Invalid example:

```text
cross(Point[RadiusFrame] - Point[WorldFrame], Force[HandFrame])
```

This must be rejected or internally repaired only if required transports are unambiguous and allowed by the task.

## 4.3 Force, Line of Action, Lever Arm, and Torque

For a force `f` applied at point `p`, torque about point `o` is:

```text
tau = (p - o) × f
```

The operation is valid only when `p`, `o`, and `f` have been transported into a common frame.

For a 2D introductory task, torque may be projected to:

```text
tau = F * r_perp
```

where `r_perp` is the perpendicular lever arm from the joint axis or pivot to the force line of action.

The lever arm is not the vector from the pivot to the point of force application unless that vector is perpendicular to the force. The engine must distinguish:

```text
radius vector r
perpendicular lever arm r_perp
line of action
moment arm / lever arm terminology
```

The worksheets use `lever arm` and `moment arm`; treat them as synonyms at the student level.

## 4.4 Torque Direction and Sign

For a task with joint axis `e`, the signed torque for force `i` is:

```text
sign_i = sign((r_i × F_i) dot e)
```

The student’s torque-direction answer must match the task’s declared rotation labels.

Supported rotation-label sets from the worksheets:

```text
flexion / extension
plantarflexion / dorsiflexion
clockwise / counterclockwise
positive / negative
zero torque
```

The task must declare the sign convention explicitly. Example from the lower-leg jump and overhead-extension worksheets:

```yaml
rotation_convention:
  positive: extension
  negative: flexion
```

Do not assume that all tasks use the same sign convention.

## 4.5 Wrench Transport

A wrench consists of torque and force:

```text
Wrench = (torque, force)
```

If a transform from frame `B` to frame `A` has rotation `R` and offset `r`, then:

```text
f_A   = R f_B
tau_A = R tau_B + r × f_A
```

This is engine-level behavior. It should not normally be exposed to students.

## 4.6 Muscles as Constrained Anatomical Spans

Represent each muscle as a constrained anatomical span:

```text
Muscle:
  origin_region: AttachmentRegion[FrameA]
  insertion_region: AttachmentRegion[FrameB]
  path: MusclePath(q)
  tension: F_i
  constraint: F_i >= 0
```

A muscle can pull along its path. It cannot push.

Internal muscle endpoint complementarity should be enforced:

```text
forces at origin and insertion are equal and opposite after transport into a common frame
```

Do not model agonist/antagonist pairs as literal inverses. They are relations in the anatomy graph and effects computed by geometry and mechanics.

For early worksheet tasks, a muscle may be represented either as:

1. a line-of-action force with attachment geometry; or
2. a direct joint torque label such as `quadriceps_torque` when the worksheet asks only for torque direction.

The task specification must state which representation is used.

## 4.7 Static Equilibrium

Static tasks must support:

```text
sum(forces) = 0
sum(torques) = 0
```

Common worksheet equations include:

```text
tau_muscle = tau_external
M * r_perp_M = F_external * r_perp_external
sum(tau) = 0
sum(F) = 0
J = combination of other forces with signs determined by convention
```

Torque equilibrium and force equilibrium are separate stages. A task may use torque equilibrium to estimate a muscle force and then force equilibrium to estimate a joint force.

## 4.8 Rotational Dynamics

The lower-leg jump task requires qualitative rotational dynamics:

```text
sum(tau) = I * alpha
```

The task must support:

```text
angular velocity sign
angular acceleration sign
net torque sign
floor-force torque sign
muscle torque sign
which force has the same torque direction as angular acceleration
which muscle torque must dominate
intervals where quadriceps dominate
intervals where hamstrings dominate
ignore-in-air intervals
```

For worksheet-level speed-up/slow-down classification:

```text
torque same direction as angular velocity -> speeds up that rotation
torque opposite angular velocity -> slows down that rotation
```

For worksheet-level concentric/eccentric classification, use the task’s declared convention. If not declared, use:

```text
muscle torque and angular velocity same sign -> concentric-like / positive rotational power
muscle torque and angular velocity opposite signs -> eccentric-like / negative rotational power
```

Do not expose the power equation unless the task level requires it.

## 4.9 Inequality-Constrained Physics

The physics layer must support:

```text
F_i >= 0                      # muscle tension only
0 <= activation_i <= 1         # later extension
q_min <= q <= q_max            # joint limits, later extension
normal_force >= 0              # contact
friction <= mu * normal_force  # contact, later extension
```

The MVP may use direct symbolic or numeric statics rather than a general optimizer.

---

## 5. Data Model Requirements

## 5.1 Core Types

Minimum Python dataclasses or equivalent:

```python
@dataclass(frozen=True)
class Frame:
    name: str

@dataclass(frozen=True)
class Transform:
    source: Frame
    target: Frame
    rotation: np.ndarray
    translation: np.ndarray

    def inverse(self) -> "Transform": ...
    def compose(self, other: "Transform") -> "Transform": ...

@dataclass(frozen=True)
class Point:
    frame: Frame
    coordinates: np.ndarray

@dataclass(frozen=True)
class Vector:
    frame: Frame
    components: np.ndarray

@dataclass(frozen=True)
class Force:
    frame: Frame
    components: np.ndarray

@dataclass(frozen=True)
class Torque:
    frame: Frame
    components: np.ndarray

@dataclass(frozen=True)
class LineOfAction:
    frame: Frame
    point: Point
    direction: Vector

@dataclass(frozen=True)
class JointAxis:
    frame: Frame
    point: Point
    direction: Vector

@dataclass(frozen=True)
class LeverArm:
    frame: Frame
    joint_axis: JointAxis
    force_line: LineOfAction
    signed_length: float | None
    student_geometry: object | None = None
```

## 5.2 Force-Torque Unit

Each force in the force inventory must compile to a force-torque unit.

```python
@dataclass(frozen=True)
class ForceTorqueUnit:
    force_id: str
    display_name: str
    force: Force | None
    line_of_action: LineOfAction | None
    application_point: Point | None
    required_application_region_id: str | None
    lever_arm: LeverArm | None
    torque_direction: str | None
    torque_sign: int | None
    equation_term_id: str | None
    required_for_torque_balance: bool
    required_for_force_balance: bool
    may_have_zero_torque: bool = False
```

## 5.3 Body-Part System and Task Context

```python
@dataclass(frozen=True)
class BodyPartSystem:
    id: str
    display_name: str
    included_segments: tuple[str, ...]

@dataclass(frozen=True)
class TaskContext:
    body_part_system: BodyPartSystem
    joint_axis: JointAxis
    rotation_convention: dict[str, str]
    assumptions: dict[str, object]
```

Examples of `body_part_system` from the worksheets:

```text
forearm_hand
lower_leg
lower_leg_foot
whole_leg
foot
head
whole_person
```

## 5.4 Anatomy Types

```python
@dataclass(frozen=True)
class Bone:
    name: str
    frame: Frame

@dataclass(frozen=True)
class Joint:
    name: str
    parent_bone: Bone
    child_bone: Bone
    frame: Frame
    rotation_labels: tuple[str, str]

@dataclass(frozen=True)
class AttachmentRegion:
    name: str
    frame: Frame
    center: Point
    radius: float

@dataclass(frozen=True)
class Muscle:
    name: str
    origin_region: AttachmentRegion | None
    insertion_region: AttachmentRegion | None
    max_tension: float | None = None
    allowed_joint_torque_labels: tuple[str, ...] = ()
```

For early tasks, approximate circular or spherical attachment regions are sufficient.

## 5.5 Learner Actions

Required action classes:

```python
@dataclass(frozen=True)
class SelectBodyPartSystem:
    body_part_system_id: str

@dataclass(frozen=True)
class ChooseJointAxis:
    point: Point
    direction: Vector | None
    claimed_joint: str

@dataclass(frozen=True)
class DrawForceArrow:
    force_id: str
    applied_at: Point | None
    direction: Vector
    magnitude: float | None
    claimed_muscle: str | None = None

@dataclass(frozen=True)
class DrawLineOfAction:
    force_id: str
    line: LineOfAction

@dataclass(frozen=True)
class DrawLeverArm:
    force_id: str
    lever_arm: LeverArm

@dataclass(frozen=True)
class SelectTorqueDirection:
    force_id: str
    direction_label: str

@dataclass(frozen=True)
class SelectTorqueSign:
    force_id: str
    sign: int

@dataclass(frozen=True)
class ChooseCounterTorqueMuscle:
    force_id_to_counter: str
    muscle_id: str

@dataclass(frozen=True)
class ResizeForceVector:
    force_id: str
    relative_magnitude: float

@dataclass(frozen=True)
class EstimateLeverArmRatio:
    numerator_force_id: str
    denominator_force_id: str
    ratio: float

@dataclass(frozen=True)
class EquationSubmission:
    expression: str
    claimed_equation_type: str

@dataclass(frozen=True)
class SignSelectionSubmission:
    equation_template_id: str
    selected_signs: dict[str, int]

@dataclass(frozen=True)
class NumericAnswer:
    variable: str
    value: float
    units: str

@dataclass(frozen=True)
class PhaseIntervalSelection:
    graph_id: str
    interval_start: float
    interval_end: float
    selected_label: str
```

## 5.6 Diagnostic Failures

Implement a failure enum at least as broad as:

```python
class FailureType(Enum):
    TASK_UNSOLVABLE = auto()
    MISSING_BODY_PART_SYSTEM = auto()
    WRONG_BODY_PART_SYSTEM = auto()
    MISSING_JOINT_AXIS = auto()
    WRONG_JOINT_AXIS = auto()
    MISSING_REQUIRED_FORCE = auto()
    EXTRA_IRRELEVANT_FORCE = auto()
    INVALID_ATTACHMENT_REGION = auto()
    WRONG_MUSCLE_ATTACHMENT = auto()
    WRONG_FORCE_APPLICATION_POINT = auto()
    WRONG_FORCE_DIRECTION = auto()
    MISSING_LINE_OF_ACTION = auto()
    WRONG_LINE_OF_ACTION = auto()
    MISSING_LEVER_ARM = auto()
    LEVER_ARM_WRONG_FORCE = auto()
    LEVER_ARM_WRONG_PIVOT = auto()
    LEVER_ARM_NOT_PERPENDICULAR = auto()
    LEVER_ARM_WRONG_LENGTH = auto()
    WRONG_TORQUE_DIRECTION = auto()
    WRONG_TORQUE_SIGN = auto()
    WRONG_NET_TORQUE_DIRECTION = auto()
    WRONG_COUNTER_TORQUE_MUSCLE = auto()
    MISSING_TORQUE_TERM = auto()
    EXTRA_TORQUE_TERM = auto()
    EQUATION_NOT_EQUIVALENT = auto()
    WRONG_EQUATION_SIGN = auto()
    WRONG_FORCE_BALANCE_TERM = auto()
    WRONG_JOINT_FORCE_DIRECTION = auto()
    WRONG_JOINT_FORCE_MAGNITUDE = auto()
    WRONG_BODY_WEIGHT_SCALING = auto()
    NUMERIC_ERROR = auto()
    UNIT_ERROR = auto()
    WRONG_ANGULAR_VELOCITY_SIGN = auto()
    WRONG_ANGULAR_ACCELERATION_SIGN = auto()
    WRONG_TORQUE_ALPHA_RELATION = auto()
    WRONG_MUSCLE_DOMINANCE = auto()
    WRONG_SPEED_UP_SLOW_DOWN_CLASSIFICATION = auto()
    WRONG_CONCENTRIC_ECCENTRIC_CLASSIFICATION = auto()
    FRAME_TYPE_ERROR = auto()
    INTERNAL_CONSTRAINT_ERROR = auto()
```

Each failure should include:

```python
@dataclass(frozen=True)
class ConstraintFailure:
    failure_type: FailureType
    severity: str
    message_key: str
    formal_details: dict
    downstream_failures: list[FailureType]
```

---

## 6. Instructor Task Schema Requirements

Every task file must include these sections.

```yaml
task_id: string
title: string
source_worksheet: string
level: introductory_physics | intermediate | advanced

body_part_system:
  id: string
  display_name: string

joint_axis:
  id: string
  joint: string
  display_name: string
  visible_to_student: true

rotation_convention:
  positive: string
  negative: string
  zero: zero
  display_labels: [string]

assumptions:
  planar: true
  static: true
  rigid_segments: true
  ignored_forces: []
  simplifications: []

force_inventory:
  - id: string
    display_name: string
    kind: external_load | muscle_force | joint_force | contact_force | weight | direct_muscle_torque
    required_for_torque_balance: true | false
    required_for_force_balance: true | false
    student_must_draw_force: true | false
    student_must_draw_line_of_action: true | false
    student_must_draw_lever_arm: true | false
    student_must_identify_torque_direction: true | false
    student_must_select_sign: true | false
    may_have_zero_torque: true | false

student_actions: []
allowed_equations: []
diagnostics: {}
hints: {}
rubric: {}
external_references: []
```

External references are metadata only in the MVP.

---

## 7. Worksheet-Derived Task Templates

The following task templates must exist as YAML fixtures for Milestone 1. Each fixture must include `source_worksheet`, `status`, and `coverage_level` fields. In Milestone 1, every fixture must compile. Each worksheet family must provide at least one executable diagnostic path for each prompt type that can be checked from declared geometry, declared simplifications, or an instructor-provided answer key. If a prompt cannot be checked without missing geometry, the fixture must mark that prompt `requires_instructor_key` or `requires_declared_geometry`; the compiler must not invent an answer.

## 7.1 `elbow_biceps_curl_2d`

Source: `Activity Biceps Curl2d.pptx`.

Scenario:

```text
A person holds the forearm/hand still while holding a dumbbell. The weight of the arm itself is neglected in the first analysis. Forces and torques on the forearm/hand must balance.
```

Body-part system:

```text
forearm/hand
```

Joint:

```text
elbow
```

Required force inventory:

```text
dumbbell force
biceps muscle force or triceps muscle force choice
elbow joint force in later force-equilibrium section
```

Required student work:

```text
draw dumbbell force
draw dumbbell lever arm
identify dumbbell torque direction
show elbow axis
choose counter-torque muscle from biceps/triceps
draw muscle force
draw muscle lever arm
identify muscle torque direction
estimate lever-arm ratio
resize force vectors to show relative magnitude
compute muscle force for a 10 lb dumbbell when specified
choose signs in force equilibrium
compute elbow joint force
body-weight scaling prompt when instructor supplies standards value
```

Equations:

```text
sum(tau) = 0
tau_muscle = tau_dumbbell
M * r_perp_M = F_dumbbell * r_perp_dumbbell
sum(F) = 0
sign choices for M, F_dumbbell, and J_elbow
```

Assumptions:

```text
arm weight neglected in first analysis
forearm/hand not moving
all forces vertical in later force-equilibrium section, when declared
```

## 7.2 `elbow_overhead_extension_2d`

Source: `Activity overhead extension 3.pptx`.

Scenario:

```text
A forearm/hand performs or holds an overhead extension with a dumbbell. The task asks for torque directions and lever arms of the dumbbell, the weight of the forearm/hand, and the muscle force. Later prompts simplify by neglecting the forearm/hand weight, then ask what changes if that weight is included.
```

Body-part system:

```text
forearm/hand
```

Joint:

```text
elbow
```

Rotation convention:

```text
extension positive
flexion negative
```

Required force inventory:

```text
dumbbell force
forearm/hand weight, when included
triceps or biceps muscle force choice
elbow joint force in force-equilibrium section
```

Required student work:

```text
draw torque directions and lever arms for dumbbell and arm weight
choose counter-torque muscle from triceps/biceps
draw muscle force, torque direction, and lever arm
choose correct torque-balance equation with signs
show algebraic relation between muscle force and lever-arm ratio
estimate muscle force for 10 lb dumbbell when specified
resize muscle force relative to dumbbell
choose force-equilibrium signs
compute elbow joint force
use body-weight prompt when instructor supplies or declares dumbbell body-weight ratio
compare simplified result with result including arm weight
```

Equations:

```text
sum(tau_forearm_hand) = 0
signed torque equations with extension positive and flexion negative
tau_muscle = tau_dumbbell in simplified case
F_muscle / F_dumbbell = r_perp_dumbbell / r_perp_muscle
sum(F) = 0
J_elbow = signed combination of F_muscle and F_dumbbell
with arm weight: tau_M = tau_Warm + tau_Fdumbbell
with arm weight: J = W_arm + M_triceps + F_dumbbell under the worksheet's vertical-force simplification
```

Explicit constants allowed when task declares them:

```text
dumbbell = 10 lb
F_dumbbell = 0.45 Wbody
W_arm = 0.02 * 115 lb
```

## 7.3 `knee_leg_extension_2d`

Source: `Activity Leg Extension3.pptx`.

Scenario:

```text
A leg-extension machine's padded bar presses down on the top of the person's foot while the person holds still. Torques about the knee balance.
```

Body-part system:

```text
lower leg/foot or lower leg, following the task prompt
```

Joint:

```text
knee
```

Required force inventory:

```text
bar force on top of foot
quadriceps or hamstrings muscle force choice
knee joint force only if a later extension adds force equilibrium
```

Required student work:

```text
draw bar force on top of foot
place knee joint dot
draw bar-force lever arm
identify bar-force torque direction
choose counter-torque muscle from quadriceps/hamstrings
draw muscle force placement and direction
identify each muscle force's torque direction
redraw force vectors and lever arms
estimate lever-arm ratio
resize force vectors to show relative values
compute muscle force relative to bar force and body weight when instructor supplies data
```

Equations:

```text
sum(tau) = 0
tau_muscle = tau_bar
M * r_perp_M = F_bar * r_perp_bar
M = F_bar * (r_perp_bar / r_perp_M)
```

Body-weight scaling:

```text
F_bar on one leg is half of the two-leg standard when the standard refers to both legs.
```

## 7.4 `hip_leg_press_2d`

Source: `Activity Leg press 3b.pptx`.

Scenario:

```text
A person holds a leg-press platform still. The task focuses on the whole leg about the hip.
```

Body-part system:

```text
whole leg
```

Joint:

```text
hip
```

Required force inventory:

```text
platform force on leg/foot
psoas or gluteus maximus muscle force choice
```

Required student work:

```text
draw each candidate muscle force and torque direction
draw and reorient platform force on leg/foot
draw lever arms for each force
estimate lever-arm ratio
identify torque direction of platform force
choose counter-torque muscle from gluteus/psoas
use per-leg platform force when standards value is for both legs
show strategy from sum(tau)=0
rearrange equation to isolate muscle force in terms of lever-arm ratio and Wbody
```

Equations:

```text
sum(tau) = 0
tau_M = tau_platform
M * r_perp_M = F_platform * r_perp_platform
M = F_platform * (r_perp_platform / r_perp_M)
```

## 7.5 `squat_barbell_multi_joint_2d`

Source: `Squat with barbell Jc.pptx`.

Scenario:

```text
A person squats with a barbell. The worksheet first treats whole-person force equilibrium, then studies the torque effect of the left floor normal force about the hip, knee, and ankle as separate lever systems.
```

Whole-person force equilibrium:

```text
F_barbell = 3 Wbody
forces include Wbody, F_barbell, n_left, n_right
assume n_left = n_right
solve n_left in terms of Wbody
```

Lever systems:

```text
whole leg about hip
lower leg/foot about knee
foot about ankle
```

Required student work:

```text
choose signs for whole-person vertical force equilibrium
solve left and right floor normals under equal-normal assumption
identify torque direction of n_left about hip, knee, and ankle
choose counter-torque muscle around hip from glute/psoas
choose counter-torque muscle around knee from quads/hamstrings
choose counter-torque muscle around ankle from Achilles/calf or tibialis
draw muscle vectors and torque directions
draw lever arms
estimate ratio of lever arms
calculate muscle force in terms of n_left and Wbody
```

Equations:

```text
sum(F) = 0
n_left = n_right under declared assumption
sum(tau) = 0
tau_M = tau_floor
n * r_perp_n = M * r_perp_M
M = n * (r_perp_n / r_perp_M)
```

Task-specific note:

```text
The worksheet notes that the picture is not at the best angle. The task spec must declare whether the digital model uses a simplified instructor-approved geometry or requires an instructor answer key.
```

## 7.6 `ankle_foot_upside_down_seesaw_2d`

Source: `Activity Foot - upside down seesawc.pptx`.

Scenario:

```text
The foot is treated as a lever about the ankle. The floor normal acts on the foot, the Achilles/calf or tibialis provides counter-torque, and the ankle joint force is introduced when force balance is considered.
```

Body-part system:

```text
foot
```

Joint:

```text
ankle
```

Required force inventory:

```text
floor normal n_floor
Achilles/calf or tibialis muscle force choice
ankle joint force in force-balance section
foot weight omitted or neglected when declared
```

Required student work:

```text
identify floor-force torque direction as dorsiflexion or plantarflexion
choose counter-torque muscle from Achilles/calf or tibialis
identify torque direction of each muscle force
draw lever arms for floor normal and Achilles force
estimate Achilles force relative to body weight using lever-arm ratio
select visual lever-arm ratio from options when offered
resize Achilles vector relative to floor normal
answer whether displayed forces are balanced
identify need for ankle joint force
draw muscle-force components Mx/My when required
draw joint-force components Jx/Jy when required
estimate joint force relative to body weight
use simplified vertical-force approximation when declared
choose signs in force equilibrium
critique an external diagram by checking torque balance, without asserting a conclusion unless the task has an instructor key
```

Equations:

```text
n_floor = Wbody when declared
sum(tau) = 0
+ tau_Achilles - tau_floor = 0
tau_Achilles = tau_floor
F_Achilles * r_perp_Achilles = n_floor * r_perp_floor
F_Achilles = n_floor * (r_perp_floor / r_perp_Achilles)
sum(Fx) = 0
sum(Fy) = 0
simplified: + F_Achilles + n_floor ∓ J = 0
```

## 7.7 `head_atlanto_occipital_seesaw_2d`

Source: `Activity Head as seesawb.pptx`.

Scenario:

```text
The head is treated as a seesaw about the atlanto-occipital joint. Head weight and neck muscle force produce opposing torques; joint force is then estimated from force equilibrium.
```

Body-part system:

```text
head
```

Joint:

```text
atlanto-occipital joint
```

Required force inventory:

```text
head weight W_head
neck muscle force
joint force J in force-balance section
```

Required student work:

```text
draw or identify r and r_perp for weight and muscle force
estimate head weight from body weight when instructor supplies data
estimate neck muscle force by lever-arm ratio
compute or estimate joint force
```

Equations:

```text
sum(tau_head) = 0
+ tau_weight_head = tau_muscle
F_neck_muscle * r_perp_muscle = W_head * r_perp_W
F_neck_muscle = W_head * (r_perp_W / r_perp_muscle)
sum(F_head) = 0
-W_head - F_muscle + J = 0
J = W_head + F_muscle
```

## 7.8 `knee_lower_leg_jump_dynamics`

Source: `Activity Which muscle when lower leg knee partially done.pptx`.

Scenario:

```text
The lower leg-foot rotates about the knee during a jump. The worksheet uses theta, omega, and alpha time graphs; ignores in-air intervals; and uses flexion negative and extension positive.
```

Body-part system:

```text
lower leg-foot
```

Joint:

```text
knee
```

Rotation convention:

```text
flexion negative
extension positive
```

Required force/torque inventory:

```text
floor normal torque n
quadriceps muscle torque
hamstrings muscle torque
net torque
```

Required student work:

```text
read or assign angular velocity sign
read or assign angular acceleration sign
identify torque direction of floor force n about the knee
identify quadriceps torque direction
identify hamstrings torque direction
select which muscle torque can speed up or slow down flexion/extension
classify concentric/eccentric when task asks
indicate whether floor force can cause the indicated angular acceleration
if not, select quadriceps or hamstring as needed muscle
assign signs in ± tau_M ± tau_n = ± I alpha
select which force has the same torque direction as angular acceleration
drag/resize intervals where quadriceps dominate
drag/resize intervals where hamstrings dominate
ignore in-air interval
```

Equations and rules:

```text
sum(tau) = I * alpha
sign(sum(tau)) = sign(alpha)
force torque same sign as alpha can contribute to required angular acceleration
muscle dominance interval must align with declared or computed torque requirements
```

## 7.9 `knee_leg_extension_and_squat_knee_shared_template`

This is not a separate worksheet task. It is a reusable template extracted from the leg-extension and squat-knee worksheets.

It must support:

```text
lower leg/foot about knee
external force creates flexion or extension torque
quadriceps and hamstrings as candidate counter-torque muscles
lever-arm ratio estimate
muscle force from M * r_M = F * r_F
```

Use this template to reduce duplicated code across leg extension, squat knee, and lower-leg dynamic tasks.

---

## 8. Diagnostic Hierarchy

Use this default order unless a task overrides it.

```text
1. task unsolvable or missing instructor key
2. wrong or missing body-part system
3. wrong or missing joint axis
4. missing required force
5. extra irrelevant force
6. wrong force application point or attachment
7. wrong force direction
8. missing line of action
9. wrong line of action
10. missing lever arm for a force
11. lever arm associated with wrong force
12. lever arm drawn from wrong pivot or joint axis
13. lever arm not perpendicular to force line of action
14. lever-arm length or ratio wrong
15. wrong torque direction for force
16. wrong torque sign under convention
17. wrong counter-torque muscle
18. wrong net torque direction
19. wrong relation between net torque and angular acceleration
20. wrong speed-up/slow-down or concentric/eccentric classification
21. missing torque term
22. extra torque term
23. wrong equation sign
24. equation not equivalent to allowed solution
25. wrong body-weight scaling or per-leg scaling
26. wrong force-balance term
27. wrong joint-force direction
28. wrong joint-force magnitude
29. algebra/numeric/unit error
30. correct
```

Do not report downstream errors before upstream diagram errors are fixed.

Example:

```text
If the dumbbell lever arm is not perpendicular, do not yet report the equation-sign error caused by that lever arm.
```

---

## 9. Visibility and Simplification Policy

Every object and constraint must support visibility metadata.

Visibility options:

```text
visible_to_student
visible_to_instructor
visible_after_hint
visible_after_error
hidden_but_checked
hidden_until_advanced_mode
engine_only
```

Every task must declare simplifications explicitly.

Common worksheet simplifications:

```text
planar model
body part held still
static equilibrium
rigid segments
arm weight neglected
foot weight neglected
all forces vertical
platform force split evenly between two legs
left/right floor normals equal
in-air interval ignored
muscle represented as direct joint torque
external standards value supplied by instructor
```

Simplifications are not anatomical truths. They are task assumptions.

---

## 10. Equivalent Solution Handling

Correctness must not mean matching one hard-coded solution path.

For each task, define allowed solution forms.

Examples:

```text
using tau_muscle = tau_external
using sum(tau) = 0 with signed terms
using force times lever-arm terms directly
symbolic rearrangement before numeric substitution
visual lever-arm ratio followed by numeric estimate
force balance using sign choices
```

A learner solution is correct when it maps into an allowed solution representation under the task assumptions.

---

## 11. Repository Structure

Use this structure unless a strong reason emerges to change it.

```text
biomech-tutor/
  README.md
  DESIGN_CONTRACT.md
  PROJECT_PROPOSAL.md
  pyproject.toml

  biomech_tutor/
    __init__.py

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
      test_muscle_span.py
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

---

## 12. Tests Required Before UI Work

Do not begin graphical UI until these tests pass.

## 12.1 Groupoid Tests

```text
identity transform leaves points/vectors unchanged
inverse(transform) composes to identity
composition is associative within numerical tolerance
invalid composition is rejected
```

## 12.2 Quantity Typing Tests

```text
cannot subtract points in different frames without transport
cannot cross incompatible quantities
cannot compute torque from mismatched point/force frames
transported torque calculation agrees with direct calculation after transport
wrench transport preserves force/torque relationship
```

## 12.3 Force-Torque Unit Tests

```text
force line of action can be constructed from point and direction
lever arm is perpendicular to line of action
lever arm length equals point-to-line distance in 2D fixture
zero-torque force recognized when line of action passes through joint axis
torque direction matches cross-product sign and declared rotation labels
sign convention can be changed without changing geometry
```

## 12.4 Static Worksheet Task Tests

For each static worksheet-derived task fixture:

```text
task compiles
force inventory is nonempty
every force requiring torque has lever-arm and torque-direction requirements
required equations reference declared force IDs only
external references are metadata only
unknown numeric constants are placeholders unless declared
```

## 12.5 Biceps Curl Vertical-Slice Tests

```text
wrong elbow axis produces joint-axis feedback
missing dumbbell force produces missing-force feedback
wrong dumbbell force direction produces force-direction feedback
missing dumbbell lever arm produces lever-arm feedback
nonperpendicular dumbbell lever arm produces lever-arm feedback
wrong dumbbell torque direction produces torque-direction feedback
wrong counter-torque muscle produces muscle feedback
wrong muscle lever arm produces lever-arm feedback
correct torque diagram but wrong equation produces equation feedback
correct equation but wrong number produces numeric feedback
correct torque and force-balance solution accepted
```

## 12.6 Lower-Leg Dynamics Tests

```text
flexion negative / extension positive convention loaded
wrong omega sign diagnosed
wrong alpha sign diagnosed
wrong floor-force torque direction diagnosed
wrong quadriceps torque direction diagnosed
wrong hamstrings torque direction diagnosed
wrong force selected for alpha direction diagnosed
wrong signs in ± tau_M ± tau_n = ± I alpha diagnosed
wrong muscle dominance interval diagnosed
in-air interval ignored when declared
```

---

## 13. Development Order

Implement in this order. This is coding order, not milestone scope:

```text
1. Source worksheet inventory and canonical label map.
2. Task schema fields needed by every worksheet fixture.
3. Core frames and transforms.
4. Typed quantities.
5. Force line-of-action model.
6. Lever-arm model.
7. Torque-direction/sign model.
8. Static torque-balance utilities.
9. Static force-balance utilities.
10. Minimal forearm/hand and elbow anatomy model.
11. Biceps curl task fixture and text demo as the first executable path.
12. Diagnostic hierarchy and adapter.
13. Task compiler validation.
14. Overhead extension task fixture.
15. Leg extension task fixture.
16. Leg press task fixture.
17. Foot/ankle task fixture.
18. Head/atlanto-occipital task fixture.
19. Squat multi-joint task fixture.
20. Lower-leg jump qualitative dynamics fixture and text demo.
21. Regression tests across all worksheet fixtures.
22. Only then begin graphical interaction.
```

Milestone 1 is complete only after the worksheet pack is represented, compiler-validated, and covered by executable or instructor-key-gated diagnostics. A polished biceps curl demo is necessary but insufficient.

---

## 14. Prohibited Early Work

Do not start with:

```text
full-body model
walking simulation
finite element analysis
high-fidelity 3D anatomy meshes
general OpenSim import
machine learning
reinforcement learning
web scraping strength standards
complex graphical UI
game engine integration
```

These may come later. They are not part of Milestone 1. The lower-leg jump worksheet is an exception only in its worksheet-level qualitative form: signs of omega, alpha, net torque, torque direction, muscle dominance, and equation signs. Do not implement it as full continuous motion simulation in Milestone 1.

---

## 15. Milestone 1 Acceptance Criteria: Worksheet-Pack Diagnostic Core

Milestone 1 is complete only when all of the following are true.

### 15.1 Global acceptance

```text
1. Every uploaded worksheet family has a YAML fixture.
2. Every fixture declares source_worksheet, body_part_system, joint_axis, rotation labels, force inventory, required force-torque units, allowed equations, declared simplifications, missing-data policy, diagnostics, and status.
3. Every fixture compiles.
4. Every prompt that cannot be checked from declared geometry or declared simplifications is marked requires_instructor_key or requires_declared_geometry.
5. The compiler rejects under-specified answer generation instead of inventing values.
6. At least one executable diagnostic path exists for every worksheet prompt type represented in the pack.
7. Unit tests cover every fixture.
8. The text demo can run at least the biceps curl and lower-leg qualitative dynamics paths.
9. The package supports: `pytest`, `python -m biomech_tutor.tasks.validate_all`, `python -m biomech_tutor.demo.elbow_biceps_curl_2d`, and `python -m biomech_tutor.demo.knee_lower_leg_jump_dynamics`.
```

### 15.2 Static biceps curl acceptance

```text
1. Load elbow_biceps_curl_2d task.
2. Validate task specification.
3. Present student-level objects from the task projection.
4. Diagnose wrong elbow axis.
5. Diagnose missing dumbbell force.
6. Diagnose missing dumbbell lever arm.
7. Diagnose lever arm drawn for the wrong force.
8. Diagnose nonperpendicular lever arm.
9. Diagnose wrong dumbbell torque direction.
10. Diagnose wrong counter-torque muscle.
11. Diagnose wrong muscle force direction or placement.
12. Diagnose wrong muscle lever arm.
13. Diagnose wrong torque-balance equation.
14. Accept equivalent valid torque equation.
15. Diagnose wrong muscle-force numerical estimate.
16. Proceed to force-equilibrium section.
17. Diagnose wrong elbow-joint-force direction or sign.
18. Accept correct joint-force result.
```

### 15.3 Other static worksheet fixtures

For each of these fixtures:

```text
elbow_overhead_extension_2d
knee_leg_extension_2d
hip_leg_press_2d
squat_barbell_multi_joint_2d
ankle_foot_upside_down_seesaw_2d
head_atlanto_occipital_seesaw_2d
```

Milestone 1 must support:

```text
1. load fixture;
2. validate fixture;
3. list required body-part systems and joint axes;
4. list required force inventory;
5. list required lever arms and torque-direction prompts;
6. list required torque-balance and/or force-balance equations;
7. diagnose at least one representative wrong answer for every prompt type present in that worksheet;
8. accept at least one correct answer path if declared geometry or instructor key is available;
9. mark missing-geometry prompts as requires_declared_geometry or requires_instructor_key without inventing answers.
```

The squat fixture must additionally support switching the analyzed lever system among:

```text
whole person force equilibrium
whole leg about hip
lower leg/foot about knee
foot about ankle
```

### 15.4 Lower-leg qualitative dynamics acceptance

```text
1. Load knee_lower_leg_jump_dynamics task.
2. Validate flexion-negative / extension-positive convention.
3. Ignore in-air intervals when declared.
4. Diagnose wrong omega sign.
5. Diagnose wrong alpha sign.
6. Diagnose wrong floor-force torque direction.
7. Diagnose wrong quadriceps torque direction.
8. Diagnose wrong hamstrings torque direction.
9. Diagnose wrong force or muscle selected for required alpha.
10. Diagnose wrong signs in ± tau_M ± tau_n = ± I alpha.
11. Diagnose wrong speed-up/slow-down classification when enabled.
12. Diagnose wrong concentric/eccentric classification when enabled.
13. Diagnose wrong dominance intervals for quadriceps/hamstrings.
14. Accept correct qualitative dynamic reasoning.
```

---

## 16. First Demo Interface

A text-based or notebook-based demo is acceptable.

Example static interaction:

```text
Task: Biceps curl, forearm/hand held still with a dumbbell.

Student submission:
  elbow_axis = wrong point

System:
  The torque diagram must use the elbow as the joint axis for this body part.

Student submission:
  elbow_axis = elbow
  dumbbell_force = downward
  dumbbell_lever_arm = omitted

System:
  Draw the lever arm for the dumbbell force before writing the torque equation.

Student submission:
  dumbbell_lever_arm = not perpendicular

System:
  The lever arm for the dumbbell force must be perpendicular to the dumbbell force's line of action.
```

Example dynamics interaction:

```text
Task: Lower leg-foot rotation about knee during jump.
Convention: flexion negative, extension positive.

Student submission:
  alpha_sign = positive
  selected_working_force = hamstrings

System:
  With extension defined as positive, a positive angular acceleration requires a positive net torque. Check whether the selected force produces extension or flexion torque.
```

---

## 17. Design Philosophy

Keep the engine formal and the pedagogy controlled.

The student constructs a pedagogical force-torque diagram.

The engine validates a typed biomechanical diagram.

The diagnostic adapter translates formal failures into level-appropriate feedback.

The instructor controls what is visible, what is hidden, what is tested, and what kind of feedback is appropriate.

The groupoid-indexed machinery is infrastructure for correctness, extensibility, and diagnosis.
