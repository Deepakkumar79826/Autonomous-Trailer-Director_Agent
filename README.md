# Autonomous Trailer Director

## OTT Dialect Platform — AI Engineering Hiring Challenge

**Project:** Autonomous Trailer Director  
**Episode:** The Last Lantern (EP001)  
**Mode:** Synthetic evaluation package / deterministic replay demo

## 1. What this project does

The Autonomous Trailer Director turns one episode package into three audience-specific trailer plans:

- **Family viewers** — warmth, family/community context, safe mystery
- **Young adult viewers** — mystery, tension, emotional conflict
- **Dialect-region viewers** — regional context and respectful dialect treatment

The system does not select scenes from engagement history alone. It first builds a source-grounded story map, converts policies/contracts into constraints, defines an audience promise, plans clips, independently validates the result, and can selectively recover from changes.

## 2. Architecture

```text
                    Episode Package
                           |
                           v
                  +------------------+
                  |   Story Agent    |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Constraint Agent|
                  +------------------+
                           |
                           v
                +---------------------+
                | Audience Promise   |
                +---------------------+
                           |
                           v
                  +------------------+
                  | Trailer Planner   |
                  +------------------+
                           |
                           v
                  +------------------+
                  | Independent      |
                  | Validator        |
                  +------------------+
                           |
                    PASS / REJECT
                           |
                           v
                  +------------------+
                  | Recovery Agent   |
                  +------------------+
                           |
                           v
                    Decision Log
```

## 3. Important design choices

### Source grounding
Trailer segments use exact source timecodes from `data/episode/episode.json`.

### Spoiler protection
Protected spoilers are explicitly represented in the story map. The planner avoids the central twist, and the independent validator checks spoiler limits separately.

### Rights verification
Actor and music contracts are checked independently of planner selection.

### Audience personalization
Each audience receives a distinct promise and scene strategy rather than three copies of the same trailer.

### Human control
The system reports evidence, risks, assumptions, and validation status. Final release approval remains a human decision.

### Recovery
Change events such as music-rights expiry can trigger selective repair and re-validation without treating the entire previous plan as invalid.

## 4. Project structure

```text
autonomous-trailer-director/
├── README.md
├── ARCHITECTURE.md
├── AI_COLLABORATION.md
├── KNOWN_LIMITATIONS.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── src/
│   └── trailer_director/
├── data/
│   ├── episode/
│   ├── policies/
│   ├── contracts/
│   ├── audiences/
│   ├── performance/
│   └── cost/
├── tests/
└── sample_run/
```

## 5. Setup

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

$env:PYTHONPATH="src"
```

## 6. Validate the data package

```powershell
python -m trailer_director.validate_data
```

Expected:

```text
DATA PACKAGE VALID
```

## 7. Run the complete pipeline

```powershell
python -m trailer_director.main run
```

The pipeline performs:

1. Story understanding
2. Constraint mapping
3. Audience-specific planning
4. Trailer generation
5. Independent validation
6. Decision-log recording

Expected final result:

```text
Validation: 3/3 PASS
Output: sample_run/
```

## 8. CLI commands

```powershell
python -m trailer_director.main --help
python -m trailer_director.main version
python -m trailer_director.main run
python -m trailer_director.main validate
python -m trailer_director.main recover --change music_rights_expired --audience family
```

## 9. Inspect generated artifacts

```powershell
Get-ChildItem sample_run
```

Important outputs:

```text
story_map.json
constraint_map.json
family_trailer.json
young_adult_trailer.json
dialect_region_trailer.json
family_validation.json
young_adult_validation.json
dialect_region_validation.json
decision_log.json
```

## 10. Test suite

```powershell
pytest -q
```

The tests cover data loading, story grounding, constraints, audience planning, validation, CLI behavior, and recovery scenarios.

## 11. Change/recovery demo

```powershell
python -m trailer_director.main recover --change music_rights_expired --audience family
```

The recovery flow identifies affected decisions, replaces expired music usage, revalidates the plan, and records the event in `sample_run/decision_log.json`.

## 12. Synthetic-data disclosure

The challenge PDF supplied for this implementation did not include a real episode media package. Therefore the repository uses a clearly marked synthetic episode package designed to exercise the requested decision and verification behaviors.

The synthetic package is not presented as real production content.

## 13. Known human decisions

A production deployment would require human approval for:

- final trailer release
- contractual interpretation where evidence is ambiguous
- cultural/dialect review
- safety classification disputes
- final marketing copy
- rights/legal escalation
- release territory selection

## 14. Final demo

For an evaluator, the shortest complete demonstration is:

```powershell
$env:PYTHONPATH="src"
pytest -q
python -m trailer_director.main run
python -m trailer_director.main recover --change music_rights_expired --audience family
```
