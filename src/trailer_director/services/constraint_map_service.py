import json
from pathlib import Path

from trailer_director.agents.constraint_agent import ConstraintMapAgent
from trailer_director.services.data_loader import load_data_package


def build_and_save_constraint_map(
    data_dir: str | Path = "data",
    output_path: str | Path = "sample_run/constraint_map.json",
    as_of_date: str | None = None,
):
    package = load_data_package(data_dir)
    constraint_map = ConstraintMapAgent().build(package, as_of_date=as_of_date)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(constraint_map.model_dump(), indent=2),
        encoding="utf-8",
    )
    return constraint_map
