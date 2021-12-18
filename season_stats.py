import pandas as pd
import numpy as np
import requests
import os

def main():
    build_all(2021)

def build_all(year):

    build_batting(year)
    build_pitching(year)
    build_gbp(year)

def build_batting(year):
    url = "http://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season={}&playerPool=ALL&limit=5000".format(year)
    
    records = requests.get(url).json()

    players = []

    for record in records["stats"]:
        for split in record["splits"]:
            player = {}
            player["mlbam_id"] = split["player"]["id"]
            player["AB"] = split["stat"]["atBats"]
            player["R"] = split["stat"]["runs"]
            player["H"] = split["stat"]["hits"]
            player["2B"] = split["stat"]["doubles"]
            player["3B"] = split["stat"]["triples"]
            player["HR"] = split["stat"]["homeRuns"]
            player["RBI"] = split["stat"]["rbi"]
            player["SB"] = split["stat"]["stolenBases"]
            player["CS"] = split["stat"]["caughtStealing"]
            player["BB"] = split["stat"]["baseOnBalls"]
            player["SO"] = split["stat"]["strikeOuts"]
            player["HBP"] = split["stat"]["hitByPitch"]
            player["SH"] = split["stat"]["sacBunts"]
            player["SF"] = split["stat"]["sacFlies"]
            players.append(player)


    df = pd.DataFrame(players)

    print(df.head())
    df.to_csv(os.path.dirname(__file__) + "\\data\\" + str(year) + "Batting.csv", index=False)

def build_pitching(year):
    url = "http://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&season={}&playerPool=ALL&limit=5000".format(year)
    
    records = requests.get(url).json()

    players = []

    for record in records["stats"]:
        for split in record["splits"]:
            player = {}
            player["mlbam_id"] = split["player"]["id"]
            player["W"] = split["stat"]["wins"]
            player["L"] = split["stat"]["losses"]
            player["CG"] = split["stat"]["completeGames"]
            player["SHO"] = split["stat"]["shutouts"]
            player["SV"] = split["stat"]["saves"]
            player["BS"] = split["stat"]["blownSaves"]
            player["HLD"] = split["stat"]["holds"]
            player["IP"] = split["stat"]["inningsPitched"]
            player["H"] = split["stat"]["hits"]
            player["R"] = split["stat"]["runs"]
            player["ER"] = split["stat"]["earnedRuns"]
            player["HR"] = split["stat"]["homeRuns"]
            player["BB"] = split["stat"]["baseOnBalls"]
            player["IBB"] = split["stat"]["intentionalWalks"]
            player["SO"] = split["stat"]["strikeOuts"]
            player["HBP"] = split["stat"]["hitBatsmen"]
            player["BK"] = split["stat"]["balks"]
            player["WP"] = split["stat"]["wildPitches"]
            players.append(player)


    df = pd.DataFrame(players)

    print(df.head())
    df.to_csv(os.path.dirname(__file__) + "\\data\\" + str(year) + "Pitching.csv", index=False)


def build_gbp(year):
    url = "http://statsapi.mlb.com/api/v1/stats?stats=season&group=fielding&season={}&playerPool=ALL&limit=5000".format(year)
    
    records = requests.get(url).json()

    players = []

    for record in records["stats"]:
        for split in record["splits"]:
            player = {}
            player["mlbam_id"] = split["player"]["id"]
            player["pos"] = split["position"]["abbreviation"]
            player["G"] = split["stat"]["games"]
            player["GS"] = split["stat"]["gamesStarted"]
            players.append(player)


    df = pd.DataFrame(players)

    pivot = df.pivot_table(index="mlbam_id", columns="pos", values=["GS", "G"], aggfunc=np.sum, fill_value=0)

    by_pos = pivot["G"].copy(deep=True)

    # This will overcount OF appearances if someone played multiple OF positions in a game
    by_pos["OF"] = pivot["G"]["LF"] + pivot["G"]["CF"] + pivot["G"]["RF"]
    by_pos["RP"] = pivot["G"]["P"] - pivot["GS"]["P"]
    by_pos = by_pos.rename(columns={"P":"SP"})
    print(by_pos.head())
    by_pos.to_csv(os.path.dirname(__file__) + "\\games_by_pos\\" + str(year) + ".csv")


if __name__ == "__main__":
    main()
