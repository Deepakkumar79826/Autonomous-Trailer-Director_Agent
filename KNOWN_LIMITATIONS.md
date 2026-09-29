# Known Limitations

## 1. Synthetic episode package

The challenge PDF supplied the requirements but not a real episode media package. The repository therefore uses synthetic episode metadata, subtitles, policies, contracts, performance data, and cost data.

## 2. No final video rendering

The implementation produces trailer plans rather than rendered video files.

The plans contain source timecodes, ordering, audio/subtitle information, reasons, evidence, and risk flags.

## 3. Deterministic planning

The current planner is deterministic rather than powered by a production multimodal model.

This is intentional for reproducibility and verification in the take-home demo.

## 4. Mock/replay changes

Change events are simulated from known challenge scenarios.

A production system would receive contract, catalog, rights, or editorial events from external systems.

## 5. Limited cultural validation

Dialect-region treatment is represented through source-grounded rules and subtitle-track selection. A production system should include qualified regional/cultural review.

## 6. Rights interpretation

The validator checks structured contract fields. Ambiguous legal language would require human/legal escalation.

## 7. Audio/video understanding

The challenge implementation uses structured episode metadata rather than extracting facts directly from raw video/audio.

## 8. Human approval

The system reports decisions and validation status but does not make the final release decision.

## 9. Cost model

The supplied cost configuration is synthetic and is not a production cloud-cost estimate.
