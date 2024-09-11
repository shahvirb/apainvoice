from apainvoice import models, controller
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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
from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
import logging
import typing
import requests

logger = logging.getLogger(__name__)

COOKIE_EXPIRY_HRS = 24

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")
config = Config(".env")
oauth = OAuth(config)

oauth.register(
    access_token_params=None,
    access_token_url=config("AUTHENTIK_TOKEN_URL"),
    authorize_params=None,
    authorize_url=config("AUTHENTIK_AUTHORIZE_URL"),
    client_id=config("AUTHENTIK_CLIENT_ID"),
    client_kwargs={"scope": "openid profile email"},
    client_secret=config("AUTHENTIK_CLIENT_SECRET"),
    name="authentik",
    redirect_uri=config("AUTHENTIK_REDIRECT_URI"),
    server_metadata_url=config("AUTHENTIK_CONFIG_URL"),
    userinfo_endpoint=config("AUTHENTIK_USERINFO_URL"),
)
# TODO we shouldn't need to register so much given that we're providing the metadata URL https://docs.authlib.org/en/latest/client/frameworks.html#parsing-id-token

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


@app.get("/login")
async def login(request: Request):
    return await oauth.authentik.authorize_redirect(
        request, config("AUTHENTIK_REDIRECT_URI")
    )


@app.get("/authentik/callback")
async def auth_callback(
    request: Request,
):
    token = await oauth.authentik.authorize_access_token(request)

    response = RedirectResponse(url="/loggedin")
    response.set_cookie(
        key="access_token",
        value=token["access_token"],
        httponly=True,  # Prevent JavaScript from accessing this cookie
        secure=True,  # Ensure the cookie is only sent over HTTPS
        samesite="Lax",  # Lax or Strict for CSRF protection
    )
    # TODO what about the expiry of that cookie?
    return response


@app.get("/api/loggedin", response_model=FastUI, response_model_exclude_none=True)
async def logged_in(
    request: Request,
) -> list[AnyComponent]:
    access_token = request.cookies.get("access_token")
    jwks = requests.get(config("AUTHENTIK_JWKS_URL")).json()
    decoded = jwt.decode(access_token, jwks["keys"][0])
    return [
        c.Paragraph(text=f"username: {decoded['preferred_username']}"),
    ]


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
async def refresh(
    form: typing.Annotated[TestFormModel, fastui_form(TestFormModel)]
) -> list[AnyComponent]:
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
