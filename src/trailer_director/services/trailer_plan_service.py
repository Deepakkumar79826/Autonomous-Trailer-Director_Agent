import json
from pathlib import Path

from trailer_director.agents.trailer_planner import TrailerPlannerAgent
from trailer_director.models.trailer import TrailerCostEstimate


AUDIENCES = (
    "family",
    "young_adult",
    "dialect_region",
)


def calculate_trailer_cost(package, include_repair: bool = False):
    costs = package.cost.estimated_costs

    total = (
        costs["story_analysis_call"]
        + costs["audience_planning_call"]
        + costs["validation_call"]
    )

    if include_repair:
        total += costs["repair_call"]

    budget = package.cost.budget_limit

    return {
        "currency": package.cost.currency,
        "estimated_processing_cost": round(total, 2),
        "budget_limit": budget,
        "budget_remaining": round(max(0, budget - total), 2),
        "within_budget": total <= budget,
        "lower_cost_fallback": (
            "Use replay-mode deterministic planning and cache the story "
            "analysis; skip repair calls unless validation fails."
        ),
    }


def build_and_save_trailers(package, output_dir="sample_run"):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    planner = TrailerPlannerAgent()
    plans = {}

    cost = calculate_trailer_cost(package)

    for audience_id in (
        "family",
        "young_adult",
        "dialect_region",
    ):
        plan = planner.build(package, audience_id)

        plan.cost = TrailerCostEstimate(
            currency=cost["currency"],
            estimated_processing_cost=cost["estimated_processing_cost"],
            budget_limit=cost["budget_limit"],
            budget_remaining=cost["budget_remaining"],
            within_budget=cost["within_budget"],
            lower_cost_fallback=cost["lower_cost_fallback"],
        )

        path = output / f"{audience_id}_trailer.json"

        path.write_text(
            plan.model_dump_json(indent=2),
            encoding="utf-8",
        )

        plans[audience_id] = path

    return plans