import pandas as pd
import numpy as np
from pathlib import Path

class League:
    SCORING_ROTO = "R"
    SCORING_POINTS = "P"

    LEAGUE_STANDARD_4x4 = "4x4"
    LEAGUE_STANDARD_5x5 = "5x5"
    LEAGUE_YAHOO = "Yahoo"
    LEAGUE_CBS_ROTO = "CBS Roto"
    LEAGUE_CBS_POINTS = "CBS Points"
    LEAGUE_ESPN_ROTO = "ESPN Roto"
    LEAGUE_ESPN_POINTS = "ESPN Points"
    LEAGUE_NFBC_MAIN_EVENT = "NFBC Main Event"
    LEAGUE_NFBC_CUTLINE = "NFBC Cutline"
    LEAGUE_NFBC_BB10 = "NFBC BB10"
    LEAGUE_OTTONEU_5x5 = "Ottoneu 5x5"
    LEAGUE_OTTONEU_4x4 = "Ottoneu 4x4"
    LEAGUE_OTTONEU_FG_POINTS = "Ottoneu FG Points"
    LEAGUE_OTTONEU_SABR_POINTS = "Ottoneu SABR Points"
    LEAGUE_FANTRAX_BEST_BALL = "Fantrax Best Ball"

    def __init__(self, league_type=LEAGUE_STANDARD_5x5):

        # The defaults are for the "standard" 5x5 game (as on CBS)
        # Every other configuration uses this as the base
        self.teams = 12
        self.budget = 260
        self.hitting_split = 0.7
        self.catcher_scale = 0.75
        self.category_scales = {"SB": 1.0, "SV": 1.0}
        self.sb_scale = 1.0
        self.scoring_type = self.SCORING_ROTO
        self.hitting_categories = ["HR", "SB", "R", "RBI", "AVG"]
        self.pitching_categories = ["W", "SV", "SO", "ERA", "WHIP"]

        self.hitting_positions = {
            "C": 2,
            "2B": 1,
            "3B": 1,
            "1B": 1,
            "OF": 5,
            "SS": 1,
            "MI": 1,
            "CI": 1,
            "Util": 1,
        }
        self.pitching_positions = {"SP": 6, "RP": 3}
        self.hitting_eligibility = 20
        self.sp_eligibility = 5
        self.rp_eligibility = 5

        # 4x4
        if league_type == self.LEAGUE_STANDARD_4x4:
            self.hitting_categories = ["HR", "SB", "RBI", "AVG"]
            self.pitching_categories = ["W", "SV", "ERA", "WHIP"]

        # YAHOO
        if league_type == self.LEAGUE_YAHOO:
            self.hitting_eligibility = 10
            self.hitting_split = 0.65
            self.hitting_positions = {
                "C": 1,
                "2B": 1,
                "3B": 1,
                "1B": 1,
                "OF": 3,
                "SS": 1,
                "Util": 2,
            }
            # Officially it's SP=2, RP=2, P=4
            self.pitching_positions = {"SP": 5, "RP": 3, "P": 0}

        # CBS POINTS
        if league_type == self.LEAGUE_CBS_POINTS:
            self.hitting_positions = {
                "C": 1,
                "2B": 1,
                "3B": 1,
                "1B": 1,
                "OF": 3,
                "SS": 1,
                "Util": 1,
            }
            self.pitching_positions = {"SP": 5, "RP": 2}
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"R": 1, "RBI": 1, "TB": 1, "BB": 1, "HBP": 1, "SO": -0.5, "SB": 2, "CS": -1}
            self.pitching_points = {"IP": 3, "H": -1, "ER": -1, "BB": -1, "HBP": -1, "SO": 0.5, "W": 7, "QS": 3, "L": -5, "SV": 7}


        # ESPN
        if league_type in [self.LEAGUE_ESPN_ROTO, self.LEAGUE_ESPN_POINTS]:
            self.teams = 10
            self.hitting_positions = {
            "C": 1,
            "2B": 1,
            "3B": 1,
            "1B": 1,
            "OF": 3,
            "SS": 1,
            "Util": 1,
            }
            self.pitching_positions = {"P": 7}

        if league_type == self.LEAGUE_ESPN_POINTS:
            self.hitting_split = 0.60
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"R": 1, "RBI": 1, "TB": 1, "BB": 1, "SO": -1, "SB": 1}
            self.pitching_points = {"IP": 3, "H": -1, "ER": -2, "BB": -1, "SO": 1, "W": 2, "L": -2, "SV": 5, "HLD": 2}
        
        # NFBC
        if league_type == self.LEAGUE_NFBC_MAIN_EVENT:
            self.teams = 15

        if league_type == self.LEAGUE_NFBC_CUTLINE:
            self.teams = 10
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"AB": -1, "H": 4, "R": 2, "HR": 6, "RBI": 2, "SB": 5}
            self.pitching_points = {"IP": 3, "H": -1, "ER": -2, "BB": -1, "SO": 1, "W": 6, "SV": 8}
            self.pitching_positions = {"P": 9}

        if league_type == self.LEAGUE_NFBC_BB10:
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"AB": -1, "H": 4, "R": 2, "HR": 6, "RBI": 2, "SB": 5}
            self.pitching_points = {"IP": 3, "H": -1, "ER": -2, "BB": -1, "SO": 1, "W": 6, "SV": 8}
            self.hitting_positions = {
            "C": 1,
            "2B": 1,
            "3B": 1,
            "1B": 1,
            "SS": 1,
            "OF": 2,
            "Util": 1,
            }
            self.pitching_positions = {"P": 4}

        # OTTONEU
        if league_type in [self.LEAGUE_OTTONEU_5x5, self.LEAGUE_OTTONEU_4x4, self.LEAGUE_OTTONEU_FG_POINTS, self.LEAGUE_OTTONEU_SABR_POINTS]:
            self.budget = 400
            self.hitting_eligibility = 10
            self.hitting_positions = {
                "C": 1,
                "2B": 1,
                "OF": 5,
                "3B": 1,
                "1B": 1,
                "SS": 1,
                "MI": 1,
                "Util": 1,
            }
            self.pitching_positions = {"SP": 5, "RP": 5}

        if league_type == self.LEAGUE_OTTONEU_4x4:
            self.hitting_categories = ["OBP", "SLG", "HR", "R"]
            self.pitching_categories = ["ERA", "WHIP", "HR/9", "SO"]

        if league_type == self.LEAGUE_OTTONEU_FG_POINTS:
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"AB": -1.0, "H": 5.6, "2B": 2.9, "3B": 5.7, "HR": 9.4, "BB": 3.0, "HBP": 3.0, "SB": 1.9, "CS": -2.8}
            self.pitching_points = {"IP": 7.4, "SO": 2.0, "H": -2.6, "BB": -3.0, "HBP": -3.0, "HR": -12.3, "SV": 5.0, "HLD": 4.0}

        if league_type == self.LEAGUE_OTTONEU_SABR_POINTS:
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"AB": -1.0, "H": 5.6, "2B": 2.9, "3B": 5.7, "HR": 9.4, "BB": 3.0, "HBP": 3.0, "SB": 1.9, "CS": -2.8}
            self.pitching_points = {"IP": 5.0, "SO": 2.0, "BB": -3.0, "HBP": -3.0, "HR": -13.0, "SV": 5.0, "HLD": 4.0}
        
        # FANTRAX
        if league_type == self.LEAGUE_FANTRAX_BEST_BALL:
            self.scoring_type = self.SCORING_POINTS
            self.hitting_points = {"H": 1, "HR": 3, "RBI": 1, "R": 1, "SB": 3, "BB": 1}
            self.pitching_points = {"ER": -1.5, "IP": 1.5, "QS": 3, "SV": 6, "SO": 1.5, "W": 3, "H": -0.5, "BB": -0.5}
            self.hitting_positions = {
                "C": 1,
                "OF": 5,
                "2B": 1,
                "3B": 1,
                "1B": 1,
                "SS": 1,
                "Util": 3,
            }
            self.pitching_positions = {"P": 9}

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
    hitters = load_games_by_pos(hitters, lg, year, True)
    pitchers = load_games_by_pos(pitchers, lg, year, False)

    # Build values
    hitters, hitting_config = build_values(hitters, lg, True)
    pitchers, pitching_config = build_values(pitchers, lg, False)

    # Convert to dollar values
    hitters, hitting_config["dollar_rate"] = calc_dollar_values(hitters, lg, True)
    pitchers, pitching_config["dollar_rate"] = calc_dollar_values(pitchers, lg, False)
    
    config = {}
    config["hitting"] = hitting_config
    config["pitching"] = pitching_config

    df = pd.merge(hitters, pitchers, how="outer", suffixes=("_H", "_P"), on=["mlbam_id", "name", "pos", "$", "total", "adj_total",])

    df = format_final_columns(df, lg)

    return df, config

