import yaml
from pathlib import Path
from .models import ReleaseInfo, TeamInfo
from typing import List, Dict


class Config:
    def __init__(self, config_path="config/regression_config.yaml"):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self):
        project_root = Path(__file__).parent.parent.parent.parent
        absolute_config_path = project_root / self.config_path
        with open(absolute_config_path, "r") as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)


def load_release_config(config_path="config/release-config.yaml") -> Dict[str, TeamInfo]:
    project_root = Path(__file__).parent.parent.parent.parent
    absolute_config_path = project_root / config_path
    with open(absolute_config_path, "r") as f:
        data = yaml.safe_load(f)
        teams = {team["name"]: TeamInfo(**team) for team in data.get("teams", [])}
        releases = data.get("releases", [])
        return releases, teams


def get_release_info(releases: List[Dict], teams: Dict[str, TeamInfo], release_version: str) -> ReleaseInfo:
    for release_data in releases:
        if release_data.get("release_version") == release_version:
            team_name = release_data.get("team_name")
            team_info = teams.get(team_name)
            if team_info:
                return ReleaseInfo(
                    release_version=release_data.get("release_version"),
                    branch_cut_date=release_data.get("branch_cut_date"),
                    team_name=team_name,
                    teams=[team_info]
                )
    return None