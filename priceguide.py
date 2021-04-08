import pandas as pd
import os

year = 2021
system = "Steamer"
teams = 12
budget = 260
h_split = 0.7
h_cats = ["HR", "SB", "R", "RBI", "OBP"]
p_cats = ["W", "SV", "SO", "ERA", "WHIP"]
h_pos = {
    "C": 2,
    "SS": 1,
    "2B": 1,
    "3B": 1,
    "OF": 5,
    "1B": 1,
    "MI": 1,
    "CI": 1,
    "Util": 1,
}
p_pos = {"SP": 7, "RP": 5}
h_elig = 8
sp_elig = 5
rp_elig = 5

filepath = os.path.dirname(__file__)


def main():

    # Load file
    hitters = load_projection(system, year, h_cats, True)
    pitchers = load_projection(system, year, p_cats, False)

    # Build values
    hitters = build_values(hitters, h_cats, h_pos, h_split, True)
    pitchers = build_values(pitchers, p_cats, p_pos, 1 - h_split, False)

    # Save the results
    save_values(system, year, pd.concat([hitters, pitchers]))


def build_values(df, cats, pos, split, is_batting):
    settled = False
    previous_mean = None
    penultimate_mean = None

    num_players = sum(pos.values()) * teams

    while not settled:

        # Generate calculated stats
        df = calc_stats(df, cats, num_players, is_batting)
        
        # Calculate z-scores
        for cat in cats:
            df["m" + cat] = (df[cat] - df.head(num_players)[cat].mean()) / df.head(
                num_players
            )[cat].std(ddof=0)

        # Add z-scores as a total
        m_cats = ["m" + cat for cat in cats]
        df["total"] = df[m_cats].sum(axis=1)

        # Sort total
        df.sort_values(by="total", inplace=True, ascending=False)

        # Adjust by position
        last_player_picked = df.iloc[num_players]
        df["adj_total"] = df["total"] - last_player_picked["total"]

        # TODO: Sort by position

        # Sort by value
        df.sort_values(by="adj_total", inplace=True, ascending=False)

        # Check if optimal grouping
        mean = df.head(num_players).mean()
        if mean.equals(previous_mean) or mean.equals(penultimate_mean):
            settled = True
        else:
            penultimate_mean = previous_mean
            previous_mean = mean

    # Convert to dollar values
    total_money = teams * budget
    money = total_money * split

    # Save $1 for a minimum bid
    money = money - (teams * sum(pos.values()))

    total_points = df.head(num_players)["adj_total"].sum()

    df["$"] = (df["adj_total"] / total_points) * money + 1

    # Clear out excess columns
    df = df[["mlbam_id","Name"] + cats + m_cats + ["total","adj_total","$"]]

    return df

def calc_stats(df, cats, num_players, is_batting):

    # First, let's add any missing columns
    if is_batting and "SF" not in df:
        df["SF"] = 0
    if not is_batting and "HLD" not in df:
        df["HLD"] = 0
    if not is_batting and "QS" not in df:
        df["QS"] = 0

    # Next, anything that just needs a calculation
    if "TB" in cats or "SLG" in cats:
        df["TB"] = df["H"] + df["2B"] + (df["3B"] * 2) + (df["HR"] * 3)
    if "xBH" in cats:
        df["xBH"] = df["2B"] + df["3B"] + df["HR"]
    if "R+RBI" in cats:
        df["R+RBI"] = df["R"] + df["RBI"]
    if "SB-CS" in cats:
        df["SB-CS"] - df["SB"] - df["CS"]

    # Next, let's deal with rate stats
    avg_player = df.head(num_players).mean()

    if "AVG" in cats:
        df["AVG"] = calc_rate_stat(df, ["H"], ["AB"], avg_player)

    if "OBP" in cats:
        num = ["H","BB","HBP"]
        den = ["AB","BB","HBP","SF"]
        df["OBP"] = calc_rate_stat(df, num, den, avg_player)

    if "SLG" in cats:
        df["SLG"] = calc_rate_stat(df, ["TB"], ["AB"], avg_player)

    if "ERA" in cats:
        df["ERA"] = calc_rate_stat(df, ["ER"], ["IP"], avg_player)

    if "WHIP" in cats:
        df["WHIP"] = calc_rate_stat(df, ["H","BB"], ["IP"], avg_player)

    if "K/9" in cats:
        df["K/9"] = calc_rate_stat(df, ["SO"], ["IP"], avg_player)
        
    if "BB/9" in cats:
        df["BB/9"] = calc_rate_stat(df, ["BB"], ["IP"], avg_player)

    if "K/BB" in cats:
        df["K/BB"] = calc_rate_stat(df, ["SO"], ["BB"], avg_player)


    # Finally, any category that is negative needs the sign flipped
    if is_batting and "SO" in cats:
        df["SO"] = df["SO"] * -1
    if "ERA" in cats:
        df["ERA"] = df["ERA"] * -1
    if "WHIP" in cats:
        df["WHIP"] = df["WHIP"] * -1
    if "BB/9" in cats:
        df["WHIP"] = df["WHIP"] * -1

    return df

def calc_rate_stat(df, num, den, avg):
    return df[num].sum(axis=1) - (df[den].sum(axis=1) * avg[num].sum() / avg[den].sum())

def load_projection(system, year, cats, is_batting):

    if is_batting:
        filename = str(year) + system + "Batting.csv"
    else:
        filename = str(year) + system + "Pitching.csv"

    df = pd.read_csv(filepath + "\\" + filename)

    register = pd.read_csv(
        filepath + "\\register-master\\data\\people.csv",
        usecols=["key_fangraphs", "key_mlbam"],
    ).dropna()
    register["key_fangraphs"] = register["key_fangraphs"].astype(int).astype(str)

    df = df.merge(register, left_on="playerid", right_on="key_fangraphs")

    df = df.rename(columns={"key_mlbam": "mlbam_id"})

    pos = pd.read_csv(filepath + "\\" + str(year - 1) + ".csv")

    # Create boolean columns for positional eligibility
    for hit_pos in h_pos:
        if hit_pos in pos.columns:
            pos["is_" + hit_pos] = pos[hit_pos] > h_elig

    return df


def save_values(system, year, df):

        df.to_csv(filepath + "\\output\\" + str(year) + system + "Values.csv", index=False)


if __name__ == "__main__":
    main()
