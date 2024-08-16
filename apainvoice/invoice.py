from apainvoice import models, ppapi
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


# def calculate_bills(api: ppapi.PoolPlayersAPI, match_ids: list[int]):
#     """Calculate a bill with matches of ID specified in match_ids

#     Args:
#         api (ppapi.PoolPlayersAPI): api object to fetch data
#         match_ids (list[int]): IDs of matches to use in the bill
#     """
#     players: list[str] = []
#     for id in match_ids:
#         players.extend([p for p in api.fetch_players(id) if p in PLAYERS])

#     bills = {}
#     for name in players:
#         if name not in bills:
#             bills[name] = SINGLE_MATCH_BILL_AMOUNT
#         else:
#             bills[name] += SINGLE_MATCH_BILL_AMOUNT

#     player_bills = [
#         models.PlayerBill(name=name, amount=amt) for name, amt in bills.items()
#     ]
#     return player_bills


# TODO this should take a list of MatchDetails
def make_invoice(
    api: ppapi.PoolPlayersAPI, matchdetails: list[models.MatchDetails]
) -> models.Invoice:
    assert matchdetails

    fees_sum = 0
    invoice_name = matchdetails[0].startDate()
    players: list[models.Player] = []
    for md in matchdetails:
        assert (
            invoice_name == md.startDate()
        )  # Assert that an invoice is only for one date
        fees_sum += md.fees.total
        for p in md.get_players():
            if p.displayName in PLAYERS:
                players.append(p)

    single_fee = fees_sum / len(players)
    bills: dict[int, models.PlayerBill] = {}
    for p in players:
        if p.id not in bills:
            bills[p.id] = models.PlayerBill(amount=single_fee, player_id=p.id, player=p)
        else:
            bills[p.id].amount += single_fee

    invoice = models.Invoice(name=invoice_name, bills=list(bills.values()))
    return invoice


if __name__ == "__main__":
    api = ppapi.PersistentDataAPI()
    mds = [api.get_match_details(42940044), api.get_match_details(42939976)]
    inv = make_invoice(api, mds)
    # bills = calculate_bills(api, [42940044])

    # print(bills)
