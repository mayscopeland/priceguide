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
    hitters = load_projection(system, year, True)
    pitchers = load_projection(system, year, False)

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
    m_cats = ["m" + cat for cat in cats]

    while not settled:
        df = setup_stats(df, cats, num_players, is_batting)
        df = calc_values(df, cats, m_cats, num_players)

        # Check if optimal grouping
        mean = df.head(num_players).mean()
        if mean.equals(previous_mean) or mean.equals(penultimate_mean):
            settled = True
        else:
            penultimate_mean = previous_mean
            previous_mean = mean

    # Convert to dollar values
    df = calc_dollar_values(df, pos, split, num_players)

    # Clear out excess columns
    df = remove_extra_cols(df, cats, m_cats)

    return df


def setup_stats(df, cats, num_players, is_batting):

    df = add_missing_cols(df, is_batting)
    df = calc_stats(df, cats)
    df = calc_rate_stats(df, cats, num_players)
    df = flip_neg_cats(df, cats, is_batting)

    return df


def add_missing_cols(df, is_batting):

    if is_batting and "SF" not in df:
        df["SF"] = 0
    if not is_batting and "HLD" not in df:
        df["HLD"] = 0
    if not is_batting and "QS" not in df:
        df["QS"] = 0

    return df


def calc_stats(df, cats):
    if "TB" in cats or "SLG" in cats:
        df["TB"] = df["H"] + df["2B"] + (df["3B"] * 2) + (df["HR"] * 3)
    if "xBH" in cats:
        df["xBH"] = df["2B"] + df["3B"] + df["HR"]
    if "R+RBI" in cats:
        df["R+RBI"] = df["R"] + df["RBI"]
    if "SB-CS" in cats:
        df["SB-CS"] - df["SB"] - df["CS"]

    return df


def calc_rate_stats(df, cats, num_players):
    avg_player = df.head(num_players).mean()

    if "AVG" in cats:
        df["AVG"] = calc_rate_stat(df, ["H"], ["AB"], avg_player)

    if "OBP" in cats:
        num = ["H", "BB", "HBP"]
        den = ["AB", "BB", "HBP", "SF"]
        df["OBP"] = calc_rate_stat(df, num, den, avg_player)

    if "SLG" in cats:
        df["SLG"] = calc_rate_stat(df, ["TB"], ["AB"], avg_player)

    if "ERA" in cats:
        df["ERA"] = calc_rate_stat(df, ["ER"], ["IP"], avg_player)

    if "WHIP" in cats:
        df["WHIP"] = calc_rate_stat(df, ["H", "BB"], ["IP"], avg_player)

    if "K/9" in cats:
        df["K/9"] = calc_rate_stat(df, ["SO"], ["IP"], avg_player)

    if "BB/9" in cats:
        df["BB/9"] = calc_rate_stat(df, ["BB"], ["IP"], avg_player)

    if "K/BB" in cats:
        df["K/BB"] = calc_rate_stat(df, ["SO"], ["BB"], avg_player)

    return df


def calc_rate_stat(df, num, den, avg):
    return df[num].sum(axis=1) - (df[den].sum(axis=1) * avg[num].sum() / avg[den].sum())


def flip_neg_cats(df, cats, is_batting):
    neg_cats = ["ERA", "WHIP", "BB/9"]

    for cat in neg_cats:
        if cat in cats:
            df[cat] = df[cat] * -1

    # Strikeouts are negative for batters but not pitchers
    if is_batting and "SO" in cats:
        df["SO"] = df["SO"] * -1

    return df


def calc_values(df, cats, m_cats, num_players):

    df = calc_z_scores(df, cats, num_players)

    df["total"] = df[m_cats].sum(axis=1)

    df.sort_values(by="total", inplace=True, ascending=False)

    df = adjust_by_pos(df, num_players)

    df.sort_values(by="adj_total", inplace=True, ascending=False)

    return df


def calc_z_scores(df, cats, num_players):
    for cat in cats:
        df["m" + cat] = (df[cat] - df.head(num_players)[cat].mean()) / df.head(
            num_players
        )[cat].std(ddof=0)

    return df


# TODO: add positional adjustment
def adjust_by_pos(df, num_players):
    last_player_picked = df.iloc[num_players]
    df["adj_total"] = df["total"] - last_player_picked["total"]

    return df


def calc_dollar_values(df, pos, split, num_players):
    total_money = teams * budget
    money = total_money * split

    # Save $1 for a minimum bid
    money = money - (teams * sum(pos.values()))

    total_points = df.head(num_players)["adj_total"].sum()

    df["$"] = (df["adj_total"] / total_points) * money + 1

    return df


def remove_extra_cols(df, cats, m_cats):
    return df[["mlbam_id", "Name"] + cats + m_cats + ["total", "adj_total", "$"]]


def load_projection(system, year, is_batting):

    if is_batting:
        filename = str(year) + system + "Batting.csv"
    else:
        filename = str(year) + system + "Pitching.csv"

    df = pd.read_csv(filepath + "\\" + filename)

    df = load_mlbam_id(df)
    df = load_games_by_pos(df)

    return df


def load_mlbam_id(df):
    register = pd.read_csv(
        filepath + "\\register-master\\data\\people.csv",
        usecols=["key_fangraphs", "key_mlbam"],
    ).dropna()
    register["key_fangraphs"] = register["key_fangraphs"].astype(int).astype(str)

    df = df.merge(register, left_on="playerid", right_on="key_fangraphs")

    df = df.rename(columns={"key_mlbam": "mlbam_id"})

    return df


def load_games_by_pos(df):
    pos = pd.read_csv(filepath + "\\games_by_pos\\" + str(year - 1) + ".csv")

    # Create boolean columns for positional eligibility
    for hit_pos in h_pos:
        if hit_pos in pos.columns:
            pos["is_" + hit_pos] = pos[hit_pos] > h_elig

    return df


def save_values(system, year, df):
    df.to_csv(filepath + "\\output\\" + str(year) + system + "Values.csv", index=False)


if __name__ == "__main__":
    main()
