from apainvoice import models, controller, default_page, auth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent
from fastui.forms import (
    FormFile,
    SelectSearchResponse,
    Textarea,
    fastui_form,
    SelectOptions,
)
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
import logging
import typing

from apainvoice.default_page import default_page

logger = logging.getLogger(__name__)

config = Config(".env")
app = FastAPI()
app.include_router(auth.router)
app.add_middleware(SessionMiddleware, secret_key=config("MIDDLEWARE_SECRET"))


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
                    style = "secondary"
                case "":
                    next_state = "paid"
                    style = None

            components.append(
                c.Button(
                    text=f"{bill.first_name} -> {next_state}",
                    named_style=style,
                    on_click=GoToEvent(
                        url=f"/admin/setbillstatus/{bill.id}/{next_state}"
                    ),
                )
            )

        components.append(
            c.Button(
                text=f"All players -> paid",
                named_style="warning",
                on_click=GoToEvent(url=f"/admin/setinvoicestatus/{invoice.id}/paid"),
            )
        )

    return components


def render_all_invoices(admin: bool) -> list[AnyComponent]:
    invoices = controller.sort_most_recent(controller.get_invoices())
    logger.debug(f"Got {len(invoices)} invoices")
    components = []
    for inv in invoices:
        components.extend(render_invoice(inv, admin))
    return components


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def landing_page(request: Request) -> list[AnyComponent]:
    return default_page(request, render_all_invoices(admin=False))


@app.get("/api/admin/console", response_model=FastUI, response_model_exclude_none=True)
def admin_console(request: Request) -> list[AnyComponent]:
    metadata = controller.get_metadata()
    components = [
        c.Heading(text="Admin Console", level=1),
        c.Paragraph(text=f"Data last refreshed: {metadata.last_refresh}"),
        c.Button(text="Refresh Data", on_click=GoToEvent(url="/admin/refreshdata")),
    ]
    return default_page(request, components)


@app.get("/api/admin/invoices", response_model=FastUI, response_model_exclude_none=True)
def admin_invoices(request: Request) -> list[AnyComponent]:
    components = [
        c.Page(components=render_all_invoices(admin=True)),
    ]
    return default_page(request, components)


@app.get(
    "/api/admin/refreshdata", response_model=FastUI, response_model_exclude_none=True
)
async def refresh(
    request: Request, form: typing.Annotated[TestFormModel, fastui_form(TestFormModel)]
) -> list[AnyComponent]:
    controller.update_invoices()
    metadata = controller.get_metadata()
    components = [
        c.Paragraph(text=f"Refresh complete: {metadata.last_refresh}"),
        c.Button(
            text="Back to Admin Console", on_click=GoToEvent(url="/admin/console")
        ),
    ]
    return default_page(request, components)


@app.get(
    "/api/admin/setbillstatus/{billid}/{status}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def set_bill_status(billid: int, status: str) -> list[AnyComponent]:
    player_bill = controller.get_bill(billid)
    player_bill.status = status if status != "reset" else ""
    controller.write_db(player_bill)
    return admin_invoices()


@app.get(
    "/api/admin/setinvoicestatus/{invid}/{status}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def set_bill_status(invid: int, status: str) -> list[AnyComponent]:
    invoice = controller.get_invoice(invid)
    for bill in invoice.bills:
        bill.status = status if status != "reset" else ""

    controller.write_db(invoice)
    return admin_invoices()


@app.get("/{path:path}")
async def default_route() -> HTMLResponse:
    # This needs to be defined last because it will match all paths
    return HTMLResponse(prebuilt_html(title="APA Invoice"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "webapp:app",
        log_config="log_conf.yaml",
        host="192.168.1.38",
        port=8000,
        reload=True,
    )
