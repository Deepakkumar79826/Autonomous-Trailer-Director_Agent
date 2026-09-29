class AudiencePromiseAgent:
    """Defines the audience promise before selecting source scenes."""

    PROMISES = {
        "family": {
            "promise": "A warm family mystery about trust, community and lighting the lantern together.",
            "journey": ["warmth", "curiosity", "gentle tension", "hope"],
        },
        "young_adult": {
            "promise": "A fast-moving mystery driven by sibling humour, identity and family conflict.",
            "journey": ["humour", "mystery", "tension", "conflict", "hope"],
        },
        "dialect_region": {
            "promise": "A familiar regional story grounded in authentic language, family bonds and community tradition.",
            "journey": ["familiarity", "curiosity", "identity", "community", "hope"],
        },
    }

    def build(self, audience_id: str) -> dict:
        if audience_id not in self.PROMISES:
            raise ValueError(f"Unsupported audience: {audience_id}")
        return self.PROMISES[audience_id].copy()
