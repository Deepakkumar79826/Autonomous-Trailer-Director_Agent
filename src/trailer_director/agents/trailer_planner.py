from trailer_director.agents.audience_promise_agent import AudiencePromiseAgent
from trailer_director.models.trailer import TrailerPlan, TrailerSegment


class TrailerPlannerAgent:
    """Selects source-grounded scenes after an audience promise is defined."""

    SCENE_SELECTIONS = {
        "family": ["scene_03", "scene_02", "scene_08"],
        "young_adult": ["scene_03", "scene_02", "scene_06", "scene_08"],
        "dialect_region": ["scene_02", "scene_03", "scene_08"],
    }

    MUSIC = {
        "family": "music_warm_01",
        "young_adult": "music_tension_01",
        "dialect_region": "music_warm_01",
    }

    def build(self, package, audience_id: str) -> TrailerPlan:
        if audience_id not in self.SCENE_SELECTIONS:
            raise ValueError(f"Unsupported audience: {audience_id}")

        audience = next(
            (a for a in package.audiences if a.audience_id == audience_id),
            None,
        )

        if audience is None:
            raise ValueError(f"Audience profile not found: {audience_id}")

        policy = package.policies[audience_id]

        promise = AudiencePromiseAgent().build(audience_id)

        scenes = {
            scene.scene_id: scene
            for scene in package.episode.scenes
        }

        subtitle_track = self._subtitle_track(
            package,
            audience_id,
        )

        segments = []

        selected_scene_ids = self.SCENE_SELECTIONS[audience_id]

        for scene_id in selected_scene_ids:
            # Source grounding: fail if planner references a nonexistent scene.
            if scene_id not in scenes:
                raise ValueError(
                    f"Selected scene does not exist in episode: {scene_id}"
                )

            scene = scenes[scene_id]

            # Audience safety / policy check.
            self._assert_allowed(scene, policy)

            subtitle = self._subtitle_for_scene(
                subtitle_track,
                scene_id,
            )

            music = self.MUSIC[audience_id]

            audio = f"Original dialogue + {music}"

            reason = self._reason(
                audience_id,
                scene_id,
            )

            evidence = [
                f"data/episode/episode.json:{scene_id}",
                f"data/audiences/audiences.json:{audience_id}",
                f"data/policies/policies.json:{audience_id}",
            ]

            if audience_id == "dialect_region":
                evidence.append(
                    "data/episode/subtitles.json:regional_hi"
                )

            order = len(segments) + 1

            if order == 1:
                transition = "fade_in"
            elif order == len(selected_scene_ids):
                transition = "fade_out"
            else:
                transition = "cut"

            segment = TrailerSegment(
                order=order,

                source_in=scene.start,
                source_out=scene.end,

                video=scene.description,

                transition=transition,

                # We only expose dialogue where the standard subtitle
                # track can ground the spoken line.
                dialogue=(
                    subtitle
                    if audience_id != "dialect_region"
                    else None
                ),

                subtitle=subtitle,

                # No unsupported creative material is invented.
                voice_over=None,
                text_card=None,

                music=music,

                # Backward-compatible field used by the existing pipeline.
                audio=audio,

                reason=reason,

                evidence=evidence,

                risk_flags=[],
            )

            segments.append(segment)

        duration = sum(
            self._seconds(
                segment.source_in,
                segment.source_out,
            )
            for segment in segments
        )

        return TrailerPlan(
            trailer_id=f"{audience_id}_trailer",

            audience=audience_id,

            creative_brief=self._creative_brief(
                audience_id
            ),

            duration_seconds=duration,

            audience_promise=promise["promise"],

            emotional_journey=promise["journey"],

            segments=segments,

            warnings=[
                "Synthetic evaluation package; final rendered media requires human editorial review.",
                "No unsupported scenes, dialogue or story facts are introduced by the planner.",
            ],

            assumptions=[
                "Supplied episode scene descriptions and subtitle tracks are authoritative for replay mode.",
                "Final promotional use remains subject to supplied contracts and human legal approval.",
                "Voice-over and text-card content are omitted unless explicitly grounded in source material.",
            ],

            human_approvals=[
                "Editorial approval of final trailer sequence.",
                "Legal/rights approval of actors, music and promotional usage.",
                "Cultural/editorial approval for dialect-region localization.",
            ],
        )

    @staticmethod
    def _creative_brief(audience_id: str) -> str:
        briefs = {
            "family": (
                "Build a warm, accessible mystery trailer that introduces "
                "the missing lantern, creates gentle curiosity and ends on "
                "a hopeful family and community beat."
            ),

            "young_adult": (
                "Build a faster mystery trailer using humour, sibling "
                "dynamics and family conflict while protecting the central twist."
            ),

            "dialect_region": (
                "Build a culturally respectful regional trailer using "
                "authentic language context, family relationships and "
                "community tradition without turning dialect identity "
                "into a stereotype."
            ),
        }

        return briefs[audience_id]

    @staticmethod
    def _assert_allowed(scene, policy):
        if scene.spoiler_level > policy.max_spoiler_level:
            raise ValueError(
                f"Scene {scene.scene_id} exceeds spoiler limit"
            )

        if scene.frightening_score > policy.max_frightening_score:
            raise ValueError(
                f"Scene {scene.scene_id} exceeds frightening-score limit"
            )

        if scene.suggestive and not policy.allow_suggestive:
            raise ValueError(
                f"Scene {scene.scene_id} contains disallowed suggestive content"
            )

    @staticmethod
    def _subtitle_track(package, audience_id):
        wanted = (
            "regional_hi"
            if audience_id == "dialect_region"
            else "standard_en"
        )

        return next(
            (
                track
                for track in package.subtitles.tracks
                if track.track_id == wanted
            ),
            None,
        )

    @staticmethod
    def _subtitle_for_scene(track, scene_id):
        if not track:
            return None

        lines = [
            line
            for line in track.lines
            if line.scene_id == scene_id
        ]

        return lines[0].text if lines else None

    @staticmethod
    def _reason(audience_id, scene_id):
        reasons = {
            "family": {
                "scene_01": (
                    "Establishes family warmth and festival context "
                    "without revealing the mystery."
                ),
                "scene_03": (
                    "Adds light humour while keeping the mystery intact."
                ),
                "scene_02": (
                    "Introduces the missing-lantern question as a "
                    "safe story hook."
                ),
                "scene_08": (
                    "Promises hopeful family and community payoff "
                    "without exposing the twist."
                ),
            },

            "young_adult": {
                "scene_03": (
                    "Uses sibling humour to establish an energetic tone."
                ),
                "scene_02": (
                    "Creates a clear mystery question."
                ),
                "scene_04": (
                    "Raises tension through a discovery without "
                    "revealing the answer."
                ),
                "scene_06": (
                    "Adds identity and family conflict while preserving "
                    "the central twist."
                ),
                "scene_08": (
                    "Provides hopeful stakes and a forward-looking payoff."
                ),
            },

            "dialect_region": {
                "scene_01": (
                    "Centers family and festival context familiar "
                    "to the regional audience."
                ),
                "scene_02": (
                    "Uses a direct, source-grounded mystery hook "
                    "suitable for regional subtitles."
                ),
                "scene_03": (
                    "Preserves natural sibling humour without turning "
                    "dialect into a joke."
                ),
                "scene_06": (
                    "Highlights family identity and conflict without "
                    "stereotyping language."
                ),
                "scene_08": (
                    "Connects the story to community and shared tradition."
                ),
            },
        }

        try:
            return reasons[audience_id][scene_id]
        except KeyError:
            return (
                "Selected because it supports the audience promise "
                "while remaining grounded in the supplied episode."
            )

    @staticmethod
    def _seconds(start, end):
        def parse(value):
            h, m, rest = value.split(":")
            s, ms = rest.split(".")

            return (
                int(h) * 3600
                + int(m) * 60
                + int(s)
                + int(ms) / 1000
            )

        return int(
            round(
                parse(end) - parse(start)
            )
        )