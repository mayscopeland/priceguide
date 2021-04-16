import pandas as pd
import numpy as np
import requests
import os

def main():
    build_gbp(2015)

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

    by_pos = pivot["GS"].copy(deep=True)
    by_pos["OF"] = pivot["GS"]["LF"] + pivot["GS"]["CF"] + pivot["GS"]["RF"]
    by_pos["RP"] = pivot["G"]["P"] - pivot["GS"]["P"]
    by_pos = by_pos.rename(columns={"P":"SP"})
    print(by_pos.head())
    by_pos.to_csv(os.path.dirname(__file__) + "\\games_by_pos\\" + str(year) + ".csv")

if __name__ == "__main__":
    main()
