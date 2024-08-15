from pydantic import BaseModel, RootModel
from sqlmodel import Field, SQLModel
from typing import Any, Generator
import datetime
import logging

logger = logging.getLogger(__name__)


# All these classes are for MatchesResponse being turned into a list[Match]
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


class MatchesResponseData(BaseModel):
    data: Data


class MatchesResponse(RootModel):
    root: list[MatchesResponseData]

    def matches(self) -> Generator[Any, Any, Any]:
        for mrdata in self.root:
            for team in mrdata.data.viewer.teams:
                for match in team.matches:
                    yield match

    def completed_matches(self) -> list[Match]:
        return [m for m in self.matches() if m.status == "COMPLETED"]


# --- End Match and associated classes


# All these classes are for MatchDetails and associated classes
class Player(BaseModel):
    id: int
    displayName: str


class Scores(BaseModel):
    id: int
    player: Player


class Results(BaseModel):
    homeAway: str
    scores: list[Scores]


class FeesFromMatchDetails(BaseModel):
    total: int


class TeamFromMatchDetails(BaseModel):
    id: int
    name: str
    number: str
    isMine: bool


# class MatchDetails(SQLModel, table=True):
class MatchDetails(BaseModel):
    id: int = Field(default=None, primary_key=True)
    type: str
    startTime: str
    home: TeamFromMatchDetails
    away: TeamFromMatchDetails
    fees: FeesFromMatchDetails
    results: list[Results]


class MatchDetailsMatch(BaseModel):
    match: MatchDetails


class MatchDetailsResponseData(BaseModel):
    data: MatchDetailsMatch


class MatchDetailsResponse(RootModel):
    root: list[MatchDetailsResponseData]

    def get_match_details(self) -> MatchDetails:
        assert len(self.root) == 1
        return self.root[0].data.match


# --- End MatchDetails and associated classes


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
