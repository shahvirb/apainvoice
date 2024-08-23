from apainvoice import models, controller
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent, PageEvent
from fastui.forms import (
    FormFile,
    SelectSearchResponse,
    Textarea,
    fastui_form,
    SelectOptions,
)
import logging
import typing

logger = logging.getLogger(__name__)

app = FastAPI()

# TODO should we import pydantic here?
from pydantic import BaseModel, RootModel, Field, computed_field


class TestFormModel(BaseModel):
    mpaid: bool | None = Field(None, title="Paid", json_schema_extra={"mode": "switch"})


def render_invoice(invoice: models.Invoice, admin: bool = False) -> list[AnyComponent]:
    table_cols = [
        DisplayLookup(field="first_name", title="Name"),
        DisplayLookup(field="currency_str", title="Amount"),
        DisplayLookup(field="status"),
    ]

    components = [
        c.Heading(text=invoice.name, level=2),
        c.Table(
            data=sorted(invoice.bills, key=lambda bill: bill.amount, reverse=True),
            columns=table_cols,
        ),
    ]

    if admin:
        for bill in invoice.bills:
            match bill.status:
                case "paid":
                    next_state = "reset"
                case "":
                    next_state = "paid"

            components.append(
                c.Button(
                    text=f"Set {bill.first_name} to {next_state}",
                    on_click=GoToEvent(
                        url=f"/admin/setbillstatus/{bill.id}/{next_state}"
                    ),
                )
            )

    return components


def render_all_invoices(admin: bool) -> list[AnyComponent]:
    invoices = controller.get_invoices()
    logger.debug(f"Got {len(invoices)} invoices")
    components = []
    for inv in invoices:
        components.extend(render_invoice(inv, admin))
    return components


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def landing_page() -> list[AnyComponent]:
    return [
        c.Page(components=render_all_invoices(admin=False)),
    ]


@app.get("/api/admin/console", response_model=FastUI, response_model_exclude_none=True)
def admin_console() -> list[AnyComponent]:
    metadata = controller.get_metadata()
    return [
        c.Heading(text="Admin Console", level=1),
        c.Paragraph(text=f"Data last refreshed: {metadata.last_refresh}"),
        c.Button(text="Refresh Data", on_click=GoToEvent(url="/admin/refreshdata")),
    ]


@app.get("/api/admin/invoices", response_model=FastUI, response_model_exclude_none=True)
def admin_invoices() -> list[AnyComponent]:
    return [
        c.Page(components=render_all_invoices(admin=True)),
    ]


@app.get(
    "/api/admin/refreshdata", response_model=FastUI, response_model_exclude_none=True
)
async def refresh(form: typing.Annotated[TestFormModel, fastui_form(TestFormModel)]):
    controller.update_invoices()
    metadata = controller.get_metadata()
    return [
        c.Paragraph(text=f"Refresh complete: {metadata.last_refresh}"),
        c.Button(
            text="Back to Admin Console", on_click=GoToEvent(url="/admin/console")
        ),
    ]


@app.get(
    "/api/admin/setbillstatus/{billid}/{status}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def set_bill_status(billid: int, status: str) -> list[AnyComponent]:
    player_bill = controller.get_bill(billid)
    player_bill.status = status if status != "reset" else ""
    controller.set_bill(player_bill)
    comp = [c.Paragraph(text=f"set bill billid={billid} status={status}")]
    return [c.Page(components=comp)]


@app.get("/{path:path}")
async def default_route() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="APA Invoice"))


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.DEBUG)

    # TODO None of this below works to set the log level
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["loggers"]["uvicorn"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.error"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.access"]["level"] = "DEBUG"
    log_config["disable_existing_loggers"] = "false"

    uvicorn.run(
        "webapp:app", log_config=log_config, host="0.0.0.0", port=8000, reload=True
    )
