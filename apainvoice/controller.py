from apainvoice import db, ppapi, models
import logging
import sqlmodel
import base64

logger = logging.getLogger(__name__)


# Obfucsate player names for basic privacy in public code repos
B64_PLAYERS = [
    "TWFkaGF2IFNoYXJtYQ==",  # Ma Sh
    "U3RlcGhhbmllIFBhcGFnZW9yZ2U=",  # St Pa
    "U2Fta2l0IFNoYWg=",  # Sa Sh
    "RGlvbiBLaW5n",  # Di Ki
    "QWxiZXJ0byBDYWxkZXJvbg==",  # Al Ca
    "Sm9lIEZsb3Jlcw==",  # Jo Fl
    "U2hhaHZpciBCdWhhcml3YWxsYQ==",  # Sh Bu
    "UGF1bCBTaGVsdG9u",  # Pa Sh
]


def player_names(names: list[str] = B64_PLAYERS) -> list[str]:
    return [base64.b64decode(encoded_name.encode()).decode() for encoded_name in names]


def make_invoice(
    api: ppapi.PoolPlayersAPI, matchdetails: list[models.MatchDetails]
) -> models.Invoice:
    assert matchdetails
    fees_sum = 0
    invoice_name = matchdetails[0].startDate
    players: list[models.Player] = []
    players_on_team = player_names()

    # Find the players involved in the matches and calculate fees_sum
    for md in matchdetails:
        assert (
            invoice_name == md.startDate
        )  # Assert that an invoice is only for one date
        fees_sum += md.fees.total
        for p in md.get_players():
            if p.displayName in players_on_team:
                players.append(p)
                logger.info(
                    f"Found player {p.displayName} in match ID={md.id} type={md.type}"
                )

    single_fee = round(fees_sum / len(players), 2)
    logger.info(f"single_fee = {fees_sum} / {len(players)} == {single_fee}")

    # Calculate a bill for a each player
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
    logging.basicConfig(level=logging.DEBUG)

    api = ppapi.PoolPlayersAPI()
    dbengine = db.create_engine()

    with sqlmodel.Session(dbengine) as session:
        completed = api.fetch_completed_matches()
        logger.info(f"Queried and found {len(completed)} completed matches")
        matches_date_list = models.matches_date_list(completed)
        for mdl in matches_date_list:
            match_details = [api.get_match_details(m.id) for m in mdl.matches]
            logger.info(
                f"Making invoice for date {mdl.date} comprising of {len(mdl.matches)} matches"
            )
            inv = make_invoice(api, match_details)

            session.add(inv)
            session.commit()
            exit()
