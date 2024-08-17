from apainvoice import models, controller
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayLookup
import logging
import uvicorn

logger = logging.getLogger(__name__)

app = FastAPI()


def render_invoice(invoice: models.Invoice) -> list[AnyComponent]:
    components = [
        c.Heading(text=invoice.name, level=2),
        c.Table(
            data=invoice.bills,
            columns=[
                DisplayLookup(field="player_name"),
                DisplayLookup(field="amount"),
            ],
        ),
    ]
    return components


def render_all_invoices() -> list[AnyComponent]:
    invoices = controller.get_invoices()
    logger.debug(f"Got {len(invoices)} invoices")
    # return [c.Heading(text="debug remove me", level=1)]
    components = []
    for inv in invoices:
        components.extend(render_invoice(inv))
    return components


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def landing_page() -> list[AnyComponent]:
    """
    `/api` is the endpoint the frontend will connect to
    when a user visits `/` to fetch components to render.
    """

    return [
        c.Page(components=render_all_invoices()),
    ]


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="APA Invoice"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["loggers"]["uvicorn"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.error"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.access"]["level"] = "DEBUG"
    log_config["disable_existing_loggers"] = "false"

    uvicorn.run(
        "webapp:app", log_config=log_config, host="0.0.0.0", port=8001, reload=True
    )
