from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class TeamInfo:
    name: str
    em: str
    em_email: str
    sm: str
    sm_email: str


@dataclass
class ReleaseInfo:
    release_version: str
    branch_cut_date: str
    team_name: str
    teams: List[TeamInfo]


@dataclass
class ReportConfig:
    name: str
    jql_template: str


@dataclass
class IssueDetails:
    key: str
    summary: str
    assignee: str
    assignee_email: str
    reporter: str
    reporter_email: str
    priority: str
    status: str
    time_in_status: float
    time_to_assign: float
    time_in_each_status: Dict[str, float]
    created: datetime
    resolution_date: Optional[datetime] = None


@dataclass
class ReportData:
    name: str
    jql: str
    issues: List[IssueDetails]
