import pandas as pd
import numpy as np
import requests
import os

def main():
    build_gbp(2020)

def build_gbp(year):
    url = "http://statsapi.mlb.com/api/v1/stats?stats=season&group=fielding&season={}&playerPool=ALL&limit=5000".format(year)
    
    records = requests.get(url).json()

    players = []

    for record in records["stats"]:
        for split in record["splits"]:
            player = {}
            player["player_id"] = split["player"]["id"]
            player["pos"] = split["position"]["abbreviation"]
            player["GS"] = split["stat"]["gamesStarted"]
            players.append(player)


    df = pd.DataFrame(players)

    pivot = df.pivot_table(index="player_id", columns="pos", values=["GS"], aggfunc=np.sum, fill_value=0)
    pivot = pivot["GS"]
    pivot["OF"] = pivot["LF"] + pivot["CF"] + pivot["RF"]
    print(pivot.head())
    pivot.to_csv(os.path.dirname(__file__) + "\\" + str(year) + ".csv")

if __name__ == "__main__":
    main()
