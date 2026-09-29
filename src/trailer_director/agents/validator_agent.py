from datetime import date

from trailer_director.models.validation import ValidationIssue, ValidationResult, ValidationStatus
from trailer_director.agents.constraint_agent import ConstraintMapAgent


class TrailerValidatorAgent:
    """Independent, source-grounded validator for generated trailer plans."""

    def validate(self, package, plan, as_of_date: str | None = None, territory: str = "IN") -> ValidationResult:
        run_date = (
            as_of_date.isoformat()
            if isinstance(as_of_date, date)
            else (as_of_date or date.today().isoformat())
        )
        issues: list[ValidationIssue] = []
        checked: list[str] = []
        scenes = {scene.scene_id: scene for scene in package.episode.scenes}
        policy = package.policies.get(plan.audience)

        if policy is None:
            issues.append(ValidationIssue(
                code="AUDIENCE_POLICY_MISSING", severity="error",
                message=f"No policy exists for audience '{plan.audience}'.",
                evidence=["data/policies/policies.json"],
            ))
        else:
            checked.extend([
                f"{plan.audience}_spoiler_limit",
                f"{plan.audience}_frightening_limit",
                f"{plan.audience}_suggestive_limit",
                f"{plan.audience}_subtitles_required",
            ])
            if policy.avoid_dialect_stereotype:
                checked.append(f"{plan.audience}_dialect_respect")

        # Scene/source grounding and content policy checks.
        for segment in plan.segments:
            scene = self._find_scene_by_timecode(scenes, segment.source_in, segment.source_out)
            if scene is None:
                issues.append(ValidationIssue(
                    code="MISSING_SCENE_REFERENCE", severity="error",
                    message=f"No source scene matches timecode {segment.source_in}-{segment.source_out}.",
                    evidence=["data/episode/episode.json"],
                ))
                continue

            checked.append(f"source:{scene.scene_id}")
            if policy:
                if scene.spoiler_level > policy.max_spoiler_level:
                    issues.append(ValidationIssue(
                        code="SPOILER_LIMIT_EXCEEDED", severity="error",
                        message=f"{scene.scene_id} has spoiler level {scene.spoiler_level}; limit is {policy.max_spoiler_level}.",
                        evidence=[f"data/episode/episode.json:{scene.scene_id}", f"data/policies/policies.json:{plan.audience}.max_spoiler_level"],
                    ))
                if scene.frightening_score > policy.max_frightening_score:
                    issues.append(ValidationIssue(
                        code="FRIGHTENING_LIMIT_EXCEEDED", severity="error",
                        message=f"{scene.scene_id} has frightening score {scene.frightening_score}; limit is {policy.max_frightening_score}.",
                        evidence=[f"data/episode/episode.json:{scene.scene_id}", f"data/policies/policies.json:{plan.audience}.max_frightening_score"],
                    ))
                if scene.suggestive and not policy.allow_suggestive:
                    issues.append(ValidationIssue(
                        code="SUGGESTIVE_CONTENT_BLOCKED", severity="error",
                        message=f"{scene.scene_id} contains suggestive content not allowed for {plan.audience}.",
                        evidence=[f"data/episode/episode.json:{scene.scene_id}", f"data/policies/policies.json:{plan.audience}.allow_suggestive"],
                    ))

            if policy and policy.require_accessible_subtitles and not segment.subtitle:
                issues.append(ValidationIssue(
                    code="ACCESSIBLE_SUBTITLE_MISSING", severity="error",
                    message=f"{scene.scene_id} has no subtitle text in the trailer segment.",
                    evidence=[f"data/episode/subtitles.json:{plan.audience}"],
                ))

            if plan.audience == "dialect_region" and segment.audio and "Original dialogue" not in segment.audio:
                issues.append(ValidationIssue(
                    code="DIALECT_SOURCE_AUDIO_UNGROUNDED", severity="error",
                    message=f"{scene.scene_id} uses audio not explicitly grounded in original dialogue.",
                    evidence=[f"data/episode/episode.json:{scene.scene_id}"],
                ))

        # Rights checks are deliberately independent from the planner.
        for segment in plan.segments:
            for actor_id, actor in self._actors_in_segment(package, segment).items():
                checked.append(f"rights_{actor_id}")
                if not actor.allowed_promotional_use or territory not in actor.territories:
                    issues.append(ValidationIssue(
                        code="ACTOR_PROMOTIONAL_RIGHTS_BLOCKED", severity="error",
                        message=f"Actor {actor_id} is not cleared for promotional use in {territory}.",
                        evidence=[f"data/contracts/contracts.json:actors[{actor_id}]"],
                    ))

            for music in self._music_assets(segment.audio):
                contract = next((m for m in package.contracts.music if m.asset_id == music), None)
                checked.append(f"rights_{music}")
                if contract is None:
                    issues.append(ValidationIssue(
                        code="MUSIC_CONTRACT_MISSING", severity="error",
                        message=f"No contract found for music asset {music}.",
                        evidence=["data/contracts/contracts.json"],
                    ))
                elif (not contract.allowed_promotional_use or territory not in contract.territories
                      or (contract.expires_at and contract.expires_at < run_date)):
                    issues.append(ValidationIssue(
                        code="MUSIC_PROMOTIONAL_RIGHTS_BLOCKED", severity="error",
                        message=f"Music {music} is unavailable for promotional use in {territory} on {run_date}.",
                        evidence=[f"data/contracts/contracts.json:music[{music}]"],
                    ))

        # Independent central-twist protection: levels 3 are never trailer-safe.
        for segment in plan.segments:
            scene = self._find_scene_by_timecode(scenes, segment.source_in, segment.source_out)
            if scene and scene.spoiler_level >= 3:
                issues.append(ValidationIssue(
                    code="CENTRAL_SPOILER_BLOCKED", severity="error",
                    message=f"{scene.scene_id} is protected at spoiler level {scene.spoiler_level}.",
                    evidence=[f"data/episode/episode.json:{scene.scene_id}"],
                ))

        status = ValidationStatus.REJECT if any(i.severity == "error" for i in issues) else ValidationStatus.PASS
        return ValidationResult(status=status, issues=issues, checked_rules=sorted(set(checked)))

    @staticmethod
    def _find_scene_by_timecode(scenes, start, end):
        return next((s for s in scenes.values() if s.start == start and s.end == end), None)

    @staticmethod
    def _actors_in_segment(package, segment):
        scene = next((s for s in package.episode.scenes if s.start == segment.source_in and s.end == segment.source_out), None)
        if not scene:
            return {}
        mapping = {"Asha": "actor_asha", "Ravi": "actor_ravi", "Meera": "actor_meera"}
        actor_ids = {mapping[name] for name in scene.characters if name in mapping}
        return {a.actor_id: a for a in package.contracts.actors if a.actor_id in actor_ids}

    @staticmethod
    def _music_assets(audio: str):
        assets = []
        for token in audio.replace(",", " ").split():
            if token.startswith("music_"):
                assets.append(token)
        return assets
