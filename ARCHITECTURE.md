# Architecture

## Goal

The system separates creative planning from constraint verification so that a plausible-looking trailer cannot automatically become an approved trailer.

## Components

### 1. Data Loader
Loads:

- episode scenes
- subtitles
- audiences
- policies
- contracts
- historical performance
- cost configuration

### 2. Story Map Agent

Produces:

- characters
- relationships
- major events
- emotional turns
- protected spoilers
- sensitive-content flags

The story map is source-grounded in the episode package.

### 3. Constraint Map Agent

Converts policy and contract information into testable rules.

Each rule records:

- constraint ID
- category
- rule type
- description
- severity
- audience when applicable
- affected assets
- territory
- evidence

### 4. Audience Promise Agent

Defines what the trailer should promise before clip selection.

This prevents historical engagement from becoming the only planning signal.

### 5. Trailer Planner Agent

Selects and orders source scenes according to:

- audience promise
- spoiler limits
- safety limits
- subtitle availability
- audience-specific strategy
- source evidence

### 6. Independent Validator

Checks the generated plan independently.

Checks include:

- source timecode grounding
- spoiler rules
- frightening-content limits
- suggestive-content rules
- subtitle requirements
- actor promotional rights
- music promotional rights
- music expiry
- dialect source grounding

### 7. Recovery Agent

Handles selected change events.

The recovery flow is:

```text
Change event
    |
    v
Identify affected decisions
    |
    v
Repair affected decision
    |
    v
Re-run independent validation
    |
    v
Append decision log
```

### 8. Change Log

The decision log preserves recovery events with:

- event
- audience
- affected decisions
- recovery action
- validation status
- timestamp

## Why deterministic rules are used

For the challenge demo, deterministic rules make the verification path observable and reproducible. A production version could place an LLM/multimodal model behind the same interfaces while keeping policy and rights checks independently testable.

## Failure boundaries

The system should reject or escalate when:

- source evidence is missing
- a scene cannot be grounded
- a rights restriction blocks use
- a policy threshold is exceeded
- required accessibility information is unavailable
- cultural/dialect treatment cannot be verified
- an external change invalidates a previous decision
