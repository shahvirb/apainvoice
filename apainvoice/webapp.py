from apainvoice import models, ppapi, invoice
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayLookup
import logging
import uvicorn

logger = logging.getLogger(__name__)

app = FastAPI()


def generate_bill(
    api: ppapi.PoolPlayersAPI, mdle=models.MatchesDateListEntry
) -> list[AnyComponent]:
    bills = invoice.calculate_bills(api, [m.id for m in mdle.matches])
    logger.info(f"Calculating bills for {len(mdle.matches)} matches on {mdle.date}")
    return [
        c.Heading(text=mdle.date, level=2),
        c.Table(
            data=bills,
            columns=[
                DisplayLookup(field="name"),
                DisplayLookup(field="amount"),
            ],
        ),
    ]


def generate_bills() -> list[AnyComponent]:
    api = ppapi.PersistentDataAPI()
    completed = api.fetch_completed_matches()
    date_list = models.matches_date_list(completed)
    components = []
    for mdle in date_list:
        components.extend(generate_bill(api, mdle))
    return components


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def landing_page() -> list[AnyComponent]:
    """
    `/api` is the endpoint the frontend will connect to
    when a user visits `/` to fetch components to render.
    """

    return [
        c.Page(components=generate_bills()),
    ]


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="APA Invoice"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn.run(
        "webapp:app", log_config=log_config, host="0.0.0.0", port=8001, reload=True
    )
