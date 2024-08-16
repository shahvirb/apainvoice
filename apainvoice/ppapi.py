from apainvoice import db, models
import json
import logging
import requests
import sqlmodel
import typing

logger = logging.getLogger(__name__)

GQLURL = "https://gql.poolplayers.com/graphql"
DEFAULT_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVyTjd2TDlFOUlwWUlnTjJsQ0JMdFd0TnhBZXRYaHkxNUJwNzl4a18wOVEifQ.eyJhcHBsaWNhdGlvblJlZnJlc2hUb2tlbklkIjoiNDY5NDM1NiIsImlhdCI6MTcyMjQ2Mzc1MywiaXNzIjoiQVBBIiwic3ViIjoiMjI3ODQ5MyJ9.POx2fQMK1ZkGK87aSjZxCJ45UVg01r-IvtzLnahNCXu4SzKEMfgX7cRnUiLqQhbmsq6-kiYclJBfZDcDhc6EMrspR30Y4CgqyJoSPW1_sSDSi7xUs4UP6Rjo4mqVdmAgc25qHUjDGDIzIikTjsQFCr6YzEpt600G4Vtskl9ZyRPYoi9h_CM8i_alXywepK9L4YALIq2pw08ePZSy5dMVqeVYOqkXBByQBfgV-UAnbA5LTrwbtVqMrfQ5RfyfwaOBnuwh2tKxr-wBa2Nb_WoFK3cYrSmkEMxUSwk-ps0kyKPG2qYmTIIc5FaodO4vXAoOG27FcsNTnUj4cGR6eebRFA"


DEFAULT_HEADER = {
    "Content-Type": "application/json",
    "Origin": "https://league.poolplayers.com",
}


class ResponseOKWithErrorsData(Exception):
    "Raised if the response dictionary has a key named 'errors'"
    pass


def json_to_dict(response: requests.Response) -> typing.Any:
    return json.loads(response.text)


def post_data(headers: dict | None, json_data: dict) -> typing.Any:
    merged_headers = DEFAULT_HEADER | (headers if headers else {})
    response = requests.post(GQLURL, headers=merged_headers, json=json_data)
    assert response.status_code == 200

    resp_dict = json_to_dict(response)
    for rd in resp_dict:
        if "errors" in rd.keys():
            raise ResponseOKWithErrorsData

    return resp_dict


def parse_players(match_results) -> list[str]:
    all = []
    for results in match_results[0]["data"]["match"]["results"]:
        for score in results["scores"]:
            name = score["player"]["displayName"]
            logger.debug(f"Found player: {name}")
            all.append(name)
    assert len(all) > 0
    return all


