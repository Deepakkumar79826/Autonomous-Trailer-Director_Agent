from copy import deepcopy

from trailer_director.agents.validator_agent import TrailerValidatorAgent
from trailer_director.services.data_loader import load_data_package
from trailer_director.agents.trailer_planner import TrailerPlannerAgent


TODAY = "2026-09-29"


def family_plan(package):
    return TrailerPlannerAgent().build(package, "family")


def test_valid_generated_trailer_passes():
    package = load_data_package()
    result = TrailerValidatorAgent().validate(package, family_plan(package), as_of_date=TODAY)
    assert result.status.value == "PASS"
    assert result.issues == []


def test_missing_scene_reference_is_rejected():
    package = load_data_package()
    plan = family_plan(package)
    plan.segments[0].source_in = "99:99:99.000"
    result = TrailerValidatorAgent().validate(package, plan, as_of_date=TODAY)
    assert any(i.code == "MISSING_SCENE_REFERENCE" for i in result.issues)
    assert result.status.value == "REJECT"


def test_spoiler_scene_is_rejected():
    package = load_data_package()
    plan = family_plan(package)
    scene = next(s for s in package.episode.scenes if s.scene_id == "scene_09")
    plan.segments[0].source_in = scene.start
    plan.segments[0].source_out = scene.end
    plan.segments[0].subtitle = "A truth is finally revealed."
    result = TrailerValidatorAgent().validate(package, plan, as_of_date=TODAY)
    codes = {i.code for i in result.issues}
    assert "SPOILER_LIMIT_EXCEEDED" in codes
    assert "CENTRAL_SPOILER_BLOCKED" in codes


def test_changed_contract_is_rechecked():
    package = load_data_package()
    package.contracts.actors[0].allowed_promotional_use = False
    plan = family_plan(package)
    result = TrailerValidatorAgent().validate(package, plan, as_of_date=TODAY)
    assert any(i.code == "ACTOR_PROMOTIONAL_RIGHTS_BLOCKED" for i in result.issues)


def test_expired_music_is_rejected_even_if_planner_selected_it():
    package = load_data_package()
    plan = family_plan(package)
    plan.segments[0].audio = "Original dialogue + music_expired_demo"
    result = TrailerValidatorAgent().validate(package, plan, as_of_date=TODAY)
    assert any(i.code == "MUSIC_PROMOTIONAL_RIGHTS_BLOCKED" for i in result.issues)
