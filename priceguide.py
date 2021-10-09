import pandas as pd
import numpy as np
from pathlib import Path

class League:
    def __init__(self):
        self.teams = 12
        self.budget = 260
        self.hitting_split = 0.7
        self.hitting_categories = ["HR", "SB", "R", "RBI", "AVG"]
        self.pitching_categories = ["W", "SV", "SO", "ERA", "WHIP"]
        self.hitting_positions = {
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
        self.pitching_positions = {"SP": 6, "RP": 3}
        self.hitting_eligibility = 20
        self.sp_eligibility = 5
        self.rp_eligibility = 5

    @property
    def num_hitters(self):
        return sum(self.hitting_positions.values()) * self.teams

    @property
    def num_pitchers(self):
        return sum(self.pitching_positions.values()) * self.teams


def calculate(lg, year, hitters, pitchers):

    lg = clean_request(lg)

    # Load extra info (id, name)
    hitters = load_extra(hitters)
    pitchers = load_extra(pitchers)
    
    # Add positions
    hitters = load_games_by_pos(hitters, lg, str(year - 1), True)
    pitchers = load_games_by_pos(pitchers, lg, str(year - 1), False)

    # Build values
    hitters, hitting_config = build_values(hitters, lg, True)
    pitchers, pitching_config = build_values(pitchers, lg, False)

    # Convert to dollar values
    hitters, hitting_config["dollar_rate"] = calc_dollar_values(hitters, lg, True)
    pitchers, pitching_config["dollar_rate"] = calc_dollar_values(pitchers, lg, False)
    
    config = {}
    config["hitting"] = hitting_config
    config["pitching"] = pitching_config

    df = pd.concat([hitters, pitchers])

    df = format_final_columns(df, lg)

    return df, config

def quick_calc(config, df, is_batting):

    if is_batting:
        lg_stats = config["hitting"]
    else:
        lg_stats = config["pitching"]

    # Calculate and combine z-scores
    for cat in lg_stats["sds"]:
        if cat in lg_stats["avg_rates"]:
            if cat == "AVG":
                df["mAVG"] = (df["H"] - (df["AB"] * lg_stats["avg_rates"]["AVG"])) / lg_stats["sds"]["AVG"]
            elif cat == "OBP":
                df["mOBP"] = ((df["H"] + df["BB"] + df["HBP"]) - (df["AB"] + df["BB"] + df["HBP"] + df["SF"]) * lg_stats["avg_rates"]["OBP"]) / lg_stats["sds"]["OBP"]
            elif cat == "SLG":
                df["mSLG"] = ((df["H"] + df["2B"] + df["3B"]*2 + df["HR"]*3) - (df["AB"] * lg_stats["avg_rates"]["SLG"])) / lg_stats["sds"]["SLG"]
            elif cat == "ERA":
                df["mERA"] = (df["ER"] - (df["IP"] * lg_stats["avg_rates"]["ERA"])) / lg_stats["sds"]["ERA"]
            elif cat == "WHIP":
                df["mWHIP"] = ((df["H"] + df["BB"]) - (df["IP"] * lg_stats["avg_rates"]["WHIP"])) / lg_stats["sds"]["WHIP"]
            elif cat == "K/9":
                df["mK/9"] = (df["SO"] - (df["IP"] * lg_stats["avg_rates"]["K/9"])) / lg_stats["sds"]["K/9"]
            elif cat == "BB/9":
                df["mBB/9"] = (df["BB"] - (df["IP"] * lg_stats["avg_rates"]["BB/9"])) / lg_stats["sds"]["BB/9"]
            elif cat == "K/BB":
                df["mK/BB"] = (df["SO"] - (df["BB"] * lg_stats["avg_rates"]["K/BB"])) / lg_stats["sds"]["K/BB"]
        else:
            df["m" + cat] = (df[cat] - lg_stats["means"][cat]) / lg_stats["sds"][cat]
    
    flip_negative_cats(df, lg_stats["sds"].keys(), is_batting)

    df["total"] = 0
    for cat in lg_stats["sds"]:
        df["total"] += df["m" + cat]

    # Adjust for position
    df["pos"].replace("DH", "Util", inplace=True)
    df["pos"].replace(["LF","CF","RF"], "OF", inplace=True)

    # We'll count a player as SP if he starts at least half of his games
    if not is_batting:
        df["pos"] = np.where((df.GS >= (df.G / 2)), "SP", "RP")

    df["repl"] = df["pos"].map(lg_stats["repl"])
    df["adj_total"] = df["total"] - df["repl"]

    # Convert to dollar value
    df["$"] = df["adj_total"] * lg_stats["dollar_rate"] + 1

    return df


def build_values(df, lg, is_batting):
    settled = False
    previous_sds = []
    previous_means = []
    previous_rep_levels = []

    if is_batting:
        cats = lg.hitting_categories
        pos = lg.hitting_positions
        num_players = lg.num_hitters
    else:
        cats = lg.pitching_categories
        pos = lg.pitching_positions
        num_players = lg.num_pitchers

    m_cats = ["m" + cat for cat in cats]

    while not settled:
        df, avg_rates = setup_stats(df, cats, num_players, is_batting)
        df, sds, means = calc_z_scores(df, cats, num_players)
        df = flip_negative_cats(df, cats, is_batting)

        df["total"] = df[m_cats].sum(axis=1)
        df.sort_values(by="total", inplace=True, ascending=False)

        df, repl = adjust_by_pos(df, pos, lg.teams)
        df.sort_values(by="adj_total", inplace=True, ascending=False)

        # Check if optimal grouping
        if sds in previous_sds:
            settled = True

        previous_sds.append(sds)
        previous_means.append(means)
        previous_rep_levels.append(repl)

    config = {}
    config["sds"] = sds
    config["means"] = means
    config["avg_rates"] = avg_rates
    config["repl"] = repl

    # Clear out excess columns
    df = cleanup_cols(df, cats, m_cats)

    return df, config

def clean_request(lg):

    # Remove any positions with a value of 0
    lg.hitting_positions = {k: v for k, v in lg.hitting_positions.items() if v}
    lg.pitching_positions = {k: v for k, v in lg.pitching_positions.items() if v}

    if "K" in lg.hitting_categories:
        lg.hitting_categories[lg.hitting_categories.index("K")] = "SO"

    if "DB" in lg.hitting_categories:
        lg.hitting_categories[lg.hitting_categories.index("DB")] = "2B"

    if "TP" in lg.hitting_categories:
        lg.hitting_categories[lg.hitting_categories.index("TP")] = "3B"

    if "K" in lg.pitching_categories:
        lg.pitching_categories[lg.pitching_categories.index("K")] = "SO"

    if "S" in lg.pitching_categories:
        lg.pitching_categories[lg.pitching_categories.index("S")] = "SV"

    if "BAA" in lg.pitching_categories:
        lg.pitching_categories[lg.pitching_categories.index("BAA")] = "AVG"

    return lg


def setup_stats(df, cats, num_players, is_batting):

    df = add_missing_cols(df, is_batting)
    df = calc_stats(df, cats)
    df, avg_rates = calc_rate_stats(df, cats, num_players)

    return df, avg_rates


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
    if "RBI+R" in cats:
        df["RBI+R"] = df["RBI"] + df["R"]
    if "SB-CS" in cats:
        df["SB-CS"] = df["SB"] - df["CS"]
    if "SV+HLD" in cats:
        df["SV+HLD"] = df["SV"] + df["HLD"]

    if "AVG" in cats and "AB" not in df.columns:
        df["AB"] = df["BFP"] - df["BB"] - df["HBP"]

    return df


def calc_rate_stats(df, cats, num_players):
    avg_player = df.head(num_players).mean()
    avg_rates = {}

    if "AVG" in cats:
        df["AVG"] = calc_rate_stat(df, ["H"], ["AB"], avg_player)
        avg_rates["AVG"] = avg_player["H"] / avg_player["AB"]

    if "OBP" in cats:
        num = ["H", "BB", "HBP"]
        den = ["AB", "BB", "HBP", "SF"]
        df["OBP"] = calc_rate_stat(df, num, den, avg_player)
        avg_rates["OBP"] = (avg_player["H"] + avg_player["BB"] + avg_player["HBP"]) / (avg_player["AB"] + avg_player["BB"] + avg_player["HBP"] + avg_player["SF"])

    if "SLG" in cats:
        df["SLG"] = calc_rate_stat(df, ["TB"], ["AB"], avg_player)
        avg_rates["SLG"] = avg_player["TB"] / avg_player["AB"]

    if "ERA" in cats:
        df["ERA"] = calc_rate_stat(df, ["ER"], ["IP"], avg_player)
        avg_rates["ERA"] = avg_player["ER"] / avg_player["IP"]

    if "WHIP" in cats:
        df["WHIP"] = calc_rate_stat(df, ["H", "BB"], ["IP"], avg_player)
        avg_rates["WHIP"] = (avg_player["H"] + avg_player["BB"]) / avg_player["IP"]

    if "K/9" in cats:
        df["K/9"] = calc_rate_stat(df, ["SO"], ["IP"], avg_player)
        avg_rates["K/9"] = avg_player["SO"] / avg_player["IP"]

    if "BB/9" in cats:
        df["BB/9"] = calc_rate_stat(df, ["BB"], ["IP"], avg_player)
        avg_rates["BB/9"] = avg_player["BB"] / avg_player["IP"]

    if "K/BB" in cats:
        df["K/BB"] = calc_rate_stat(df, ["SO"], ["BB"], avg_player)
        avg_rates["K/BB"] = avg_player["SO"] / avg_player["BB"]

    return df, avg_rates


def calc_rate_stat(df, num, den, avg):
    return df[num].sum(axis=1) - (df[den].sum(axis=1) * avg[num].sum() / avg[den].sum())


def calc_z_scores(df, cats, num_players):

    sds = {}
    means = {}
    for cat in cats:
        sd = df.head(num_players)[cat].std(ddof=0)
        mean = df.head(num_players)[cat].mean()
        df["m" + cat] = (df[cat] - mean) / sd

        sds[cat] = sd
        means[cat] = mean

    return df, sds, means


def flip_negative_cats(df, cats, is_batting):
    
    if is_batting:
        negative_cats = ["SO"]
    else:
        negative_cats = ["ERA","WHIP","AVG","BB/9","HR"]
    
    for cat in cats:
        if cat in negative_cats:
            df["m" + cat] *= -1

    return df


def adjust_by_pos(df, positions, teams):

    repl = {position: 100 for position in positions}
    df["counted"] = False
    df["adj_total"] = 0

    for position in positions:
        pos_count = positions[position] * teams

        # Only look at players who are eligible at this position
        if position == "MI":
            df_pos = df[df["pos"].str.contains("2B|SS")]
        elif position == "CI":
            df_pos = df[df["pos"].str.contains("1B|3B")]
        elif position in ["Util", "P"]:
            df_pos = df
        else:
            df_pos = df[df["pos"].str.contains(position)]

        # And only look at players that we haven't counted for other positions
        df_pos = df_pos[df_pos["counted"] == False]

        # And only players who are above replacement
        df_pos = df_pos.head(pos_count)

        df_pos["counted"] = True
        df.update(df_pos)

        # Save our replacement level for this position
        repl[position] = df_pos["total"].min()
        if position == "MI":
            repl["2B"] = repl["MI"]
            repl["SS"] = repl["MI"]
        elif position == "CI":
            repl["1B"] = repl["CI"]
            repl["3B"] = repl["CI"]
        elif position == "Util":
            for u_pos in positions:
                if u_pos not in ["CI", "MI", "Util"]:
                    if (df_pos["pos"].str.contains(u_pos)).any():
                        repl[u_pos] = repl["Util"]

    # For each position, adjust each player's total value by the
    # replacement level. Start with the smallest adjustment and get deeper.
    for position in sorted(repl, key=repl.get, reverse=True):

        if position in ["Util", "P"]:
            df["adj_total"] = df["total"] - repl[position]

        if position not in ["CI", "MI", "Util", "P"]:
            df.loc[df["pos"].str.contains(position), "adj_total"] = (
                df["total"] - repl[position]
            )

    return df, repl


def calc_dollar_values(df, lg, is_batting):
    total_money = lg.teams * lg.budget

    if is_batting:
        money = total_money * lg.hitting_split
        pos = lg.hitting_positions
        num_players = lg.num_hitters
    else:
        money = total_money * (1 - lg.hitting_split)
        pos = lg.pitching_positions
        num_players = lg.num_pitchers

    # Save $1 for a minimum bid
    money = money - (lg.teams * sum(pos.values()))

    total_points = df.head(num_players)["adj_total"].sum()

    df["$"] = (df["adj_total"] / total_points) * money + 1
    dollar_rate = 1 / total_points * money

    return df, dollar_rate


def cleanup_cols(df, cats, m_cats):

    if "AVG" in cats:
        df["AVG"] = df["H"] / df["AB"]

    if "OBP" in cats:
        df["OBP"] = (df["H"] + df["BB"] + df["HBP"]) / (df["AB"] + df["BB"] + df["HBP"] + df["SF"])

    if "SLG" in cats:
        df["SLG"] = df["TB"] / df["AB"]

    if "ERA" in cats:
        df["ERA"] = df["ER"] / df["IP"] * 9
    
    if "WHIP" in cats:
        df["WHIP"] = (df["H"] + df["BB"]) / df["IP"]

    if "K/9" in cats:
        df["K/9"] = df["SO"] / df["IP"] * 9

    if "BB/9" in cats:
        df["BB/9"] = df["BB"] / df["IP"] * 9

    if "K/BB" in cats:
        df["K/BB"] = df["SO"] / df["BB"]

    return df[["mlbam_id", "name", "pos"] + cats + m_cats + ["total", "adj_total"]]

def format_final_columns(df, lg):
    df.sort_values(by="$", ascending=False, inplace=True)

    # Round columns as needed
    for cat in lg.hitting_categories:
        if cat in ["AVG","OBP","SLG"]:
            df[cat] = df[cat].round(3)
        else:
            df[cat] = df[cat].astype("Int64")

        df["m" + cat] = df["m" + cat].round(1)
    
    for cat in lg.pitching_categories:
        if cat in ["ERA","WHIP","K/9","BB/9","K/BB"]:
            df[cat] = df[cat].round(2)
        elif cat == "AVG":
            df[cat] = df[cat].round(3)
        else:
            df[cat] = df[cat].astype("Int64")

        df["m" + cat] = df["m" + cat].round(1)
    
    df["mlbam_id"] = df["mlbam_id"].astype(int)
    df["total"] = df["total"].round(1)
    df["adj_total"] = df["adj_total"].round(1)
    df["$"] = df["$"].round(2)

    # Arrange columns a bit
    cols = ["mlbam_id","name","pos","$"]
    for cat in lg.hitting_categories:
        cols.append(cat)
    for cat in lg.pitching_categories:
        cols.append(cat)
    for cat in lg.hitting_categories:
        cols.append("m" + cat)
    for cat in lg.pitching_categories:
        cols.append("m" + cat)
    cols.append("total")
    cols.append("adj_total")

    df = df[cols]

    return df


def load_stats(system, year, lg, is_batting):

    if is_batting:
        filepath = Path(__file__).parent / "data" / (str(year) + system + "Batting.csv")
    else:
        filepath = Path(__file__).parent / "data" / (str(year) + system + "Pitching.csv")

    df = pd.read_csv(filepath)

    return df

def load_extra(df):

    if "mlbam_id" not in df.columns:
        df = load_mlbam_id(df)

    if "name" not in df.columns:
        if "name_last" in df.columns and "name_first" in df.columns:
            df["name"] = df["name_first"] + " " + df["name_last"]
        else:
            df = load_names(df)

    return df


def load_mlbam_id(df):

    register = pd.DataFrame()
    register = pd.read_csv(
        "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv",
        usecols=["key_fangraphs", "key_mlbam"],
        low_memory=False,
    ).dropna()
    register["key_fangraphs"] = register["key_fangraphs"].astype(int).astype(str)
    df = df.join(register, how="left")

    df = df.rename(columns={"key_mlbam": "mlbam_id"})
    df["mlbam_id"] = df["mlbam_id"].astype(int)
    df = df.set_index("mlbam_id")

    return df


def load_names(df):
    register = pd.DataFrame()
    register = pd.read_csv(
        "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv",
        usecols=["key_mlbam", "name_last", "name_first", "name_suffix"],
        low_memory=False,
    )

    df = df.merge(register.add_suffix("_reg"), how="left", left_on="mlbam_id", right_on="key_mlbam_reg")

    df["name"] = df["name_first_reg"] + " " + df["name_last_reg"]
    df.loc[df["name_suffix_reg"].notna(), "name"] = df["name"] + " " + df["name_suffix_reg"]

    return df

def load_games_by_pos(df, lg, year, is_batting):
    
    gbp = pd.read_csv(
        Path(__file__).parent / "games_by_pos" / (year + ".csv"), index_col="mlbam_id"
    )
    gbp = gbp.add_prefix("G_")

    gbp["gbp_pos"] = ""
    # Create boolean columns for positional eligibility
    if is_batting:
        for hit_pos in lg.hitting_positions:
            if "G_" + hit_pos in gbp.columns:
                gbp.loc[gbp["G_" + hit_pos] > lg.hitting_eligibility, "gbp_pos"] += hit_pos + "-" 
    else:
        if "G_SP" in gbp.columns:
            gbp.loc[gbp["G_SP"] > lg.sp_eligibility, "gbp_pos"] += "SP-"
        if "G_RP" in gbp.columns:
            gbp.loc[gbp["G_RP"] > lg.rp_eligibility, "gbp_pos"] += "RP-"
    gbp["gbp_pos"] = gbp["gbp_pos"].str.rstrip("-")

    df = df.merge(gbp, how="left", on="mlbam_id")
    df["gbp_pos"] = df["gbp_pos"].fillna("")
    df["pos"] = df["pos"].fillna("")

    if "pos" not in df.columns:
        df["pos"] = ""
    
    df.loc[df["gbp_pos"] != "", "pos"] = df["gbp_pos"]
    
    return df


def save_values(system, year, df):
    df.to_csv(Path(__file__).parent / "output" / (str(year) + system + "Values.csv"), index=False)
