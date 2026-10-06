# Gets the information from all ten players that were in the match
def get_players(participants):
    players = []

    for participant in participants:
        champion = participant["championName"]

        name = participant.get("riotIdGameName")

        if not name:
            name = participant.get(
                "summonerName",
                "Unknown"
            )

        tag = participant.get(
            "riotIdTagline",
            ""
        )

        image = (
            "https://ddragon.leagueoflegends.com/"
            f"cdn/16.18.1/img/champion/{champion}.png"
        )

        player = {
            "name": name,
            "tag": tag,
            "champion": champion,
            "champion_image": image,
            "kills": participant["kills"],
            "deaths": participant["deaths"],
            "assists": participant["assists"],
            "team": participant["teamId"]
        }

        players.append(player)

    return players


def get_items(player):
    items = []

    for item_number in range(7):
        item_id = player[f"item{item_number}"]

        if item_id == 0:
            continue

        image = (
            "https://ddragon.leagueoflegends.com/"
            f"cdn/16.18.1/img/item/{item_id}.png"
        )

        items.append(image)

    return items


def get_my_player(participants, puuid):
    for participant in participants:
        if participant["puuid"] == puuid:
            return participant

    return None


# Takes the match data from Riot and prepares the information shown on the website
def make_match(match_data, puuid):
    participants = match_data["info"]["participants"]

    my_player = get_my_player(
        participants,
        puuid
    )

    if my_player is None:
        return None

    champion = my_player["championName"]

    kills = my_player["kills"]
    deaths = my_player["deaths"]
    assists = my_player["assists"]

    if deaths == 0:
        kda = kills + assists
    else:
        kda = (kills + assists) / deaths

    champion_image = (
        "https://ddragon.leagueoflegends.com/"
        f"cdn/16.18.1/img/champion/{champion}.png"
    )

    return {
        "champion": champion,
        "champion_image": champion_image,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda": round(kda, 2),
        "win": my_player["win"],
        "items": get_items(my_player),
        "players": get_players(participants)
    }