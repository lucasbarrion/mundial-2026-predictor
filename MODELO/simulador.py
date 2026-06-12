import pandas as pd
import numpy as np
import pickle
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from bracket import GROUPS, FIXTURE_GRUPOS, ROUND_OF_32

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

df = pd.read_csv(os.path.join(BASE_DIR, "data", "equipos.csv"))
teams_dict = {row["team"]: row for _, row in df.iterrows()}

with open(os.path.join(BASE_DIR, "modelo", "modelo_mundial.pkl"), "rb") as f:
    saved = pickle.load(f)
model = saved["model"]
FEATURE_NAMES = saved["features"]

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, float(v)))

def get_features(t):
    return [t[f] for f in FEATURE_NAMES]

def model_strength(t):
    score = 0.0
    score += (125 - t["fifa_ranking"]) * 0.46
    score += t["ppg"] * 2.65
    score += t["avg_goals_scored"] * 2.0
    score -= t["avg_goals_conceded"] * 1.5
    score += t["win_pct"] * 0.028
    score += t["clean_sheet_pct"] * 0.03
    score += t["avg_shots_on_target_pg"] * 0.42
    score += t["avg_possession"] * 0.02
    score += t["world_cups_won"] * 0.35
    score += t["appearances"] * 0.03
    if t["is_host"] == 1:
        score += 0.7
    if t["is_debut"] == 1:
        score -= 4.0
    if t["appearances"] < 3:
        score -= 1.0
    if t["confederation"] in ["UEFA", "CONMEBOL"]:
        score += 0.9
    if t["confederation"] == "AFC":
        score -= 1.2
    if t["team"] == "Japan":
        score -= 1.1
    if t["team"] == "Morocco":
        score -= 1.0
    if t["confederation"] == "OFC":
        score -= 3.0
    if t["goal_diff"] > 20:
        score += 1.0
    elif t["goal_diff"] < 0:
        score -= 1.0
    return score


def calibrated_probabilities(t1, t2, raw):
    raw = np.array(raw, dtype=float)
    raw = np.maximum(raw, 0.001)
    raw = raw ** (1 / 2.35)
    raw = raw / raw.sum()

    diff_strength = model_strength(t1) - model_strength(t2)
    draw = clamp(0.25 * np.exp(-abs(diff_strength) / 9.0) + 0.07, 0.08, 0.31)
    split = 1 / (1 + np.exp(-diff_strength / 13.5))
    strength_probs = np.array([split * (1 - draw), draw, (1 - split) * (1 - draw)])

    probs = raw * 0.34 + strength_probs * 0.66

    # Hosts get atmosphere, but not an automatic model boost.
    if t1["is_host"] == 1 and t2["is_host"] != 1:
        shift = min(0.055, max(0.0, probs[0] - 0.48))
        probs[0] -= shift
        probs[1] += shift * 0.35
        probs[2] += shift * 0.65
    if t2["is_host"] == 1 and t1["is_host"] != 1:
        shift = min(0.055, max(0.0, probs[2] - 0.48))
        probs[2] -= shift
        probs[1] += shift * 0.35
        probs[0] += shift * 0.65

    # Current elite FIFA ranking should keep top teams competitive in any matchup.
    if t1["fifa_ranking"] <= 3 and t2["fifa_ranking"] > 3 and probs[0] < 0.30:
        delta = min(0.30 - probs[0], max(0.0, probs[2] - 0.18))
        probs[0] += delta
        probs[2] -= delta
    if t2["fifa_ranking"] <= 3 and t1["fifa_ranking"] > 3 and probs[2] < 0.30:
        delta = min(0.30 - probs[2], max(0.0, probs[0] - 0.18))
        probs[2] += delta
        probs[0] -= delta

    probs = np.clip(probs, 0.065, 0.76)
    return probs / probs.sum()


def ranking_floor(p1, pd_, p2, t1, t2):
    if t1["fifa_ranking"] <= 5 and t2["fifa_ranking"] > 10 and p1 < 52:
        move = min(52 - p1, max(0, p2 - 20))
        p1 += move
        p2 -= move
    if t2["fifa_ranking"] <= 5 and t1["fifa_ranking"] > 10 and p2 < 52:
        move = min(52 - p2, max(0, p1 - 20))
        p2 += move
        p1 -= move
    total = max(p1 + pd_ + p2, 0.1)
    return round(p1 / total * 100, 1), round(pd_ / total * 100, 1), round(p2 / total * 100, 1)


def predict_match(team1, team2):
    t1, t2 = teams_dict[team1], teams_dict[team2]
    diff = np.array([[a - b for a, b in zip(get_features(t1), get_features(t2))]])
    raw = model.predict_proba(diff)[0]
    cls = list(model.classes_)
    mapped = np.array([
        raw[cls.index(0)] if 0 in cls else .33,
        raw[cls.index(1)] if 1 in cls else .33,
        raw[cls.index(2)] if 2 in cls else .33,
    ])
    p1, pd_, p2 = calibrated_probabilities(t1, t2, mapped)
    g1 = round((t1["avg_goals_scored"] + t2["avg_goals_conceded"]) / 2 * (p1 + .5 * pd_) * 2, 1)
    g2 = round((t2["avg_goals_scored"] + t1["avg_goals_conceded"]) / 2 * (p2 + .5 * pd_) * 2, 1)
    return round(p1*100, 1), round(pd_*100, 1), round(p2*100, 1), g1, g2

