from fastapi import Request
from requests_oauthlib import OAuth2Session
from starlette.config import Config
import json

def get_userinfo(oauth: OAuth2Session, request: Request) -> dict | None:
    if oauth.authorized:
        config = Config(".env")
        url = config("AUTHENTIK_USERINFO_URL")
        response = oauth.get(url)
        assert response.ok
        userinfo = json.loads(response.content)
        return userinfo
    else:
        return None