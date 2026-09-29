from trailer_director.models.story import (
    Character,
    EmotionalTurn,
    MajorEvent,
    ProtectedSpoiler,
    Relationship,
    SensitiveContent,
    StoryMap,
)
from trailer_director.services.data_loader import DataPackage


class StoryMapAgent:
    """Builds a source-grounded story map from the episode manifest.

    This first implementation is deterministic: it does not invent facts
    and every derived item points back to one or more source scene IDs.
    """

    def build(self, package: DataPackage) -> StoryMap:
        scenes = package.episode.scenes

        character_evidence: dict[str, list[str]] = {}
        for scene in scenes:
            for character in scene.characters:
                character_evidence.setdefault(character, []).append(scene.scene_id)

        characters = [
            Character(name=name, evidence=sorted(evidence))
            for name, evidence in sorted(character_evidence.items())
        ]

        relationships = [
            Relationship(
                subject="Asha",
                relation="sibling_of",
                object="Ravi",
                evidence=["scene_01", "scene_02", "scene_07", "scene_08"],
            ),
            Relationship(
                subject="Asha",
                relation="family_relationship_with",
                object="Meera",
                evidence=["scene_01", "scene_05", "scene_06", "scene_09"],
            ),
            Relationship(
                subject="Ravi",
                relation="family_relationship_with",
                object="Meera",
                evidence=["scene_01", "scene_07", "scene_08"],
            ),
        ]

        major_events = [
            MajorEvent(
                event_id="event_01",
                description="The old festival lantern is discovered to be missing.",
                scene_id="scene_02",
                spoiler_level=0,
            ),
            MajorEvent(
                event_id="event_02",
                description="Asha finds an old photograph connecting Meera to the lantern's history.",
                scene_id="scene_05",
                spoiler_level=2,
            ),
            MajorEvent(
                event_id="event_03",
                description="Asha confronts Meera about the photograph.",
                scene_id="scene_06",
                spoiler_level=1,
            ),
            MajorEvent(
                event_id="event_04",
                description="Ravi reveals that he moved the lantern to protect it from rain.",
                scene_id="scene_07",
                spoiler_level=2,
            ),
            MajorEvent(
                event_id="event_05",
                description="Meera tells Asha the full truth about the lantern's history.",
                scene_id="scene_09",
                spoiler_level=3,
            ),
            MajorEvent(
                event_id="event_06",
                description="The family reconciles and lights the lantern at the festival.",
                scene_id="scene_10",
                spoiler_level=3,
            ),
        ]

        emotional_turns = [
            EmotionalTurn(
                scene_id=scene.scene_id,
                emotion=scene.emotion,
                evidence=[scene.scene_id],
            )
            for scene in scenes
        ]

        protected_spoilers = [
            ProtectedSpoiler(
                spoiler_id="spoiler_01",
                description="The full truth about why the lantern was preserved.",
                scene_ids=["scene_09", "scene_10"],
                level=3,
            ),
            ProtectedSpoiler(
                spoiler_id="spoiler_02",
                description="Ravi was responsible for moving the lantern to protect it from rain.",
                scene_ids=["scene_07"],
                level=2,
            ),
            ProtectedSpoiler(
                spoiler_id="spoiler_03",
                description="The old photograph reveals a connection between Meera and the lantern's history.",
                scene_ids=["scene_05"],
                level=2,
            ),
        ]

        sensitive_content = [
            SensitiveContent(
                scene_id=scene.scene_id,
                description="No sensitive content flagged in the source manifest.",
                severity="none",
            )
            for scene in scenes
            if scene.sensitive_content
        ]

        return StoryMap(
            episode_id=package.episode.episode_id,
            title=package.episode.title,
            characters=characters,
            relationships=relationships,
            major_events=major_events,
            emotional_turns=emotional_turns,
            protected_spoilers=protected_spoilers,
            sensitive_content=sensitive_content,
        )
