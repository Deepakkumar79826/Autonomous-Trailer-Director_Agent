import json
from pathlib import Path

from trailer_director.agents.story_agent import StoryMapAgent
from trailer_director.services.data_loader import load_data_package


def build_and_save_story_map(
    data_dir: str | Path = "data",
    output_path: str | Path = "sample_run/story_map.json",
):
    package = load_data_package(data_dir)
    story_map = StoryMapAgent().build(package)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(story_map.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return story_map
