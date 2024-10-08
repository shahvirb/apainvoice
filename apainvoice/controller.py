from apainvoice import db, ppapi, models
import logging
import sqlmodel
import datetime

from apainvoice.players import player_names

logger = logging.getLogger(__name__)


def make_invoice(
    api: ppapi.PoolPlayersAPI,
    matches_date_list: models.MatchesDateList,
    session_name: str,
) -> models.Invoice:

    matchdetails = [api.get_match_details(m.id) for m in matches_date_list.matches]
    assert matchdetails
    logger.info(
        f"Making invoice for date {matches_date_list.date} comprising of {len(matches_date_list.matches)} matches"
    )

    fees_sum = 0
    invoice_name = matchdetails[0].startDate
    players: list[models.Player] = []
    players_on_team = player_names()

    # Find players involved in matches and calculate fees_sum
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
                amount=single_fee, player_name=p.displayName
            )
        else:
            bills[p.displayName].amount += single_fee

    invoice = models.Invoice(
        name=invoice_name,
        bills=list(bills.values()),
        matches_hash=matches_date_list.matches_hash,
        session_name=session_name,
    )
    return invoice


def all_invoices(api: ppapi.PoolPlayersAPI, session):
    completed, session_name = api.fetch_completed_matches()
    matches_date_list = models.matches_date_list(completed)
    for mdl in matches_date_list:
        results = (
            session.exec(
                sqlmodel.select(models.Invoice).where(
                    models.Invoice.matches_hash == mdl.matches_hash
                )
            )
            .unique()
            .all()
        )
        assert len(results) <= 1
        if results:
            inv = results[0]
            logger.info(f"Found existing invoice {inv.name}")
            yield inv
        else:
            inv = make_invoice(api, mdl, session_name)
            session.add(inv)
            session.commit()
            yield inv


def update_invoices():
    api = ppapi.PoolPlayersAPI()

    with sqlmodel.Session(db.create_engine()) as session:
        invoices = list(all_invoices(api, session))
        # return invoices

        results = session.exec(sqlmodel.select(models.MetadataRefresh)).all()
        meta: models.MetadataRefresh
        if not results:
            meta = models.MetadataRefresh(id=0, last_refresh=datetime.datetime.now())
        else:
            assert len(results) == 1
            meta = results[0]
            logger.info(f"Previous data update: {meta.last_refresh}")
            meta.last_refresh = datetime.datetime.now()
        session.add(meta)
        session.commit()
        logger.info(f"Data updated at: {meta.last_refresh}")


def get_invoices():
    with sqlmodel.Session(db.create_engine()) as session:
        return session.exec(sqlmodel.select(models.Invoice)).unique().all()


def sort_most_recent(invoices: list[models.Invoice]):
    return sorted(invoices, key=lambda inv: inv.name, reverse=True)


def get_metadata() -> models.MetadataRefresh:
    with sqlmodel.Session(db.create_engine()) as session:
        return session.exec(sqlmodel.select(models.MetadataRefresh)).one()


def get_bill(id: int) -> models.PlayerBill:
    with sqlmodel.Session(db.create_engine()) as session:
        return session.exec(
            sqlmodel.select(models.PlayerBill).where(models.PlayerBill.id == id)
        ).one()


def get_invoice(id: int) -> models.Invoice:
    with sqlmodel.Session(db.create_engine()) as session:
        return (
            session.exec(sqlmodel.select(models.Invoice).where(models.Invoice.id == id))
            .unique()
            .one()
        )


def write_db(x: models.PlayerBill | models.Invoice) -> bool:
    with sqlmodel.Session(db.create_engine()) as session:
        session.add(x)
        session.commit()
        return True
    return False
