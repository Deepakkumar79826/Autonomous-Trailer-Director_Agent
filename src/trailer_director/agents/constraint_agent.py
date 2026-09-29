from datetime import date

from trailer_director.models.constraint_map import ConstraintMap, ConstraintRule


class ConstraintMapAgent:
    """Converts supplied policies/contracts into testable, source-linked rules."""

    def build(self, package, as_of_date: str | None = None) -> ConstraintMap:
        run_date = as_of_date or date.today().isoformat()
        rules: list[ConstraintRule] = []

        # Audience policy rules.
        for audience_id, policy in package.policies.items():
            rules.extend([
                ConstraintRule(
                    constraint_id=f"{audience_id}_spoiler_limit",
                    category="spoiler",
                    rule_type="max_spoiler_level",
                    description=f"Do not use scenes above spoiler level {policy.max_spoiler_level}.",
                    audience_id=audience_id,
                    evidence=[f"data/policies/policies.json:{audience_id}.max_spoiler_level"],
                ),
                ConstraintRule(
                    constraint_id=f"{audience_id}_frightening_limit",
                    category="safety",
                    rule_type="max_frightening_score",
                    description=f"Do not use scenes with frightening score above {policy.max_frightening_score}.",
                    audience_id=audience_id,
                    evidence=[f"data/policies/policies.json:{audience_id}.max_frightening_score"],
                ),
                ConstraintRule(
                    constraint_id=f"{audience_id}_suggestive_limit",
                    category="safety",
                    rule_type="suggestive_allowed",
                    description="Suggestive content is not permitted." if not policy.allow_suggestive else "Suggestive content is permitted.",
                    severity="error" if not policy.allow_suggestive else "info",
                    audience_id=audience_id,
                    evidence=[f"data/policies/policies.json:{audience_id}.allow_suggestive"],
                ),
                ConstraintRule(
                    constraint_id=f"{audience_id}_subtitles_required",
                    category="accessibility",
                    rule_type="accessible_subtitles_required",
                    description="Accessible subtitles are required for the trailer.",
                    severity="error" if policy.require_accessible_subtitles else "info",
                    audience_id=audience_id,
                    evidence=[f"data/policies/policies.json:{audience_id}.require_accessible_subtitles"],
                ),
            ])
            if policy.avoid_dialect_stereotype:
                rules.append(ConstraintRule(
                    constraint_id=f"{audience_id}_dialect_respect",
                    category="cultural_respect",
                    rule_type="avoid_dialect_stereotype",
                    description="Do not stereotype the dialect or use it as a comic device.",
                    audience_id=audience_id,
                    evidence=[f"data/policies/policies.json:{audience_id}.avoid_dialect_stereotype"],
                ))

        # Actor promotional rights.
        for actor in package.contracts.actors:
            severity = "error" if not actor.allowed_promotional_use else "info"
            rules.append(ConstraintRule(
                constraint_id=f"rights_{actor.actor_id}",
                category="rights",
                rule_type="actor_promotional_use",
                description=("Actor may appear in promotional material." if actor.allowed_promotional_use
                             else "Actor must not appear in promotional material."),
                severity=severity,
                actor_ids=[actor.actor_id],
                territories=actor.territories,
                evidence=[f"data/contracts/contracts.json:actors[{actor.actor_id}]"],
            ))

        # Music rights, including date-sensitive expiry.
        for music in package.contracts.music:
            expired = bool(music.expires_at and music.expires_at < run_date)
            allowed = music.allowed_promotional_use and not expired
            rules.append(ConstraintRule(
                constraint_id=f"rights_{music.asset_id}",
                category="rights",
                rule_type="music_promotional_use",
                description=("Music may be used in promotional material."
                             if allowed else
                             "Music must not be used in promotional material because promotional rights are unavailable or expired."),
                severity="error" if not allowed else "info",
                music_asset_ids=[music.asset_id],
                territories=music.territories,
                expires_at=music.expires_at,
                evidence=[f"data/contracts/contracts.json:music[{music.asset_id}]"],
            ))

        return ConstraintMap(
            episode_id=package.episode.episode_id,
            generated_for_date=run_date,
            rules=rules,
        )
