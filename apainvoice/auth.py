from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt, errors
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from starlette.config import Config
import logging
import requests
import typing

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])
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


@router.get("/login")
async def login(request: Request):
    return await oauth.authentik.authorize_redirect(
        request, config("AUTHENTIK_REDIRECT_URI")
    )


@router.get("/authentik/callback")
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


@router.get("/api/loggedin", response_model=FastUI, response_model_exclude_none=True)
async def logged_in(
    request: Request,
) -> list[AnyComponent]:
    access_token = request.cookies.get("access_token")
    jwks = requests.get(config("AUTHENTIK_JWKS_URL")).json()
    claims = jwt.decode(access_token, jwks["keys"][0])
    try:
        claims.validate()
    except errors.ExpiredTokenError as e:
        logger.debug(f"JWT has expired")
        return RedirectResponse(url="/login")
    return [
        c.Paragraph(text=f"username: {claims['preferred_username']}"),
    ]
