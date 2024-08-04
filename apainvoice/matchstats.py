import json
import requests

GQLURL = "https://gql.poolplayers.com/graphql"

def response_to_dict(response):
    return json.loads(response.text)


def get_access_token():
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://league.poolplayers.com',
    }
    payload_text = r'''
    [{"operationName":"GenerateAccessTokenMutation","variables":{"refreshToken":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjVyTjd2TDlFOUlwWUlnTjJsQ0JMdFd0TnhBZXRYaHkxNUJwNzl4a18wOVEifQ.eyJhcHBsaWNhdGlvblJlZnJlc2hUb2tlbklkIjoiNDY5NDM1NiIsImlhdCI6MTcyMjQ2Mzc1MywiaXNzIjoiQVBBIiwic3ViIjoiMjI3ODQ5MyJ9.POx2fQMK1ZkGK87aSjZxCJ45UVg01r-IvtzLnahNCXu4SzKEMfgX7cRnUiLqQhbmsq6-kiYclJBfZDcDhc6EMrspR30Y4CgqyJoSPW1_sSDSi7xUs4UP6Rjo4mqVdmAgc25qHUjDGDIzIikTjsQFCr6YzEpt600G4Vtskl9ZyRPYoi9h_CM8i_alXywepK9L4YALIq2pw08ePZSy5dMVqeVYOqkXBByQBfgV-UAnbA5LTrwbtVqMrfQ5RfyfwaOBnuwh2tKxr-wBa2Nb_WoFK3cYrSmkEMxUSwk-ps0kyKPG2qYmTIIc5FaodO4vXAoOG27FcsNTnUj4cGR6eebRFA"},"query":"mutation GenerateAccessTokenMutation($refreshToken: String!) {\n  generateAccessToken(refreshToken: $refreshToken) {\n    accessToken\n    __typename\n  }\n}\n"}]
    '''
    data = json.loads(payload_text)
    response = requests.post(GQLURL, headers=headers, json=data)
    return response_to_dict(response)[0]['data']['generateAccessToken']['accessToken']

def get_match_data(access_token):
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json',
        'Origin': 'https://league.poolplayers.com',
    }
    
    payload_text = r'''
    [{"operationName":"MatchPage","variables":{"id":42940044},"query":"query MatchPage($id: Int!) {\n  match(id: $id) {\n    id\n    division {\n      id\n      electronicScoringEnabled\n      __typename\n    }\n    league {\n      id\n      esEnabled\n      __typename\n    }\n    ...matchForCart\n    __typename\n  }\n}\n\nfragment matchForCart on Match {\n  __typename\n  id\n  type\n  startTime\n  week\n  isBye\n  isMine\n  isScored\n  scoresheet\n  isPaid\n  location {\n    ...googleMapComponent\n    __typename\n  }\n  home {\n    id\n    name\n    number\n    isMine\n    ...rosterComponent\n    __typename\n  }\n  away {\n    id\n    name\n    number\n    isMine\n    ...rosterComponent\n    __typename\n  }\n  division {\n    id\n    scheduleInEdit\n    type\n    __typename\n  }\n  session {\n    id\n    name\n    year\n    __typename\n  }\n  league {\n    id\n    name\n    currentSessionId\n    isElectronicPaymentsEnabled\n    country {\n      id\n      __typename\n    }\n    __typename\n  }\n  fees {\n    amount\n    tax\n    total\n    __typename\n  }\n  orderItems {\n    id\n    order {\n      id\n      member {\n        id\n        firstName\n        lastName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  results {\n    homeAway\n    overUnder\n    forfeits\n    matchesWon\n    matchesPlayed\n    points {\n      bonus\n      penalty\n      won\n      adjustment\n      sportsmanship\n      total\n      skillLevelViolationAdjustment\n      __typename\n    }\n    scores {\n      id\n      player {\n        id\n        displayName\n        __typename\n      }\n      matchPositionNumber\n      playerPosition\n      skillLevel\n      innings\n      defensiveShots\n      eightBallWins\n      eightOnBreak\n      eightBallBreakAndRun\n      nineBallPoints\n      nineOnSnap\n      nineBallBreakAndRun\n      nineBallMatchPointsEarned\n      mastersEightBallWins\n      mastersNineBallWins\n      winLoss\n      matchForfeited\n      doublesMatch\n      dateTimeStamp\n      teamSlot\n      eightBallMatchPointsEarned\n      incompleteMatch\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment googleMapComponent on HostLocation {\n  id\n  phone\n  name\n  address {\n    id\n    name\n    address1\n    address2\n    city\n    zip\n    latitude\n    longitude\n    __typename\n  }\n  __typename\n}\n\nfragment rosterComponent on Team {\n  id\n  name\n  number\n  league {\n    id\n    slug\n    __typename\n  }\n  division {\n    id\n    type\n    __typename\n  }\n  roster {\n    id\n    memberNumber\n    displayName\n    matchesWon\n    matchesPlayed\n    ... on EightBallPlayer {\n      pa\n      ppm\n      skillLevel\n      __typename\n    }\n    ... on NineBallPlayer {\n      pa\n      ppm\n      skillLevel\n      __typename\n    }\n    member {\n      id\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"}]
    '''
    data = json.loads(payload_text)
    response = requests.post(GQLURL, headers=headers, json=data)
    return response


if __name__ == "__main__":
    at = get_access_token()
    # print(at)
    
    response = get_match_data(at)
    print(response.text)