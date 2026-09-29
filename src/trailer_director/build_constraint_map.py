from trailer_director.services.constraint_map_service import build_and_save_constraint_map


if __name__ == "__main__":
    print("Building constraint map...")
    result = build_and_save_constraint_map(as_of_date="2026-09-29")

    categories = sorted({rule.category for rule in result.rules})
    errors = sum(rule.severity == "error" for rule in result.rules)

    print(f"✓ Episode: {result.episode_id}")
    print(f"✓ Rules: {len(result.rules)}")
    print(f"✓ Categories: {', '.join(categories)}")
    print(f"✓ Blocking/error rules: {errors}")
    print("✓ Music expiry evaluated for 2026-09-29")
    print("✓ Saved: sample_run/constraint_map.json")
