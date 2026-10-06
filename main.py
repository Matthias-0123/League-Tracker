import uvicorn

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from riot_api import get_account, get_rank, get_match_ids, get_match
from match_data import make_match


app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "player": None,
            "matches": [],
            "error": None
        }
    )


@app.post("/", response_class=HTMLResponse)
def search_player(
    request: Request,
    game_name: str = Form(...),
    tag_line: str = Form(...)
):
    matches = []

    # Gets the Riot account first because we need the puuid for the other requests
    account = get_account(game_name, tag_line)

    if account is None:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "player": None,
                "matches": [],
                "error": "Speler kon niet gevonden worden."
            }
        )

    puuid = account["puuid"]

    # Gets the ranked information that is shown above the match history
    rank = get_rank(puuid)

    player_data = None

    if rank is not None:
        player_data = {
            "name": game_name,
            "tag": tag_line,
            "tier": rank["tier"],
            "rank": rank["rank"],
            "lp": rank["lp"],
            "wins": rank["wins"],
            "losses": rank["losses"],
            "winrate": rank["winrate"]
        }

    # Gets the last ten matches and adds them to the match history
    match_ids = get_match_ids(puuid)

    for match_id in match_ids:
        match_data = get_match(match_id)

        if match_data is None:
            continue

        match = make_match(match_data, puuid)

        if match is not None:
            matches.append(match)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "player": player_data,
            "matches": matches,
            "error": None
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )