from pathlib import Path

from trailer_director.services.data_loader import load_data_package
from trailer_director.services.validation_service import validate_trailer_file


def main():
    package = load_data_package()
    output = Path("sample_run")
    output.mkdir(parents=True, exist_ok=True)
    print("Validating audience-specific trailer plans...")
    statuses = []
    for audience in ("family", "young_adult", "dialect_region"):
        result = validate_trailer_file(
            package,
            output / f"{audience}_trailer.json",
            output / f"{audience}_validation.json",
            as_of_date="2026-09-29",
        )
        statuses.append(result.status.value)
        print(f"✓ {audience}: {result.status.value} ({len(result.issues)} issues)")
    print("✓ Validation reports saved")
    print(f"✓ Overall: {'REJECT' if 'REJECT' in statuses else 'PASS'}")


if __name__ == "__main__":
    main()
