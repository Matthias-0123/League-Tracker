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
    matches = []
    error = None

    if request.method == "POST":

        game_name = request.form["game_name"]
        tag_line = request.form["tag_line"]


        # SPELER OPZOEKEN

        account_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

        response = requests.get(account_url, headers=headers)

        if response.status_code != 200:
            error = "Speler kon niet gevonden worden."
            return render_template("index.html", error=error)

        account_data = response.json()

        puuid = account_data["puuid"]


        # RANK OPHALEN

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


        # LAATSTE 10 MATCHES

        match_history_url = (
            f"https://europe.api.riotgames.com/"
            f"lol/match/v5/matches/by-puuid/{puuid}/ids"
            f"?start=0&count=10"
        )

        match_history_response = requests.get(
            match_history_url,
            headers=headers
        )

        match_ids = match_history_response.json()


        # ELKE MATCH OPHALEN

        for match_id in match_ids:

            match_url = (
                f"https://europe.api.riotgames.com/"
                f"lol/match/v5/matches/{match_id}"
            )

            match_response = requests.get(
                match_url,
                headers=headers
            )

            match_data = match_response.json()


            # SPELER IN MATCH VINDEN

            participants = match_data["info"]["participants"]

            for participant in participants:

                if participant["puuid"] == puuid:

                    champion = participant["championName"]

                    kills = participant["kills"]
                    deaths = participant["deaths"]
                    assists = participant["assists"]

                    win = participant["win"]


                    # KDA BEREKENEN

                    if deaths == 0:
                        kda = kills + assists
                    else:
                        kda = (kills + assists) / deaths


                    # CHAMPION IMAGE
                    champion_image = (
                        "https://ddragon.leagueoflegends.com/"
                        "cdn/16.18.1/img/champion/"
                        f"{champion}.png"
                    )


                    # MATCH OPSLAAN

                    match = {
                        "champion": champion,
                        "champion_image": champion_image,
                        "kills": kills,
                        "deaths": deaths,
                        "assists": assists,
                        "kda": round(kda, 2),
                        "win": win
                    }

                    matches.append(match)


    return render_template(
        "index.html",
        player=player_data,
        matches=matches,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)