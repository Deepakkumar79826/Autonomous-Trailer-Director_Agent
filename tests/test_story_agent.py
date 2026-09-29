from trailer_director.agents.story_agent import StoryMapAgent
from trailer_director.services.data_loader import load_data_package


def test_story_map_is_grounded_in_episode():
    package = load_data_package()

    story_map = StoryMapAgent().build(package)

    assert story_map.episode_id == "EP001"
    assert story_map.title == "The Last Lantern"

    # Every major event must reference a real scene.
    scene_ids = {scene.scene_id for scene in package.episode.scenes}

    for event in story_map.major_events:
        assert event.scene_id in scene_ids


def test_story_map_protects_the_main_twist():
    package = load_data_package()

    story_map = StoryMapAgent().build(package)

    spoiler_ids = {
        spoiler.spoiler_id
        for spoiler in story_map.protected_spoilers
    }

    assert "spoiler_01" in spoiler_ids

    main_twist = next(
        spoiler
        for spoiler in story_map.protected_spoilers
        if spoiler.spoiler_id == "spoiler_01"
    )

    assert "scene_09" in main_twist.scene_ids
    assert main_twist.level == 3