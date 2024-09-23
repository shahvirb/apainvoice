from apainvoice import userinfo
from fastapi import Request
from fastui import AnyComponent, components as c
from fastui.events import GoToEvent
from requests_oauthlib import OAuth2Session

def default_page(
    request: Request,
    components: list[AnyComponent],
    title: str = "APA Invoice",
    oauth2session: OAuth2Session | None = None
) -> list[AnyComponent]:

    navlinks = []
    user = userinfo.get_userinfo(oauth2session, request=request) if oauth2session else None
    if user:
        navlinks.extend(
            [
                c.Link(
                    components=[c.Text(text="Admin Console")],
                    on_click=GoToEvent(url="/admin/console"),
                    active="/admin/console",
                ),
                c.Link(
                    components=[c.Text(text="Logout")],
                    on_click=GoToEvent(url="/logout"),
                    # active='startswith:/auth',
                ),
            ]
        )
    else:
        navlinks.extend(
            [
                c.Link(
                    components=[c.Text(text="Login")],
                    # HACK the url /login alone does not work  because that causes a FastUI fetch
                    # which tries to load the page contents of /login inline, but because /login causes
                    # a RedirectResponse we cannot handle an inline load. By sending the full URL
                    # we circumvent this.
                    on_click=GoToEvent(url=f"{request.base_url}login"),
                    # active='startswith:/auth',
                ),
            ]
        )

    return [
        c.PageTitle(text=f"{title}"),
        c.Navbar(title="Home", title_event=GoToEvent(url="/"), start_links=navlinks),
        c.Page(
            components=components
            # components=[
            #     *((c.Heading(text=title),) if title else ()),
            #     *components,
            # ],
        ),
        c.Footer(
            extra_text="v0.1",
            links=[
                c.Link(
                    components=[c.Text(text="Github")],
                    on_click=GoToEvent(url="https://github.com/shahvirb/apainvoice"),
                ),
            ],
        ),
    ]
