from apainvoice import ppapi, pydmodels
import logging

logger = logging.getLogger(__name__)

PLAYERS = [
    "Madhav Sharma",
    "Stephanie Papageorge",
    "Samkit Shah",
    "Dion King",
    "Alberto Calderon",
    "Joe Flores",
    "Shahvir Buhariwalla",
    "Paul Shelton",
]

SINGLE_MATCH_BILL_AMOUNT = 8


def calculate_bills(api: ppapi.PoolPlayersAPI, match_ids: list[int]):
    """Calculate a bill with matches of ID specified in match_ids

    Args:
        api (ppapi.PoolPlayersAPI): api object to fetch data
        match_ids (list[int]): IDs of matches to use in the bill
    """
    players: list[str] = []
    for id in match_ids:
        players.extend([p for p in api.fetch_players(id) if p in PLAYERS])

    bills = {}
    for name in players:
        if name not in bills:
            bills[name] = SINGLE_MATCH_BILL_AMOUNT
        else:
            bills[name] += SINGLE_MATCH_BILL_AMOUNT

    player_bills = [
        pydmodels.PlayerBill(name=name, amount=amt) for name, amt in bills.items()
    ]
    return player_bills


if __name__ == "__main__":
    api = ppapi.PersistentDataAPI()
    bills = calculate_bills(api, [42940044])
    print(bills)