def quick_calc(config, df, is_batting):

    if is_batting:
        lg_stats = config["hitting"]
    else:
        lg_stats = config["pitching"]

    # If we have SDs, then this is a roto league
    if "cats" in lg_stats.keys():
        
        df = add_missing_cols(df, lg_stats["cats"], is_batting)
        # Calculate and combine z-scores
        for cat in lg_stats["cats"]:
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
                elif cat == "HR/9":
                    df["mHR/9"] = (df["HR"] - (df["IP"] * lg_stats["avg_rates"]["HR/9"])) / lg_stats["sds"]["HR/9"]
            else:
                df["m" + cat] = (df[cat] - lg_stats["means"][cat]) / lg_stats["sds"][cat]
        
        flip_negative_cats(df, lg_stats["sds"].keys(), is_batting)

        df["total"] = 0
        for cat in lg_stats["cats"]:
            df["total"] += df["m" + cat]
    
    # Points leagues
    else:
        df = add_missing_cols(df, lg_stats["pts"], is_batting)
        df["total"] = 0
        for cat, value in lg_stats["pts"].items():
            df["total"] += df[cat] * value

    # Adjust for position
    df["pos"].replace("DH", "Util", inplace=True)
    df["pos"].replace(["LF","CF","RF"], "OF", inplace=True)

    # We'll count a player as SP if he starts at least half of his games
    if not is_batting:
        if "SP" in lg_stats["repl"]:
            df["pos"] = np.where((df.GS >= (df.G / 2)), "SP", "RP")

    df["repl"] = df["pos"].map(lg_stats["repl"])
    df["adj_total"] = df["total"] - df["repl"]

    if "cats" in lg_stats.keys():
        df = calculate_rate_stats(df, lg_stats["cats"])
        for cat in lg_stats["cats"]:
            df = round_column(df, cat, cat)

    # Convert to dollar value
    df["$"] = df["adj_total"] * lg_stats["dollar_rate"] + 1

    return df


