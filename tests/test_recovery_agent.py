from trailer_director.agents.recovery_agent import RecoveryAgent
from trailer_director.agents.trailer_planner import TrailerPlannerAgent
from trailer_director.services.change_log_service import ChangeLogService
from trailer_director.services.data_loader import load_data_package


TODAY = "2026-09-29"


def test_music_rights_change_replaces_music_and_revalidates():
    package = load_data_package()

    original = TrailerPlannerAgent().build(
        package,
        "family",
    )

    result = RecoveryAgent().recover(
        package,
        original,
        "music_rights_expired",
        as_of_date=TODAY,
    )

    assert result["action"] == "replan_music"

    assert result["validation"].status.value == "PASS"

    for segment in result["recovered_plan"].segments:
        assert "licensed_library_track" in segment.audio


def test_change_log_is_append_only(tmp_path):
    path = tmp_path / "decision_log.json"

    service = ChangeLogService(path)

    service.append({
        "event": "initial_plan",
        "audience_id": "family",
    })

    service.append({
        "event": "music_rights_expired",
        "audience_id": "family",
    })

    entries = service.read()

    assert len(entries) == 2

    assert entries[0]["event"] == "initial_plan"

    assert entries[1]["event"] == "music_rights_expired"


def test_spoiler_change_replaces_only_affected_scene():
    package = load_data_package()

    planner = TrailerPlannerAgent()

    original = planner.build(
        package,
        "young_adult",
    )

    # Use a copy of the plan and replace the first
    # segment's timecode with scene_05's source timecode.
    from copy import deepcopy

    modified = deepcopy(original)

    scene_05 = next(
        scene
        for scene in package.episode.scenes
        if scene.scene_id == "scene_05"
    )

    modified.segments[0].source_in = scene_05.start
    modified.segments[0].source_out = scene_05.end

    result = RecoveryAgent().recover(
        package,
        modified,
        "scene_05_is_spoiler",
        as_of_date=TODAY,
    )

    assert result["action"] == "replace_affected_segments"

    assert result["validation"].status.value == "PASS"

    scene_03 = next(
        scene
        for scene in package.episode.scenes
        if scene.scene_id == "scene_03"
    )

    first_segment = result["recovered_plan"].segments[0]

    assert first_segment.source_in == scene_03.start
    assert first_segment.source_out == scene_03.end