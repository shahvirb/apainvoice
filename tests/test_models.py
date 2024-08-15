from apainvoice import ppapi, models
import typing
import json


def read_json_file(filepath: str) -> typing.Any:
    with open(filepath) as f:
        return json.load(f)


def test_match_details():
    contents = read_json_file("tests/match page response.json")
    mdr = models.MatchDetailsResponse.model_validate(contents)
    details = mdr.get_match_details()
    assert details.id == contents[0]["data"]["match"]["id"]


def test_matches_response():
    contents = read_json_file("tests/matches response.json")
    resp = models.MatchesResponse.model_validate(contents)
