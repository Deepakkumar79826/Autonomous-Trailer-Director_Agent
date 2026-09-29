from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from trailer_director.agents.recovery_agent import RecoveryAgent
from trailer_director.agents.trailer_planner import TrailerPlannerAgent
from trailer_director.agents.validator_agent import TrailerValidatorAgent
from trailer_director.models.trailer import (
    TrailerCostEstimate,
    TrailerValidationSummary,
)
from trailer_director.services.change_log_service import ChangeLogService
from trailer_director.services.constraint_map_service import (
    build_and_save_constraint_map,
)
from trailer_director.services.data_loader import load_data_package
from trailer_director.services.story_map_service import (
    build_and_save_story_map,
)
from trailer_director.services.trailer_plan_service import (
    build_and_save_trailers,
    calculate_trailer_cost,
)


app = typer.Typer(
    help="Autonomous Trailer Director CLI",
    no_args_is_help=True,
)

console = Console()

VERSION = "0.9.0"


@app.command()
def version() -> None:
    """Show CLI version."""
    console.print(
        f"Autonomous Trailer Director v{VERSION}"
    )


@app.command()
def run() -> None:
    """Run the complete trailer-director pipeline."""

    console.print(
        Panel.fit(
            "[bold]AUTONOMOUS TRAILER DIRECTOR[/bold]\n"
            "End-to-end source-grounded trailer planning",
        )
    )

    # =========================================================
    # STEP 1: Load episode package
    # =========================================================
    console.print(
        "[1/6] Loading episode package..."
    )

    package = load_data_package()

    console.print(
        f"✓ Episode: {package.episode.title} "
        f"({package.episode.episode_id})"
    )

    # =========================================================
    # STEP 2: Build story map
    # =========================================================
    console.print(
        "[2/6] Building story map..."
    )

    story_path = build_and_save_story_map()

    console.print(
        f"✓ Story map: {story_path}"
    )

    # =========================================================
    # STEP 3: Build constraint map
    # =========================================================
    console.print(
        "[3/6] Building constraint map..."
    )

    constraint_path = build_and_save_constraint_map()

    console.print(
        f"✓ Constraint map: {constraint_path}"
    )

    # =========================================================
    # STEP 4: Build audience-specific trailers
    # =========================================================
    console.print(
        "[4/6] Building audience-specific trailers..."
    )

    trailer_paths = build_and_save_trailers(
        package
    )

    for audience_id, path in trailer_paths.items():
        console.print(
            f"✓ {audience_id}: {path}"
        )

    # =========================================================
    # STEP 5: Independently validate trailers
    # =========================================================
    console.print(
        "[5/6] Independently validating trailers..."
    )

    validator = TrailerValidatorAgent()
    planner = TrailerPlannerAgent()

    validation_dir = Path("sample_run")
    validation_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_results = {}

    # ---------------------------------------------------------
    # Calculate deterministic processing cost ONCE
    # ---------------------------------------------------------
    cost_data = calculate_trailer_cost(
        package,
        include_repair=False,
    )

    for audience_id in (
        "family",
        "young_adult",
        "dialect_region",
    ):
        # Build fresh plan for independent validation.
        plan = planner.build(
            package,
            audience_id,
        )

        # -----------------------------------------------------
        # Independent validation
        # -----------------------------------------------------
        result = validator.validate(
            package,
            plan,
            as_of_date="2026-09-29",
        )

        validation_results[audience_id] = result

        # -----------------------------------------------------
        # Attach processing cost
        # -----------------------------------------------------
        plan.cost = TrailerCostEstimate(
            currency=cost_data["currency"],
            estimated_processing_cost=cost_data[
                "estimated_processing_cost"
            ],
            budget_limit=cost_data[
                "budget_limit"
            ],
            budget_remaining=cost_data[
                "budget_remaining"
            ],
            within_budget=cost_data[
                "within_budget"
            ],
            lower_cost_fallback=cost_data[
                "lower_cost_fallback"
            ],
        )

        # -----------------------------------------------------
        # Build submission-facing validation summary
        # -----------------------------------------------------
        overall_status = result.status.value

        if overall_status == "PASS":
            summary = TrailerValidationSummary(
                status="PASS",
                spoiler="PASS",
                rights="PASS",
                policy="PASS",
                bias="PASS",
                factual_consistency="PASS",
                accessibility="PASS",
                source_accuracy="PASS",
            )
        else:
            summary = TrailerValidationSummary(
                status="FAIL",
                spoiler="REVIEW",
                rights="REVIEW",
                policy="REVIEW",
                bias="REVIEW",
                factual_consistency="REVIEW",
                accessibility="REVIEW",
                source_accuracy="REVIEW",
            )

        plan.validation = summary

        # -----------------------------------------------------
        # Save final submission-ready trailer
        # -----------------------------------------------------
        trailer_path = trailer_paths[
            audience_id
        ]

        trailer_path.write_text(
            plan.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        # -----------------------------------------------------
        # Save detailed validator report separately
        # -----------------------------------------------------
        report_path = (
            validation_dir
            / f"{audience_id}_validation.json"
        )

        report_path.write_text(
            result.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        console.print(
            f"✓ {audience_id}: "
            f"{result.status.value} "
            f"({len(result.issues)} issues)"
        )

    # =========================================================
    # STEP 6: Write decision log
    # =========================================================
    console.print(
        "[6/6] Writing decision log..."
    )

    log = ChangeLogService()

    log.append(
        {
            "event": "pipeline_run",
            "episode_id": (
                package.episode.episode_id
            ),
            "validation": {
                audience: result.status.value
                for audience, result
                in validation_results.items()
            },
            "estimated_processing_cost": (
                cost_data[
                    "estimated_processing_cost"
                ]
            ),
            "budget_limit": (
                cost_data[
                    "budget_limit"
                ]
            ),
            "within_budget": (
                cost_data[
                    "within_budget"
                ]
            ),
        }
    )

    console.print(
        "✓ Decision log: "
        "sample_run/decision_log.json"
    )

    # =========================================================
    # Final pipeline summary
    # =========================================================
    passed = sum(
        result.status.value == "PASS"
        for result in validation_results.values()
    )

    console.print(
        Panel.fit(
            f"[bold]Pipeline complete[/bold]\n"
            f"Validation: {passed}/3 PASS\n"
            f"Estimated cost: "
            f"${cost_data['estimated_processing_cost']:.2f}\n"
            f"Budget: "
            f"${cost_data['budget_limit']:.2f}\n"
            f"Output: sample_run/",
        )
    )


@app.command()
def validate() -> None:
    """Validate all three generated audience trailer plans."""

    package = load_data_package()

    planner = TrailerPlannerAgent()
    validator = TrailerValidatorAgent()

    console.print(
        "Validating generated trailer plans..."
    )

    all_passed = True

    for audience_id in (
        "family",
        "young_adult",
        "dialect_region",
    ):
        plan = planner.build(
            package,
            audience_id,
        )

        result = validator.validate(
            package,
            plan,
            as_of_date="2026-09-29",
        )

        console.print(
            f"✓ {audience_id}: "
            f"{result.status.value} "
            f"({len(result.issues)} issues)"
        )

        if result.status.value != "PASS":
            all_passed = False

    if not all_passed:
        raise typer.Exit(code=1)

    console.print(
        "✓ All audience trailer validations passed."
    )


@app.command()
def recover(
    change: str = typer.Option(
        "music_rights_expired",
        "--change",
        "-c",
        help="Change event to replay.",
    ),
    audience: str = typer.Option(
        "family",
        "--audience",
        "-a",
        help="Audience whose plan is affected.",
    ),
) -> None:
    """Replay a change event and selectively recover the affected plan."""

    package = load_data_package()

    plan = TrailerPlannerAgent().build(
        package,
        audience,
    )

    result = RecoveryAgent().recover(
        package,
        plan,
        change,
        as_of_date="2026-09-29",
    )

    log = ChangeLogService()

    log.append(
        {
            "event": result[
                "change_type"
            ],
            "audience_id": result[
                "audience_id"
            ],
            "affected_scenes": result[
                "affected_scenes"
            ],
            "action": result[
                "action"
            ],
            "validation_status": result[
                "validation"
            ].status.value,
        }
    )

    console.print(
        f"Event: "
        f"{result['change_type']}"
    )

    console.print(
        f"Affected: "
        f"{result['affected_scenes']}"
    )

    console.print(
        f"Recovery: "
        f"{result['action']}"
    )

    console.print(
        f"Validation: "
        f"{result['validation'].status.value}"
    )

    console.print(
        "✓ Decision log updated"
    )


if __name__ == "__main__":
    app()