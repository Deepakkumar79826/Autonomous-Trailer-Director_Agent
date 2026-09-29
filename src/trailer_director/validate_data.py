from trailer_director.services.data_loader import load_data_package


def main():
    package = load_data_package()

    print("Loading episode package...")
    print(f"✓ Episode: {package.episode.title}")
    print(f"✓ Scenes: {len(package.episode.scenes)}")
    print(f"✓ Subtitle tracks: {len(package.subtitles.tracks)}")
    print(f"✓ Audience profiles: {len(package.audiences)}")
    print(f"✓ Policies: {len(package.policies)}")
    print("✓ Contracts loaded")
    print("✓ Historical performance loaded")
    print("✓ Cost configuration loaded")
    print("\nDATA PACKAGE VALID")


if __name__ == "__main__":
    main()
