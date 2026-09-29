from trailer_director.agents.constraint_agent import ConstraintMapAgent
from trailer_director.services.data_loader import load_data_package


def test_constraint_map_contains_audience_rules():
    package = load_data_package()
    result = ConstraintMapAgent().build(package, as_of_date="2026-09-29")

    ids = {rule.constraint_id for rule in result.rules}

    assert "family_spoiler_limit" in ids
    assert "young_adult_frightening_limit" in ids
    assert "dialect_region_dialect_respect" in ids


def test_expired_music_is_blocked():
    package = load_data_package()
    result = ConstraintMapAgent().build(package, as_of_date="2026-09-29")

    rule = next(
        rule for rule in result.rules
        if rule.constraint_id == "rights_music_expired_demo"
    )

    assert rule.severity == "error"
    assert rule.rule_type == "music_promotional_use"
    assert "must not be used" in rule.description
    assert rule.expires_at == "2026-09-01"