def simular_grupos():
    standings = {g: {t: {"pts":0,"gf":0,"ga":0,"gd":0} for t in teams}
                 for g, teams in GROUPS.items()}
    resultados = []
    for grupo, t1, t2 in FIXTURE_GRUPOS:
        p1, pd_, p2, g1, g2 = predict_match(t1, t2)
        if p1 > p2 and p1 > pd_:
            pts1, pts2 = 3, 0
            gf1, gf2 = max(1, round(g1)), max(0, round(g2))
        elif p2 > p1 and p2 > pd_:
            pts1, pts2 = 0, 3
            gf1, gf2 = max(0, round(g1)), max(1, round(g2))
        else:
            pts1, pts2 = 1, 1
            gf1 = gf2 = max(0, round((g1+g2)/2))
        standings[grupo][t1]["pts"] += pts1
        standings[grupo][t1]["gf"]  += gf1
        standings[grupo][t1]["ga"]  += gf2
        standings[grupo][t1]["gd"]  += gf1 - gf2
        standings[grupo][t2]["pts"] += pts2
        standings[grupo][t2]["gf"]  += gf2
        standings[grupo][t2]["ga"]  += gf1
        standings[grupo][t2]["gd"]  += gf2 - gf1
        resultados.append({"grupo":grupo,"home":t1,"away":t2,
            "prob_home":p1,"prob_draw":pd_,"prob_away":p2,
            "goles_home":g1,"goles_away":g2})
    clasificados = {}
    terceros = []
    for grupo, table in standings.items():
        sorted_t = sorted(table.items(), key=lambda x: (x[1]["pts"],x[1]["gd"],x[1]["gf"], -teams_dict[x[0]]["fifa_ranking"]), reverse=True)
        clasificados[grupo] = sorted_t
        terceros.append((sorted_t[2][0], sorted_t[2][1], grupo))
    terceros_sorted = sorted(terceros, key=lambda x: (x[1]["pts"],x[1]["gd"],x[1]["gf"]), reverse=True)
    mejores_terceros = [t[0] for t in terceros_sorted[:8]]
    return clasificados, mejores_terceros, resultados

def get_team_by_slot(slot, clasificados, mejores_terceros, used_thirds=None):
    used_thirds = used_thirds if used_thirds is not None else set()
    pos = slot[0]
    ref = slot[1:]
    if pos == "1":
        return clasificados[ref][0][0]
    elif pos == "2":
        return clasificados[ref][1][0]
    elif pos == "3":
        for t in mejores_terceros:
            if t in used_thirds:
                continue
            for g in ref:
                if g in clasificados and clasificados[g][2][0] == t:
                    used_thirds.add(t)
                    return t
        for t in mejores_terceros:
            if t not in used_thirds:
                used_thirds.add(t)
                return t
        return mejores_terceros[0] if mejores_terceros else None
    return None

def simular_eliminatoria(clasificados, mejores_terceros):
    resultados_ko = {}
    r32 = []
    used_thirds = set()
    for slot1, slot2 in ROUND_OF_32:
        t1 = get_team_by_slot(slot1, clasificados, mejores_terceros, used_thirds)
        t2 = get_team_by_slot(slot2, clasificados, mejores_terceros, used_thirds)
        if t1 and t2:
            p1, pd_, p2, g1, g2 = predict_match(t1, t2)
            ko1 = clamp(50 + (p1 - p2) * 0.55, 25, 75)
            ko2 = 100 - ko1
            ganador = t1 if ko1 >= ko2 else t2
            r32.append(ganador)
            resultados_ko.setdefault("Round of 32", []).append(
                {"home":t1,"away":t2,"prob_home":ko1,"prob_away":ko2,"ganador":ganador})
        else:
            r32.append(t1 or "TBD")

    def play_round(teams, nombre):
        ganadores = []
        for i in range(0, len(teams), 2):
            t1, t2 = teams[i], teams[i+1]
            p1, pd_, p2, g1, g2 = predict_match(t1, t2)
            ko1 = clamp(50 + (p1 - p2) * 0.55, 25, 75)
            ko2 = 100 - ko1
            g = t1 if ko1 >= ko2 else t2
            ganadores.append(g)
            resultados_ko.setdefault(nombre, []).append(
                {"home":t1,"away":t2,"prob_home":ko1,"prob_away":ko2,"ganador":g})
        return ganadores

    r16  = play_round(r32,  "Round of 16")
    qf   = play_round(r16,  "Cuartos de Final")
    sf   = play_round(qf,   "Semifinales")
    final= play_round(sf,   "Final")
    return resultados_ko, final[0]

def simular_torneo():
    clasificados, mejores_terceros, res_grupos = simular_grupos()
    res_ko, campeon = simular_eliminatoria(clasificados, mejores_terceros)
    return {"clasificados":clasificados, "mejores_terceros":mejores_terceros,
            "resultados_grupos":res_grupos, "resultados_ko":res_ko, "campeon":campeon}

if __name__ == "__main__":
    print("🏆 Simulando Mundial 2026...\n")
    r = simular_torneo()
    for grupo, tabla in r["clasificados"].items():
        print(f"Grupo {grupo}:")
        for i, (t, s) in enumerate(tabla, 1):
            estado = "✅" if i <= 2 else "❌"
            print(f"  {estado} {i}. {t:<30} Pts:{s['pts']} GD:{s['gd']}")
    print(f"\n🌟 Mejores terceros: {r['mejores_terceros']}")
    print(f"\n🏆 CAMPEÓN: {r['campeon']}")
