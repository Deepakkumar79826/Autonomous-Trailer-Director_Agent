import json
from pathlib import Path

from trailer_director.models.audience import AudienceProfile
from trailer_director.models.constraints import (
    AudiencePolicy,
    ContractPackage,
    CostConfig,
    HistoricalPerformance,
)
from trailer_director.models.episode import Episode, SubtitlePackage


class DataPackage:
    def __init__(
        self,
        episode: Episode,
        subtitles: SubtitlePackage,
        policies: dict[str, AudiencePolicy],
        contracts: ContractPackage,
        audiences: list[AudienceProfile],
        performance: HistoricalPerformance,
        cost: CostConfig,
    ):
        self.episode = episode
        self.subtitles = subtitles
        self.policies = policies
        self.contracts = contracts
        self.audiences = audiences
        self.performance = performance
        self.cost = cost


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_data_package(data_dir: str | Path = "data") -> DataPackage:
    root = Path(data_dir)

    episode = Episode.model_validate(
        _read_json(root / "episode" / "episode.json")
    )

    subtitles = SubtitlePackage.model_validate(
        _read_json(root / "episode" / "subtitles.json")
    )

    raw_policies = _read_json(root / "policies" / "policies.json")
    policies = {
        audience_id: AudiencePolicy.model_validate(policy)
        for audience_id, policy in raw_policies.items()
    }

    contracts = ContractPackage.model_validate(
        _read_json(root / "contracts" / "contracts.json")
    )

    audiences = [
        AudienceProfile.model_validate(item)
        for item in _read_json(root / "audiences" / "audiences.json")
    ]

    performance = HistoricalPerformance.model_validate(
        _read_json(root / "performance" / "historical_performance.json")
    )

    cost = CostConfig.model_validate(
        _read_json(root / "cost" / "cost_sheet.json")
    )

    return DataPackage(
        episode=episode,
        subtitles=subtitles,
        policies=policies,
        contracts=contracts,
        audiences=audiences,
        performance=performance,
        cost=cost,
    )
