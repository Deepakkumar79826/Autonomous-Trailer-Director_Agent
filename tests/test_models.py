from trailer_director.services.data_loader import load_data_package
from trailer_director.models.trailer import (
    TrailerCostEstimate,
    TrailerPlan,
    TrailerSegment,
    TrailerValidationSummary,
)


def test_data_package_loads():
    package = load_data_package()

    assert package.episode.episode_id == "EP001"
    assert len(package.episode.scenes) == 10
    assert len(package.subtitles.tracks) == 2
    assert len(package.audiences) == 3
    assert len(package.policies) == 3
    assert len(package.contracts.music) == 3


def test_scene_spoiler_levels_are_valid():
    package = load_data_package()

    for scene in package.episode.scenes:
        assert 0 <= scene.spoiler_level <= 3
        assert 0 <= scene.frightening_score <= 1


def test_submission_grade_trailer_schema():
    segment = TrailerSegment(
        order=1,
        source_in="00:01:08.000",
        source_out="00:02:14.000",
        video="Asha notices that the lantern is missing.",
        transition="fade_in",
        dialogue="Where did the old lantern go?",
        subtitle="Where did the old lantern go?",
        voice_over=None,
        text_card=None,
        music="music_warm_01",
        audio="Original dialogue + music_warm_01",
        reason="Creates the central mystery hook.",
        evidence=["data/episode/episode.json:scene_02"],
        risk_flags=[],
    )

    validation = TrailerValidationSummary()

    cost = TrailerCostEstimate(
        estimated_processing_cost=0.46,
        budget_limit=2.0,
        budget_remaining=1.54,
        within_budget=True,
        lower_cost_fallback="Replay cached analysis.",
    )

    plan = TrailerPlan(
        trailer_id="family_trailer",
        audience="family",
        creative_brief="Warm family mystery.",
        duration_seconds=210,
        audience_promise="Warmth and curiosity.",
        emotional_journey=["warmth", "curiosity", "hope"],
        segments=[segment],
        validation=validation,
        warnings=[],
        assumptions=[],
        human_approvals=["Editorial approval"],
        cost=cost,
    )

    assert plan.segments[0].order == 1
    assert plan.segments[0].voice_over is None
    assert plan.segments[0].text_card is None
    assert plan.validation.status == "PASS"
    assert plan.cost.estimated_processing_cost == 0.46
    assert plan.cost.within_budget is True