def build_values(df, lg, is_batting):
    settled = False
    previous_sds = []
    previous_means = []
    previous_rep_levels = []

    if is_batting:
        if lg.scoring_type == lg.SCORING_ROTO:
            cats = lg.hitting_categories
        else:
            pts = lg.hitting_points
        pos = lg.hitting_positions
        num_players = lg.num_hitters
    else:
        if lg.scoring_type == lg.SCORING_ROTO:
            cats = lg.pitching_categories
        else:
            pts = lg.pitching_points
        pos = lg.pitching_positions
        num_players = lg.num_pitchers

    if lg.scoring_type == lg.SCORING_ROTO:
        m_cats = ["m" + cat for cat in cats]

        while not settled:
            df, avg_rates = setup_stats(df, cats, num_players, is_batting)
            df, sds, means = calc_z_scores(df, cats, num_players)
            df = flip_negative_cats(df, cats, is_batting)

            df = scale_categories(df, cats, lg.category_scales)
            df["total"] = df[m_cats].sum(axis=1)

            df.sort_values(by="total", inplace=True, ascending=False)

            df, repl = adjust_by_pos(df, pos, lg.teams)
            df = scale_catchers(df, lg.catcher_scale)
            df.sort_values(by="adj_total", inplace=True, ascending=False)

            # Check if optimal grouping
            if sds in previous_sds:
                settled = True

            previous_sds.append(sds)
            previous_means.append(means)
            previous_rep_levels.append(repl)

        config = {}
        config["cats"] = cats
        config["sds"] = sds
        config["means"] = means
        config["avg_rates"] = avg_rates
        config["repl"] = repl

        # Clear out excess columns
        df = cleanup_cols(df, cats, m_cats, is_batting)
    else:
        df = add_missing_cols(df, pts, is_batting)
        df["total"] = 0.0
        for cat, value in pts.items():
            df["total"] += df[cat] * value

        df.sort_values(by="total", inplace=True, ascending=False)

        df, repl = adjust_by_pos(df, pos, lg.teams)
        df = scale_catchers(df, lg.catcher_scale)
        df.sort_values(by="adj_total", inplace=True, ascending=False)
        config = {}
        config["pts"] = pts
        config["repl"] = repl

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

    df = add_missing_cols(df, cats, is_batting)
    df, avg_rates = calc_rate_stats(df, cats, num_players)

    return df, avg_rates