class PoolPlayersAPI:
    def __init__(self) -> None:
        self.access_token = self.refresh_access_token()

    def refresh_access_token(self, refresh_token: str = DEFAULT_ACCESS_TOKEN) -> str:
        logger.info("refreshing access token")
        data = [
            {
                "operationName": "GenerateAccessTokenMutation",
                "variables": {
                    "refreshToken": (
                        refresh_token if refresh_token else DEFAULT_ACCESS_TOKEN
                    )
                },
                "query": "mutation GenerateAccessTokenMutation($refreshToken: String!) {\n  generateAccessToken(refreshToken: $refreshToken) {\n    accessToken\n    __typename\n  }\n}\n",
            }
        ]

        answer = post_data(None, data)
        return answer[0]["data"]["generateAccessToken"]["accessToken"]

    def post_auth_data(self, json_data: dict) -> typing.Any:
        headers = {
            "Authorization": self.access_token,
        }
        return post_data(headers, json_data)

    def get_match_details(self, id: int) -> models.MatchDetails:
        data = [
            {
                "operationName": "MatchPage",
                "variables": {"id": id},
                "query": "query MatchPage($id: Int!) {\n  match(id: $id) {\n    id\n    division {\n      id\n      electronicScoringEnabled\n      __typename\n    }\n    league {\n      id\n      esEnabled\n      __typename\n    }\n    ...matchForCart\n    __typename\n  }\n}\n\nfragment matchForCart on Match {\n  __typename\n  id\n  type\n  startTime\n  week\n  isBye\n  isMine\n  isScored\n  scoresheet\n  isPaid\n  location {\n    ...googleMapComponent\n    __typename\n  }\n  home {\n    id\n    name\n    number\n    isMine\n    ...rosterComponent\n    __typename\n  }\n  away {\n    id\n    name\n    number\n    isMine\n    ...rosterComponent\n    __typename\n  }\n  division {\n    id\n    scheduleInEdit\n    type\n    __typename\n  }\n  session {\n    id\n    name\n    year\n    __typename\n  }\n  league {\n    id\n    name\n    currentSessionId\n    isElectronicPaymentsEnabled\n    country {\n      id\n      __typename\n    }\n    __typename\n  }\n  fees {\n    amount\n    tax\n    total\n    __typename\n  }\n  orderItems {\n    id\n    order {\n      id\n      member {\n        id\n        firstName\n        lastName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  results {\n    homeAway\n    overUnder\n    forfeits\n    matchesWon\n    matchesPlayed\n    points {\n      bonus\n      penalty\n      won\n      adjustment\n      sportsmanship\n      total\n      skillLevelViolationAdjustment\n      __typename\n    }\n    scores {\n      id\n      player {\n        id\n        displayName\n        __typename\n      }\n      matchPositionNumber\n      playerPosition\n      skillLevel\n      innings\n      defensiveShots\n      eightBallWins\n      eightOnBreak\n      eightBallBreakAndRun\n      nineBallPoints\n      nineOnSnap\n      nineBallBreakAndRun\n      nineBallMatchPointsEarned\n      mastersEightBallWins\n      mastersNineBallWins\n      winLoss\n      matchForfeited\n      doublesMatch\n      dateTimeStamp\n      teamSlot\n      eightBallMatchPointsEarned\n      incompleteMatch\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment googleMapComponent on HostLocation {\n  id\n  phone\n  name\n  address {\n    id\n    name\n    address1\n    address2\n    city\n    zip\n    latitude\n    longitude\n    __typename\n  }\n  __typename\n}\n\nfragment rosterComponent on Team {\n  id\n  name\n  number\n  league {\n    id\n    slug\n    __typename\n  }\n  division {\n    id\n    type\n    __typename\n  }\n  roster {\n    id\n    memberNumber\n    displayName\n    matchesWon\n    matchesPlayed\n    ... on EightBallPlayer {\n      pa\n      ppm\n      skillLevel\n      __typename\n    }\n    ... on NineBallPlayer {\n      pa\n      ppm\n      skillLevel\n      __typename\n    }\n    member {\n      id\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",
            }
        ]

        logger.info(f"Querying MatchPage id={id}")
        answer = self.post_auth_data(data)
        response = models.MatchDetailsResponse.model_validate(answer)
        return response.get_match_details()

    def get_matches(self):
        data = [
            {
                "operationName": "matchesByViewer",
                "variables": {},
                "query": "query matchesByViewer {\n  viewer {\n    id\n    ... on Member {\n      teams {\n        id\n        name\n        number\n        session {\n          id\n          name\n          __typename\n        }\n        matches {\n          type\n          ...matchListItem\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment matchListItem on Match {\n  id\n  isBye\n  status\n  scoresheet\n  startTime\n  isMine\n  isPaid\n  isPlayoff\n  description\n  results {\n    homeAway\n    points {\n      total\n      __typename\n    }\n    __typename\n  }\n  location {\n    id\n    name\n    address {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  home {\n    id\n    name\n    number\n    isMine\n    __typename\n  }\n  away {\n    id\n    name\n    number\n    isMine\n    __typename\n  }\n  league {\n    id\n    isMine\n    slug\n    isElectronicPaymentsEnabled\n    __typename\n  }\n  orderItems {\n    id\n    order {\n      id\n      member {\n        id\n        firstName\n        lastName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  division {\n    id\n    scheduleInEdit\n    __typename\n  }\n  __typename\n}\n",
            },
        ]

        logger.info(f"Querying for matches")
        answer = self.post_auth_data(data)
        return answer

    def fetch_players(self, match_id: int) -> list[str]:
        match_data = self.get_match_details(match_id)
        return parse_players(match_data)

    def fetch_completed_matches(self) -> list[models.Match]:
        matches = self.get_matches()
        mr = models.MatchesResponse.model_validate(matches)
        completed_matches = mr.completed_matches()
        logger.info(f"Found {len(completed_matches)} completed matches")
        return completed_matches


class PersistentDataAPI(PoolPlayersAPI):
    def __init__(self) -> None:
        super().__init__()

    # def get_match_details(self, id: int) -> models.MatchDetails:
    #     with sqlmodel.Session(db.create_engine()) as session:
    #         query = sqlmodel.select(models.MatchDetails).where(models.MatchDetails.id == id)
    #         mp = session.exec(query).first()
    #         if not mp:
    #             mp = super().get_match_details(id)
    #             session.add(mp)
    #             session.commit()
    #         return mp

        # dbc = db.ReaderWriter()
        # match_data = dbc.read("match_data")
        # if id not in match_data:
        #     data = db.create_data_dict(super().get_match_data(id))
        #     match_data[id] = data
        #     dbc.write("match_data", match_data)
        # return match_data[id]["data"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    api = PersistentDataAPI()

    completed_matches = api.fetch_completed_matches()
    # date_list = pydmodels.matches_date_list(completed_matches)

    players = api.fetch_players(42940044)
    print(players)
