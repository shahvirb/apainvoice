from apainvoice import default_page, userinfo
from fastapi import APIRouter, Request, Query
from fastui.events import GoToEvent
from fastapi.responses import RedirectResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from starlette.config import Config
import logging
import requests
from requests_oauthlib import OAuth2Session
import json
import typing

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])
config = Config(".env")

OAUTH_CLIENT_ID = config("AUTHENTIK_CLIENT_ID")
OAUTH_CLIENT_SECRET = config("AUTHENTIK_CLIENT_SECRET")
OAUTH_URL_AUTHORIZE = config("AUTHENTIK_AUTHORIZE_URL")
OAUTH_URL_JWKS = config("AUTHENTIK_JWKS_URL")
OAUTH_URL_REDIRECT = config("AUTHENTIK_REDIRECT_URL")
OAUTH_URL_REVOKE = config("AUTHENTIK_REVOKE_URL")
OAUTH_URL_TOKEN = config("AUTHENTIK_TOKEN_URL")
OAUTH_URL_USERINFO = config("AUTHENTIK_USERINFO_URL")
OAUTH_SCOPE = "openid profile email"


oauth = OAuth2Session(
    OAUTH_CLIENT_ID, redirect_uri=OAUTH_URL_REDIRECT, scope=OAUTH_SCOPE
)


def revoke_access_token(access_token):
    revocation_endpoint = config("AUTHENTIK_REVOCATION_URL")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "token": access_token,
        "token_type_hint": "access_token",  # or 'refresh_token' if you're revoking a refresh token
    }

    response = requests.post(revocation_endpoint, headers=headers, data=data)

    if response.status_code == 200:
        print("Token revoked successfully.")
    else:
        print(f"Failed to revoke token: {response.status_code} {response.text}")


@router.get("/login")
async def login(
    request: Request,
    next: str = Query(default="/loggedin", description="Return path after login"),
):
    logger.debug(f"Logging in. next={next}")
    if oauth.authorized:
        logger.warning("Already authorized user is trying to login again")
        return RedirectResponse(url=next)
    else:
        authorization_url, state = oauth.authorization_url(OAUTH_URL_AUTHORIZE)
        logger.debug(f"authorization_url={authorization_url}, state={state}")
        request.session["oauth_state"] = state
        return RedirectResponse(url=f"{authorization_url}?next={next}")
        # return RedirectResponse(url="https://www.google.com")


@router.get("/api/logout")
async def logout(
    request: Request,
):
    raise NotImplementedError


@router.get("/auth/callback")
async def auth_callback(
    request: Request,
    code: str = Query(),
    next: str = Query(default="/loggedin", description="Return path after login"),
):
    logger.debug(f"auth callback. code={code}, next={next}")
    token = oauth.fetch_token(
        OAUTH_URL_TOKEN,
        authorization_response=str(request.url),
        client_secret=OAUTH_CLIENT_SECRET,
        code=code,
    )
    assert token
    logger.debug(f"token={token}")
    response = RedirectResponse(url=next)
    # TODO why do we need to set this cookie?
    # response.set_cookie(
    #     key="access_token",
    #     value=token["access_token"],
    #     httponly=True,
    #     secure=True,
    #     samesite="Lax",
    # )
    return response


def get_userinfo(request: Request) -> dict | None:
    if oauth.authorized:
        response = oauth.get(OAUTH_URL_USERINFO)
        assert response.ok
        userinfo = json.loads(response.content)
        return userinfo
    else:
        return None


@router.get("/api/loggedin", response_model=FastUI, response_model_exclude_none=True)
# @router.get("/api/loggedin")
async def logged_in(
    request: Request,
) -> list[AnyComponent]:
    user = userinfo.get_userinfo(oauth, request=request)

    components = None
    if user:
        components = [
            c.Paragraph(text=f"username: {user['preferred_username']}"),
        ]
    else:
        components = [
            c.Paragraph(text="ERROR - You are not logged in"),
        ]
        # return RedirectResponse(url=f"{request.base_url}login?next=/loggedin")
        # return RedirectResponse(url="https://www.google.com")
    return default_page.default_page(request, components, oauth2session=oauth)