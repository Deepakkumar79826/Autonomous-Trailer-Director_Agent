from trailer_director.agents.recovery_agent import RecoveryAgent
from trailer_director.services.data_loader import load_data_package
from trailer_director.services.change_log_service import ChangeLogService
from trailer_director.agents.trailer_planner import TrailerPlannerAgent


def main() -> None:
    package = load_data_package()
    planner = TrailerPlannerAgent()
    original = planner.build(package, "family")

    recovery = RecoveryAgent()
    result = recovery.recover(
        package,
        original,
        "music_rights_expired",
    )

    log = ChangeLogService()
    log.append({
        "event": result["change_type"],
        "audience_id": result["audience_id"],
        "affected_scenes": result["affected_scenes"],
        "action": result["action"],
        "validation_status": result["validation"].status.value,
    })

    print("Simulating change event...")
    print(f"✓ Event: {result['change_type']}")
    print(f"✓ Affected scenes: {result['affected_scenes']}")
    print(f"✓ Recovery action: {result['action']}")
    print(f"✓ Validation: {result['validation'].status.value}")
    print("✓ Decision log: sample_run/decision_log.json")


if __name__ == "__main__":
    main()