def add_missing_cols(df, cats, is_batting):

    if "HBP" not in df:
        df["HBP"] = 0
    if "SF" not in df:
        df["SF"] = 0
    if "HLD" in cats and not "HLD" in df:
        df["HLD"] = 0
    if "SV+HLD" in cats and not "HLD" in df:
        df["HLD"] = 0
    if "SV+HLD/2" in cats and not "HLD" in df:
        df["HLD"] = 0
    if "QS" in cats and not "QS" in df:
        df["QS"] = 0
    if "W+QS" in cats and not "QS" in df:
        df["QS"] = 0
    if "W+QS-L" in cats and not "QS" in df:
        df["QS"] = 0
    if not is_batting and not "R" in df:
        df["R"] = df["ER"]

    if is_batting:
        df["PA"] = df["AB"] + df["BB"] + df["HBP"] + df["SF"]

    if "TB" in cats or "SLG" in cats:
        df["TB"] = df["H"] + df["2B"] + (df["3B"] * 2) + (df["HR"] * 3)
    if "1B" in cats:
        df["1B"] = df["H"] - df["2B"] - df["3B"] - df["HR"]
    if "xBH" in cats:
        df["xBH"] = df["2B"] + df["3B"] + df["HR"]
    if "RBI+R" in cats:
        df["RBI+R"] = df["RBI"] + df["R"]
    if "SB-CS" in cats:
        df["SB-CS"] = df["SB"] - df["CS"]
    if "W-L" in cats:
        df["W-L"] = df["W"] - df["L"]
    if "W+QS" in cats:
        df["W+QS"] = df["W"] + df["QS"]
    if "W+QS-L" in cats:
        df["W+QS-L"] = df["W"] + df["QS"] - df["L"]
    if "SV+HLD" in cats:
        df["SV+HLD"] = df["SV"] + df["HLD"]
    if "SV+HLD/2" in cats:
        df["SV+HLD/2"] = df["SV"] + df["HLD"] / 2

    if not is_batting and "AVG" in cats:
        df["AB"] = df["IP"] * 3 - df["BB"] - df["HBP"] - df["SF"]

    return df

def calc_rate_stats(df, cats, num_players):
    avg_player = df.head(num_players).mean(numeric_only=True)
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

    if "HR/9" in cats:
        df["HR/9"] = calc_rate_stat(df, ["HR"], ["IP"], avg_player)
        avg_rates["HR/9"] = avg_player["HR"] / avg_player["IP"]

    return df, avg_rates


def calc_rate_stat(df, num, den, avg):
    return df[num].sum(axis=1) - (df[den].sum(axis=1) * avg[num].sum() / avg[den].sum())


def calc_z_scores(df, cats, num_players):

    sds = {}
    means = {}
    for cat in cats:
        sd = df.head(num_players)[cat].std(ddof=0)
        mean = df.head(num_players)[cat].mean()
        if sd == 0:
            df["m" + cat] = 0
        else:
            df["m" + cat] = (df[cat] - mean) / sd

        sds[cat] = sd
        means[cat] = mean

    return df, sds, means


def flip_negative_cats(df, cats, is_batting):
    
    if is_batting:
        negative_cats = ["SO"]
    else:
        negative_cats = ["ERA","WHIP","AVG","BB/9","HR/9","HR","L"]
    
    for cat in cats:
        if cat in negative_cats:
            df["m" + cat] *= -1

    return df

def scale_categories(df, cats, cat_scales):

    for cat, scale in cat_scales.items():
        if cat in cats:
            if cat in df:
                df["m" + cat] = df["m" + cat] * scale

    return df


