from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def users_table() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Default page", level=2),
            ]
        ),
    ]


@app.get("/api/test", response_model=FastUI, response_model_exclude_none=True)
def test_table() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="test page", level=2),
            ]
        ),
    ]


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="webdemo"))
