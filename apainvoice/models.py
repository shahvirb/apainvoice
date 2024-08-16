from pydantic import BaseModel, RootModel
from sqlmodel import Field, SQLModel, Relationship
from typing import Any, Generator, Optional
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
class Player(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    displayName: str
    bills: list["PlayerBill"] = Relationship(back_populates="player")


class Scores(BaseModel):
    id: int
    player: Player


class Results(BaseModel):
    homeAway: str
    scores: list[Scores]

    def get_players(self):
        for sc in self.scores:
            yield sc.player


class FeesFromMatchDetails(BaseModel):
    total: int


class TeamFromMatchDetails(BaseModel):
    id: int
    name: str
    number: str
    isMine: bool

# Nomenclature: a match in this context is a set of matches played in one game type. E.g., all 5 matches played in 8 ball that night
# class MatchDetails(SQLModel, table=True):
class MatchDetails(BaseModel):
    id: int = Field(default=None, primary_key=True)
    type: str
    startTime: str
    home: TeamFromMatchDetails
    away: TeamFromMatchDetails
    fees: FeesFromMatchDetails
    results: list[Results]

    def get_players(self):
        for r in self.results:
            yield from r.get_players()


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


class PlayerBill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # name: str
    amount: int
    status: str = ""
    # invoice: "Invoice" = Relationship(back_populates="bills")
    player: Player = Relationship(back_populates="bills")
    player_id: int = Field(foreign_key="player.id")


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # match_ids: list[int]  # = Field(default=None, foreign_key="parent.id")
    # bills: list[PlayerBill] = Relationship(back_populates="invoice")
