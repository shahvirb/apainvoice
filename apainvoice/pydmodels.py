from pydantic import BaseModel, Field
from pydantic import BaseModel, RootModel
from typing import Any, Generator
import datetime
import logging

logger = logging.getLogger(__name__)


# All these classes are for MatchResponse being turned into a list[Match]
class Match(BaseModel):
    id: int
    status: str
    startTime: datetime.datetime
    type: str

    @property
    def startDate(self) -> str:
        return self.startTime.strftime(r"%Y-%m-%d")


class Matches(BaseModel):
    matches: list[Match]


class Teams(BaseModel):
    teams: list[Matches]


class Viewer(BaseModel):
    viewer: Teams


class Data(BaseModel):
    data: Viewer


class MatchesResponse(RootModel):
    root: list[Data]

    def matches(self) -> Generator[Any, Any, Any]:
        for data in self.root:
            for team in data.data.viewer.teams:
                for match in team.matches:
                    yield match

    def completed_matches(self) -> list[Match]:
        return [m for m in self.matches() if m.status == "COMPLETED"]


# --- End Match and associated classes


class MatchesDateListEntry(BaseModel):
    date: str
    matches: list[Match]


def matches_date_list(matches: list[MatchesDateListEntry]):
    match_days = {}
    for m in matches:
        date = m.startDate
        if date not in match_days:
            match_days[date] = []
        match_days[date].append(m)

    l = [MatchesDateListEntry(date=d, matches=m) for d, m in match_days.items()]
    return reversed(l)


class PlayerBill(BaseModel):
    name: str
    amount: int
