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
    invoice_name = matchdetails[0].startDate
    players: list[models.Player] = []

    for md in matchdetails:
        assert (
            invoice_name == md.startDate
        )  # Assert that an invoice is only for one date
        fees_sum += md.fees.total
        for p in md.get_players():
            if p.displayName in PLAYERS:
                players.append(p)
                logger.info(
                    f"Found player {p.displayName} in match ID={md.id} type={md.type}"
                )

    single_fee = round(fees_sum / len(players), 2)
    logger.info(f"single_fee = {fees_sum} / {len(players)} == {single_fee}")
    bills: dict[str, models.PlayerBill] = {}
    for p in players:
        if p.displayName not in bills:
            bills[p.displayName] = models.PlayerBill(
                amount=single_fee, player_name=p.displayName, player=p
            )
        else:
            bills[p.displayName].amount += single_fee

    invoice = models.Invoice(name=invoice_name, bills=list(bills.values()))
    # TODO shouldn't we also link an invoice to models.MatchDetails ?
    return invoice


if __name__ == "__main__":
    api = ppapi.PoolPlayersAPI()
    mds = [api.get_match_details(42940044), api.get_match_details(42939976)]
    inv = make_invoice(api, mds)
    # bills = calculate_bills(api, [42940044])

    # print(bills)
