from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

from trailer_director.agents.trailer_planner import TrailerPlannerAgent
from trailer_director.agents.validator_agent import TrailerValidatorAgent
from trailer_director.models.trailer import TrailerPlan
from trailer_director.services.data_loader import DataPackage


class RecoveryAgent:
    """Handles external changes and selectively repairs trailer decisions."""

    def __init__(self) -> None:
        self.planner = TrailerPlannerAgent()
        self.validator = TrailerValidatorAgent()

    def recover(
        self,
        package: DataPackage,
        plan: TrailerPlan,
        change_type: str,
        *,
        as_of_date: str = "2026-09-29",
    ) -> dict[str, Any]:

        change = self._normalize_change(change_type)

        if change == "music_rights_expired":
            affected_segments = self._music_segments(plan)

            recovered_plan = self._replace_expired_music(plan)

            action = "replan_music"

        elif change == "scene_05_is_spoiler":
            affected_segments = self._segments_for_scene(
                package,
                plan,
                "scene_05",
            )

            recovered_plan = self._replace_scene(
                package,
                plan,
                "scene_05",
            )

            action = "replace_affected_segments"

        elif change == "contract_restricted":
            affected_segments = self._contract_affected_segments(
                package,
                plan,
            )

            recovered_plan = self.planner.build(
                package,
                plan.audience,
            )

            action = "rebuild_affected_audience_plan"

        else:
            raise ValueError(
                f"Unsupported change type: {change_type}"
            )

        validation = self.validator.validate(
            package,
            recovered_plan,
            as_of_date=date.fromisoformat(as_of_date),
        )

        return {
            "change_type": change,
            "audience_id": plan.audience,
            "affected_scenes": affected_segments,
            "action": action,
            "recovered_plan": recovered_plan,
            "validation": validation,
            "preserved_segment_count": min(
                len(plan.segments),
                len(recovered_plan.segments),
            ),
        }

    @staticmethod
    def _normalize_change(change_type: str) -> str:
        aliases = {
            "music_expired": "music_rights_expired",
            "music_rights_expired": "music_rights_expired",
            "historical_scene_became_spoiler": "scene_05_is_spoiler",
            "scene_05_is_spoiler": "scene_05_is_spoiler",
            "contract_changed": "contract_restricted",
            "contract_restricted": "contract_restricted",
        }

        if change_type not in aliases:
            raise ValueError(
                f"Unsupported change type: {change_type}"
            )

        return aliases[change_type]

    @staticmethod
    def _music_segments(plan: TrailerPlan) -> list[str]:
        """Return source timecodes for segments containing music."""

        affected = []

        for segment in plan.segments:
            if "+" in segment.audio:
                affected.append(
                    f"{segment.source_in}-{segment.source_out}"
                )

        return affected

    @staticmethod
    def _replace_expired_music(
        plan: TrailerPlan,
    ) -> TrailerPlan:

        recovered = deepcopy(plan)

        for segment in recovered.segments:

            if "+" in segment.audio:

                dialogue, _music = segment.audio.split(
                    "+",
                    1,
                )

                segment.audio = (
                    f"{dialogue.strip()} + "
                    "licensed_library_track"
                )

                segment.reason = (
                    f"{segment.reason}; "
                    "music replaced after rights expiry"
                )

        return recovered

    @staticmethod
    def _segments_for_scene(
        package: DataPackage,
        plan: TrailerPlan,
        scene_id: str,
    ) -> list[str]:

        scene = next(
            (
                scene
                for scene in package.episode.scenes
                if scene.scene_id == scene_id
            ),
            None,
        )

        if scene is None:
            return []

        affected = []

        for segment in plan.segments:

            if (
                segment.source_in == scene.start
                and segment.source_out == scene.end
            ):
                affected.append(scene_id)

        return affected

    @staticmethod
    def _replace_scene(
        package: DataPackage,
        plan: TrailerPlan,
        scene_id: str,
    ) -> TrailerPlan:

        recovered = deepcopy(plan)

        replacement = next(
            scene
            for scene in package.episode.scenes
            if scene.scene_id == "scene_03"
        )

        target = next(
            (
                scene
                for scene in package.episode.scenes
                if scene.scene_id == scene_id
            ),
            None,
        )

        if target is None:
            return recovered

        for segment in recovered.segments:

            if (
                segment.source_in == target.start
                and segment.source_out == target.end
            ):

                segment.source_in = replacement.start
                segment.source_out = replacement.end
                segment.video = replacement.description

                segment.reason = (
                    f"{segment.reason}; "
                    f"replaced {scene_id} because it became a spoiler"
                )

        return recovered

    @staticmethod
    def _contract_affected_segments(
        package: DataPackage,
        plan: TrailerPlan,
    ) -> list[str]:

        affected = []

        for segment in plan.segments:

            if segment.audio:
                affected.append(
                    f"{segment.source_in}-{segment.source_out}"
                )

        return affected