import os
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("RIOT_API_KEY")

headers = {
    "X-Riot-Token": api_key
}


@app.route("/", methods=["GET", "POST"])
def home():

    player_data = None
    error = None

    if request.method == "POST":
        game_name = request.form["game_name"]
        tag_line = request.form["tag_line"]

        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error = "Speler kon niet gevonden worden."
            return render_template("index.html", error=error)

        data = response.json()

        puuid = data["puuid"]

        rank_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"

        rank_response = requests.get(rank_url, headers=headers)
        rank_data = rank_response.json()

        for queue in rank_data:
            if queue["queueType"] == "RANKED_SOLO_5x5":

                total_games = queue["wins"] + queue["losses"]

                winrate = queue["wins"] / total_games * 100

                player_data = {
                    "name": game_name,
                    "tag": tag_line,
                    "tier": queue["tier"],
                    "rank": queue["rank"],
                    "lp": queue["leaguePoints"],
                    "wins": queue["wins"],
                    "losses": queue["losses"],
                    "winrate": round(winrate, 2)
                }

    return render_template(
        "index.html",
        player=player_data,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)