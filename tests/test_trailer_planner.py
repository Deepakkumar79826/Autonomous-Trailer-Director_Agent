from trailer_director.agents.trailer_planner import TrailerPlannerAgent
from trailer_director.services.data_loader import load_data_package


def test_three_audience_trailer_plans_are_generated():
    package = load_data_package()
    planner = TrailerPlannerAgent()

    plans = {
        audience_id: planner.build(package, audience_id)
        for audience_id in (
            "family",
            "young_adult",
            "dialect_region",
        )
    }

    assert set(plans.keys()) == {
        "family",
        "young_adult",
        "dialect_region",
    }


def test_trailer_plans_have_segments():
    package = load_data_package()
    planner = TrailerPlannerAgent()

    for audience_id in (
        "family",
        "young_adult",
        "dialect_region",
    ):
        plan = planner.build(package, audience_id)

        assert plan.audience == audience_id
        assert len(plan.segments) > 0
        assert plan.duration_seconds > 0


def test_trailer_segments_reference_real_source_timecodes():
    package = load_data_package()
    planner = TrailerPlannerAgent()

    source_scenes = {
        scene.scene_id: scene
        for scene in package.episode.scenes
    }

    for audience_id in (
        "family",
        "young_adult",
        "dialect_region",
    ):
        plan = planner.build(package, audience_id)

        for segment in plan.segments:
            matching_scene = next(
                (
                    scene
                    for scene in source_scenes.values()
                    if scene.start == segment.source_in
                    and scene.end == segment.source_out
                ),
                None,
            )

            assert matching_scene is not None


def test_main_twist_scene_is_not_selected():
    package = load_data_package()
    planner = TrailerPlannerAgent()

    for audience_id in (
        "family",
        "young_adult",
        "dialect_region",
    ):
        plan = planner.build(package, audience_id)

        selected_timecodes = {
            (segment.source_in, segment.source_out)
            for segment in plan.segments
        }

        twist_scene = next(
            scene
            for scene in package.episode.scenes
            if scene.scene_id == "scene_09"
        )

        assert (
            twist_scene.start,
            twist_scene.end,
        ) not in selected_timecodes


def test_trailers_have_audience_specific_promises():
    package = load_data_package()
    planner = TrailerPlannerAgent()

    plans = {
        audience_id: planner.build(package, audience_id)
        for audience_id in (
            "family",
            "young_adult",
            "dialect_region",
        )
    }

    promises = {
        audience_id: plan.audience_promise
        for audience_id, plan in plans.items()
    }

    assert promises["family"]
    assert promises["young_adult"]
    assert promises["dialect_region"]

    assert len(set(promises.values())) == 3