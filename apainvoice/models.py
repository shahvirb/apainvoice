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


class Team(BaseModel):
    id: int
    name: str
    number: str
    matches: list[Match]


class Viewer(BaseModel):
    id: int
    teams: list[Team]
    __typename: str


class Data(BaseModel):
    viewer: Viewer


class MRData(BaseModel):
    data: Data


class MatchesResponse(RootModel):
    root: list[MRData]

    def matches(self) -> Generator[Any, Any, Any]:
        for mrdata in self.root:
            for team in mrdata.data.viewer.teams:
                for match in team.matches:
                    yield match

    def completed_matches(self) -> list[Match]:
        return [m for m in self.matches() if m.status == "COMPLETED"]


# --- End Match and associated classes


class MatchesDateListEntry(BaseModel):
    date: str
    matches: list[Match]


def matches_date_list(matches: list[Match]) -> list[MatchesDateListEntry]:
    match_days: dict[str, list[Match]] = {}
    for m in matches:
        date = m.startDate
        if date not in match_days:
            match_days[date] = []
        match_days[date].append(m)

    l = [MatchesDateListEntry(date=d, matches=m) for d, m in match_days.items()]
    # Reverse the list so that the most recent dates are first in the list
    return reversed(l)


class PlayerBill(BaseModel):
    name: str
    amount: int
