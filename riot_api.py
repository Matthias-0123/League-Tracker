import os
import requests

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

headers = {
    "X-Riot-Token": api_key
}


# Gets the Riot account using the username and tag that were entered
def get_account(game_name, tag_line):
    account_url = (
        f"https://europe.api.riotgames.com/"
        f"riot/account/v1/accounts/by-riot-id/"
        f"{game_name}/{tag_line}"
    )

    response = requests.get(
        account_url,
        headers=headers
    )

    if response.status_code != 200:
        return None

    return response.json()


# Gets the solo queue rank and calculates the winrate of the player
def get_rank(puuid):
    rank_url = (
        f"https://euw1.api.riotgames.com/"
        f"lol/league/v4/entries/by-puuid/{puuid}"
    )

    response = requests.get(
        rank_url,
        headers=headers
    )

    rank_data = response.json()

    for queue in rank_data:
        if queue["queueType"] != "RANKED_SOLO_5x5":
            continue

        wins = queue["wins"]
        losses = queue["losses"]

        total_games = wins + losses

        if total_games == 0:
            winrate = 0
        else:
            winrate = wins / total_games * 100

        return {
            "tier": queue["tier"],
            "rank": queue["rank"],
            "lp": queue["leaguePoints"],
            "wins": wins,
            "losses": losses,
            "winrate": round(winrate, 2)
        }

    return None


# Gets the IDs of the last ten matches played by the player
def get_match_ids(puuid):
    history_url = (
        f"https://europe.api.riotgames.com/"
        f"lol/match/v5/matches/by-puuid/{puuid}/ids"
        f"?start=0&count=10"
    )

    response = requests.get(
        history_url,
        headers=headers
    )

    if response.status_code != 200:
        return []

    return response.json()


# Gets all the information from one match using the match ID
def get_match(match_id):
    match_url = (
        f"https://europe.api.riotgames.com/"
        f"lol/match/v5/matches/{match_id}"
    )

    response = requests.get(
        match_url,
        headers=headers
    )

    if response.status_code != 200:
        return None

    return response.json()