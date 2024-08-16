from apainvoice import db, invoice, ppapi, models
import logging
import sqlmodel

logger = logging.getLogger(__name__)


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
            inv = invoice.make_invoice(api, match_details)

            # session.add(inv)
            # session.commit()
            exit()
