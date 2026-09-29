from trailer_director.services.data_loader import load_data_package
from trailer_director.services.trailer_plan_service import build_and_save_trailers


def main():
    print("Building audience-specific trailer plans...")
    package = load_data_package()
    paths = build_and_save_trailers(package)
    for audience_id, path in paths.items():
        print(f"✓ {audience_id}: {path}")
    print("✓ Three trailer plans generated")


if __name__ == "__main__":
    main()