def adjust_by_pos(df, positions, teams):

    repl = {position: 100 for position in positions}
    df["counted"] = False
    df["adj_total"] = -100

    # For this process, we'll count P as SP if this league doesn't use P
    df["actual_pos"] = df["pos"]
    if "SP" in positions and "P" not in positions:
        df.loc[df["pos"] == "", "pos"] = "SP"

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

    df["pos"] = df["actual_pos"]
    return df, repl

def scale_catchers(df, catcher_scale):

    df.loc[df["pos"].str.contains("C"), "adj_total"] = df["adj_total"] * catcher_scale

    return df


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


def cleanup_cols(df, cats, m_cats, is_batting):

    df = calculate_rate_stats(df, cats)

    if is_batting:
        appearances = "PA"
    else:
        appearances = "IP"

    if appearances in cats:
        return df[["mlbam_id", "name", "pos"] + cats + m_cats + ["total", "adj_total"]]
    else:
        return df[["mlbam_id", "name", "pos", appearances] + cats + m_cats + ["total", "adj_total"]]


def calculate_rate_stats(df, cats):
    if "AVG" in cats and "AB" in df:
        df["AVG"] = df["H"] / df["AB"]

    if "AVG" in cats and "BFP" in df:
        df["AVG"] = df["H"] / df["BFP"]

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

    if "HR/9" in cats:
        df["HR/9"] = df["HR"] / df["IP"] * 9

    return df

def format_final_columns(df, lg):
    df.sort_values(by="$", ascending=False, inplace=True)

    # Round columns as needed
    if lg.scoring_type == League.SCORING_ROTO:

        for cat in lg.hitting_categories:
            col_name = get_col_name(df, cat, True)
            df = round_column(df, cat, col_name)
            df["m" + col_name] = df["m" + col_name].round(1)
        
        if "PA" not in lg.hitting_categories:
            df = round_column(df, "PA", "PA")

        for cat in lg.pitching_categories:
            col_name = get_col_name(df, cat, False)
            df = round_column(df, cat, col_name)
            df["m" + col_name] = df["m" + col_name].round(1)

        if "IP" not in lg.pitching_categories:
            df = round_column(df, "IP", "IP")

    else:
        for pts in lg.hitting_points:
            col_name = get_col_name(df, pts, True)
            df[col_name] = np.floor(pd.to_numeric(df[col_name], errors="coerce")).astype("Int64")
        if "PA" not in lg.hitting_points:
            df = round_column(df, "PA", "PA")

        for pts in lg.pitching_points:
            col_name = get_col_name(df, pts, False)
            df[col_name] = np.floor(pd.to_numeric(df[col_name], errors="coerce")).astype("Int64")
        if "IP" not in lg.pitching_points:
            df = round_column(df, "IP", "IP")

    df["mlbam_id"].fillna(0, inplace=True)
    df["mlbam_id"] = df["mlbam_id"].astype(int)
    df["total"] = df["total"].round(1)
    df["adj_total"] = df["adj_total"].round(1)
    df["$"] = df["$"].round(2)

    # Arrange columns a bit
    cols = ["mlbam_id","name","pos","$"]
    if lg.scoring_type == League.SCORING_ROTO:
        if "PA" not in lg.hitting_categories:
            cols.append("PA")
        for cat in lg.hitting_categories:
            cols.append(get_col_name(df, cat, True))

        if "IP" not in lg.pitching_categories:
            cols.append("IP")
        for cat in lg.pitching_categories:
            cols.append(get_col_name(df, cat, False))

        for cat in lg.hitting_categories:
            cols.append("m" + get_col_name(df, cat, True))
        for cat in lg.pitching_categories:
            cols.append("m" + get_col_name(df, cat, False))
    else:
        if "PA" not in lg.hitting_points:
            cols.append("PA")
        for pts in lg.hitting_points:
            cols.append(get_col_name(df, pts, True))

        if "IP" not in lg.pitching_points:
            cols.append("IP")
        for pts in lg.pitching_points:
            cols.append(get_col_name(df, pts, False))

    cols.append("total")
    cols.append("adj_total")

    df = df[cols]

    return df

def round_column(df, cat, col_name):

    if cat in ["AVG","OBP","SLG"]:
        df[col_name] = df[col_name].round(3)
    elif cat in ["ERA","WHIP","K/9","BB/9","HR/9","K/BB"]:
        df[col_name] = df[col_name].round(2)
    elif cat in ["IP","SV+HLD/2"]:
        df[col_name] = df[col_name].round(1)
    else:
        df[col_name] = df[col_name].astype("Int64")

    return df

