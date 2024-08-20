from pydantic import BaseModel, RootModel, computed_field
from sqlmodel import Field, SQLModel, Relationship
from typing import Any, Generator, Optional
import datetime
import logging

logger = logging.getLogger(__name__)


def date(dt: datetime) -> str:
    return dt.strftime(r"%Y-%m-%d")


def first_word(s):
    return s.split(" ")[0]


# All these classes are for MatchesResponse being turned into a list[Match]
class Match(BaseModel):
    id: int
    status: str
    startTime: datetime.datetime
    type: str

    @property
    def startDate(self) -> str:
        return date(self.startTime)


class Session(BaseModel):
    id: int
    name: str


class Team(BaseModel):
    id: int
    name: str
    number: str
    session: Session
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
    displayName: str

    @property
    def first_name(self) -> str:
        return first_word(self.displayName)


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
    startTime: datetime.datetime
    home: TeamFromMatchDetails
    away: TeamFromMatchDetails
    fees: FeesFromMatchDetails
    results: list[Results]

    def get_players(self):
        for r in self.results:
            yield from r.get_players()

    @property
    def startDate(self) -> str:
        return date(self.startTime)


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


class MatchesDateList(BaseModel):
    date: str
    matches: list[Match]

    @property
    def matches_hash(self) -> str:
        return ",".join([str(m.id) for m in self.matches])


def matches_date_list(matches: list[Match]) -> list[MatchesDateList]:
    match_days: dict[str, list[Match]] = {}
    for m in matches:
        date = m.startDate
        if date not in match_days:
            match_days[date] = []
        match_days[date].append(m)

    l = [MatchesDateList(date=d, matches=m) for d, m in match_days.items()]
    # Reverse the list so that the most recent dates are first in the list
    return reversed(l)


class PlayerBill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    status: str = ""
    invoice: "Invoice" = Relationship(back_populates="bills")
    invoice_id: int = Field(foreign_key="invoice.id")
    player_name: str

    @computed_field
    @property
    def currency_str(self) -> str:
        v = self.amount
        if self.amount.is_integer():
            v = int(v)
        return f"${v}"

    @computed_field
    @property
    def first_name(self) -> str:
        return first_word(self.player_name)


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    bills: list[PlayerBill] = Relationship(
        back_populates="invoice", sa_relationship_kwargs={"lazy": "joined"}
    )
    matches_hash: str = Field(index=True)
    session_name: str


class MetadataRefresh(SQLModel, table=True):
    id: int = Field(default=0, primary_key=True)
    last_refresh: datetime.datetime
