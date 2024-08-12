from apainvoice import pydmodels, ppapi, invoice
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayLookup

app = FastAPI()


# # define some users
# bills = [
#     pydmodels.PlayerBill(id=1, name="John", amount=8),
#     pydmodels.PlayerBill(id=2, name="Jack", amount=16),
# ]


def generate_bills() -> list[AnyComponent]:
    api = ppapi.PersistentDataAPI()
    bills = invoice.calculate_bills(api, [42940044])
    
    return [
        c.Heading(text="8-13-24", level=2),
        c.Table(
            data=bills,
            columns=[
                DisplayLookup(field="name"),
                DisplayLookup(field="amount"),
            ],
        ),
    ]


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