# Any duplicate column names were given a suffix when we merged hitters and pitchers
def get_col_name(df, cat, is_batting):

    if cat in df.columns:
        return cat
    elif is_batting and cat + "_H" in df.columns:
        return cat + "_H"
    elif not is_batting and cat + "_P" in df.columns:
        return cat + "_P"
    else:
        return None


def load_stats(system, year, lg, is_batting):

    if is_batting:
        filepath = Path(__file__).parent / "data" / (str(year) + system + "Batting.csv")
    else:
        filepath = Path(__file__).parent / "data" / (str(year) + system + "Pitching.csv")

    df = pd.read_csv(filepath)

    return df

def load_extra(df):

    if "name" not in df.columns:
        if "name_last" in df.columns and "name_first" in df.columns:
            df["name"] = df["name_first"] + " " + df["name_last"]
        else:
            df = load_names(df)

    return df

def load_names(df):
    filepath = Path(__file__).parent.parent
    register = pd.DataFrame()
    register = pd.read_csv(
        filepath / "SFBB Player ID Map - PLAYERIDMAP.csv",
        usecols=["MLBID", "MLBNAME"],
    )

    df = df.merge(register, how="left", left_on="mlbam_id", right_on="MLBID")

    df.rename(columns={"MLBNAME": "name"}, inplace=True)
    df.drop(["MLBID"], axis="columns", inplace=True)

    return df

def load_games_by_pos(df, lg, year, is_batting):
    
    if "pos" not in df:
        df["pos"] = ""

    gbp = pd.read_csv(Path(__file__).parent / "games_by_pos" / (str(year - 1) + ".csv"), index_col="mlbam_id")
    gbp = gbp.add_prefix("G_")

    cur_year_csv = Path(__file__).parent / "games_by_pos" / (str(year) + ".csv")
    if cur_year_csv.is_file():
        current_gbp = pd.read_csv(cur_year_csv, index_col="mlbam_id")
        current_gbp = current_gbp.add_prefix("GC_")
        gbp = gbp.join(current_gbp, how="outer")
        gbp = gbp.fillna(0)

    gbp["gbp_pos"] = ""

    if is_batting:
        for hit_pos in lg.hitting_positions:
            if "G_" + hit_pos in gbp.columns and "GC_" + hit_pos in gbp.columns:
                gbp.loc[(gbp["G_" + hit_pos] >= lg.hitting_eligibility) | (gbp["GC_" + hit_pos] >= lg.hitting_eligibility), "gbp_pos"] += hit_pos + "-"
            elif "G_" + hit_pos in gbp.columns:
                gbp.loc[gbp["G_" + hit_pos] >= lg.hitting_eligibility, "gbp_pos"] += hit_pos + "-"
    else:
        if "G_SP" in gbp.columns and "GC_SP" in gbp.columns:
            gbp.loc[(gbp["G_SP"] >= lg.sp_eligibility) | (gbp["GC_SP"] >= lg.sp_eligibility), "gbp_pos"] += "SP-"
        elif "G_SP" in gbp.columns:
            gbp.loc[gbp["G_SP"] >= lg.sp_eligibility, "gbp_pos"] += "SP-"
        if "G_RP" in gbp.columns and "GC_RP" in gbp.columns:
            gbp.loc[(gbp["G_RP"] >= lg.rp_eligibility) | (gbp["GC_RP"] >= lg.rp_eligibility), "gbp_pos"] += "RP-"
        elif "G_RP" in gbp.columns:
            gbp.loc[gbp["G_RP"] >= lg.rp_eligibility, "gbp_pos"] += "RP-"
    gbp["gbp_pos"] = gbp["gbp_pos"].str.rstrip("-")

    df = df.merge(gbp, how="left", on="mlbam_id")
    df["gbp_pos"] = df["gbp_pos"].fillna("")
    df["pos"] = df["pos"].fillna("")

    df.loc[df["gbp_pos"] != "", "pos"] = df["gbp_pos"]

    return df


def save_values(system, year, df):
    df.to_csv(Path(__file__).parent / "output" / (str(year) + system + "Values.csv"), index=False)
