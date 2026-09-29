import json
from pathlib import Path

from trailer_director.agents.validator_agent import TrailerValidatorAgent
from trailer_director.models.trailer import TrailerPlan


def validate_trailer_file(package, trailer_path, output_path=None, as_of_date="2026-09-29"):
    plan = TrailerPlan.model_validate_json(Path(trailer_path).read_text(encoding="utf-8"))
    result = TrailerValidatorAgent().validate(package, plan, as_of_date=as_of_date)
    if output_path:
        Path(output_path).write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result
