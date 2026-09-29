from trailer_director.services.story_map_service import build_and_save_story_map


def main():
    story_map = build_and_save_story_map()

    print("Building source-grounded story map...")
    print(f"✓ Episode: {story_map.title}")
    print(f"✓ Characters: {len(story_map.characters)}")
    print(f"✓ Relationships: {len(story_map.relationships)}")
    print(f"✓ Major events: {len(story_map.major_events)}")
    print(f"✓ Emotional turns: {len(story_map.emotional_turns)}")
    print(f"✓ Protected spoilers: {len(story_map.protected_spoilers)}")
    print(f"✓ Sensitive-content flags: {len(story_map.sensitive_content)}")
    print("✓ Saved: sample_run/story_map.json")


if __name__ == "__main__":
    main()
