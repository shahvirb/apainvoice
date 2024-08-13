from pydantic import BaseModel, Field
from pydantic import BaseModel, RootModel


class Match(BaseModel):
    id: int
    status: str
    startTime: str
    type: str

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

    def completed_matches(self):
        pass

class PlayerBill(BaseModel):
    name: str
    amount: int
