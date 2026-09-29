# AI Collaboration Note

## How AI tools were used

AI assistance was used during implementation to:

- decompose the challenge into implementation stages
- design data models
- draft deterministic agent logic
- generate test cases
- identify interface mismatches during test failures
- improve CLI ergonomics
- review architecture and failure-recovery behavior

## Where deterministic verification was preferred

The project deliberately does not allow an AI-generated creative decision to become an approved trailer by itself.

The following remain deterministic and independently testable:

- source timecode matching
- spoiler thresholds
- frightening-content thresholds
- suggestive-content policy
- subtitle presence
- actor promotional rights
- music promotional rights
- contract expiry
- change-event validation

## Hallucination control

The synthetic episode package contains explicit scene IDs and exact timecodes.

The planner only references scenes that exist in the loaded package.

The validator independently resolves trailer segments back to source timecodes.

Therefore a plausible but nonexistent scene should fail validation rather than silently pass.

## Human review

AI assistance does not replace:

- legal/contract interpretation
- final cultural review
- final safety approval
- marketing approval
- final release approval

## Reproducibility

The current challenge implementation is deterministic so that an evaluator can replay the same package and inspect the same decisions and validation evidence.
