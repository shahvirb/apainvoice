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
    # TODO shouldn't we also link an invoice to models.MatchDetails ?
    return invoice


if __name__ == "__main__":
    api = ppapi.PoolPlayersAPI()
    mds = [api.get_match_details(42940044), api.get_match_details(42939976)]
    inv = make_invoice(api, mds)
    # bills = calculate_bills(api, [42940044])

    # print(bills)
