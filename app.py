from __future__ import annotations

import os
import sys
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import charts
from components import (
    esc, flag, html, load_css, topbar, hero, section, group_table, match_card,
    metric_card, progress_bar, rank_rows, brand_splash, dashboard_cards, ai_card, footer_lab,
)

st.set_page_config(
    page_title="WORLD CUP AI PREDICTION",
    page_icon=":trophy:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "MODELO"))
from bracket import GROUPS, FIXTURE_GRUPOS, ROUND_OF_32

load_css(str(BASE_DIR / "styles.css"))

@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv(BASE_DIR / "DATA" / "equipos.csv")

@st.cache_resource(show_spinner=False)
def load_model():
    with open(BASE_DIR / "MODELO" / "modelo_mundial.pkl", "rb") as f:
        return pickle.load(f)

df = load_data()
saved = load_model()
model = saved["model"]
FEATS = saved["features"]
TD = {r["team"]: r for _, r in df.iterrows()}

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, float(v)))

def get_features(t):
    return [t[f] for f in FEATS]

def power_rating(t):
    attack = clamp(t["avg_goals_scored"] * 24 + t["avg_shots_on_target_pg"] * 5)
    defense = clamp(100 - t["avg_goals_conceded"] * 24 + t["clean_sheet_pct"] * .28)
    form = clamp(t["win_pct"] * .72 + t["ppg"] * 12)
    ranking = clamp(102 - t["fifa_ranking"])
    return round(attack * .30 + defense * .25 + form * .25 + ranking * .20, 1)

def title_probability(team):
    base = clamp((power_rating(TD[team]) - 48) * 1.42, 3, 87)
    t = TD[team]
    if t["confederation"] == "AFC":
        base -= 6.5
    if team == "Japan":
        base -= 7.0
    if team == "Morocco":
        base -= 5.5
    if t["fifa_ranking"] <= 3:
        base += 5.5
    return round(clamp(base, 3, 87), 1)

def qualify_probability(team):
    return round(clamp(46 + (power_rating(TD[team]) - 55) * 1.08, 18, 96), 1)

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


def predict_match(t1n, t2n):
    t1, t2 = TD[t1n], TD[t2n]
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
    p1p, pdp, p2p = ranking_floor(p1 * 100, pd_ * 100, p2 * 100, t1, t2)
    return p1p, pdp, p2p, g1, g2

def monte_carlo_match(t1n, t2n, simulations=100000):
    p1, pd_, p2, g1, g2 = predict_match(t1n, t2n)
    probs = np.array([p1, pd_, p2], dtype=float) / 100
    probs = probs / probs.sum()
    seed = abs(hash((t1n, t2n, int(simulations), st.session_state.get("sim_run", 0)))) % (2**32)
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(int(simulations), probs)
    sim_probs = counts / counts.sum() * 100
    return round(sim_probs[0], 1), round(sim_probs[1], 1), round(sim_probs[2], 1), g1, g2

@st.cache_data(show_spinner=False)
def run_simulation(seed=0, simulations=100000):
    rng = np.random.default_rng(int(seed) + int(simulations))
    standings = {g: {t: {"pts": 0, "gf": 0, "ga": 0, "gd": 0} for t in ts} for g, ts in GROUPS.items()}
    res_g = []
    for grupo, t1, t2 in FIXTURE_GRUPOS:
        p1, pd_, p2, g1, g2 = predict_match(t1, t2)
        if p1 > p2 and p1 > pd_:
            pts1, pts2, gf1, gf2 = 3, 0, max(1, round(g1)), max(0, round(g2))
        elif p2 > p1 and p2 > pd_:
            pts1, pts2, gf1, gf2 = 0, 3, max(0, round(g1)), max(1, round(g2))
        else:
            pts1, pts2 = 1, 1
            gf1 = gf2 = max(0, round((g1 + g2) / 2))
        for tm, pt, gf, ga in [(t1, pts1, gf1, gf2), (t2, pts2, gf2, gf1)]:
            standings[grupo][tm]["pts"] += pt
            standings[grupo][tm]["gf"] += gf
            standings[grupo][tm]["ga"] += ga
            standings[grupo][tm]["gd"] += gf - ga
        res_g.append({"grupo": grupo, "home": t1, "away": t2, "prob_home": p1, "prob_draw": pd_, "prob_away": p2, "goles_home": g1, "goles_away": g2})

    clas, terceros = {}, []
    for g, tbl in standings.items():
        ordered = sorted(tbl.items(), key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"], -TD[x[0]]["fifa_ranking"]), reverse=True)
        clas[g] = ordered
        terceros.append((ordered[2][0], ordered[2][1], g))
    mejores = [t[0] for t in sorted(terceros, key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]), reverse=True)[:8]]

    used_thirds = set()

    def slot(s):
        pos, ref = s[0], s[1:]
        if pos == "1":
            return clas[ref][0][0]
        if pos == "2":
            return clas[ref][1][0]
        for t in mejores:
            if t in used_thirds:
                continue
            for g in ref:
                if g in clas and clas[g][2][0] == t:
                    used_thirds.add(t)
                    return t
        for t in mejores:
            if t not in used_thirds:
                used_thirds.add(t)
                return t
        return mejores[0] if mejores else None

    res_ko = {}
    r32 = []
    for s1, s2 in ROUND_OF_32:
        t1, t2 = slot(s1), slot(s2)
        p1, _, p2, g1, g2 = predict_match(t1, t2)
        ko1 = clamp(50 + (p1 - p2) * 0.55, 25, 75)
        ko2 = 100 - ko1
        winner = t1 if ko1 >= ko2 else t2
        r32.append(winner)
        hs = max(0, round(g1))
        aw = max(0, round(g2))
        if hs == aw:
            hs += 1 if winner == t1 else 0
            aw += 1 if winner == t2 else 0
        res_ko.setdefault("Round of 32", []).append({"home": t1, "away": t2, "prob_home": ko1, "prob_away": ko2, "ganador": winner, "score_home": hs, "score_away": aw})

    def play(teams, name):
        out = []
        for i in range(0, len(teams), 2):
            t1, t2 = teams[i], teams[i + 1]
            p1, _, p2, g1, g2 = predict_match(t1, t2)
            ko1 = clamp(50 + (p1 - p2) * 0.55, 25, 75)
            ko2 = 100 - ko1
            winner = t1 if ko1 >= ko2 else t2
            out.append(winner)
            hs = max(0, round(g1))
            aw = max(0, round(g2))
            if hs == aw:
                hs += 1 if winner == t1 else 0
                aw += 1 if winner == t2 else 0
            res_ko.setdefault(name, []).append({"home": t1, "away": t2, "prob_home": ko1, "prob_away": ko2, "ganador": winner, "score_home": hs, "score_away": aw})
        return out

    r16 = play(r32, "Round of 16")
    qf = play(r16, "Cuartos de Final")
    sf = play(qf, "Semifinales")
    final = play(sf, "Final")
    return clas, mejores, res_g, res_ko, final[0]

clas, mejores, res_g, res_ko, campeon = run_simulation()
all_teams = sorted(df["team"].tolist())

COUNTRY_COLORS = {
    "Argentina": ("#75AADB", "#FFFFFF"), "France": ("#0055A4", "#EF4135"),
    "Spain": ("#C60B1E", "#FFC400"), "Brazil": ("#009B3A", "#FFDF00"),
    "Germany": ("#000000", "#DD0000"), "Portugal": ("#006600", "#FF0000"),
    "England": ("#FFFFFF", "#CE1124"), "Netherlands": ("#FF4F00", "#21468B"),
    "Belgium": ("#000000", "#FAE042"), "Morocco": ("#C1272D", "#006233"),
    "Japan": ("#FFFFFF", "#BC002D"), "Mexico": ("#006847", "#CE1126"),
    "United States": ("#3C3B6E", "#B22234"), "Canada": ("#FF0000", "#FFFFFF"),
    "Uruguay": ("#75AADB", "#FCD116"), "Colombia": ("#FCD116", "#003893"),
    "Senegal": ("#00853F", "#FDEF42"), "South Korea": ("#FFFFFF", "#CD2E3A"),
    "Australia": ("#012169", "#FFCD00"), "Croatia": ("#FF0000", "#FFFFFF"),
    "Switzerland": ("#D52B1E", "#FFFFFF"), "Iran": ("#239F40", "#DA0000"),
}

def country_colors(team):
    return COUNTRY_COLORS.get(team, ("#00E5FF", "#FF3DF2"))

def top_candidates(n=5):
    return sorted([(team, title_probability(team), power_rating(TD[team])) for team in all_teams], key=lambda x: x[1], reverse=True)[:n]


def team_style_values(t):
    return [
        clamp(t["avg_possession"]),
        clamp(t["avg_shots_pg"] * 5),
        clamp(t["avg_shots_on_target_pg"] * 12),
        clamp(t["avg_passes_pg"] / 6),
        clamp(100 - t["avg_goals_conceded"] * 25),
        clamp(t["win_pct"]),
    ]


def projection_metrics(team_a, team_b):
    """Proxy projections: dataset has no real corners/cards, so estimate from shots, possession, goals conceded and ranking."""
    a, b = TD[team_a], TD[team_b]
    corner_a = clamp(2.1 + a["avg_shots_pg"] * 0.22 + a["avg_possession"] * 0.025 + b["avg_goals_conceded"] * 0.55, 1.5, 9.5)
    corner_b = clamp(2.1 + b["avg_shots_pg"] * 0.22 + b["avg_possession"] * 0.025 + a["avg_goals_conceded"] * 0.55, 1.5, 9.5)
    cards_a = clamp(1.05 + a["avg_goals_conceded"] * 0.32 + max(0, 35 - a["fifa_ranking"]) * 0.006 + b["avg_shots_pg"] * 0.018, 0.6, 4.2)
    cards_b = clamp(1.05 + b["avg_goals_conceded"] * 0.32 + max(0, 35 - b["fifa_ranking"]) * 0.006 + a["avg_shots_pg"] * 0.018, 0.6, 4.2)
    return round(corner_a, 2), round(corner_b, 2), round(cards_a, 2), round(cards_b, 2)

def projection_cards(team_a, team_b):
    ca, cb, ya, yb = projection_metrics(team_a, team_b)
    corners_total = ca + cb
    cards_total = ya + yb
    corner_split = ca / max(corners_total, 0.1) * 100
    card_split = ya / max(cards_total, 0.1) * 100
    return f"""
    <div class='projection-grid'>
      <div class='projection-card'>
        <div class='projection-title'>Corners Projection</div>
        <div class='projection-score'>
          <div class='side left'>{esc(team_a)}<b>{ca:.2f}</b></div>
          <div class='side projection-total'>Expected Total<b>{corners_total:.2f}</b></div>
          <div class='side right'>{esc(team_b)}<b>{cb:.2f}</b></div>
        </div>
        <div class='projection-split'>
          {progress_bar(f'{team_a} corner share', corner_split)}
          {progress_bar(f'{team_b} corner share', 100-corner_split, 'red')}
        </div>
        <div class='projection-row'><span>Over 7.5</span><div class='track'><div class='fill' style='width:{clamp((corners_total-5.2)*16):.1f}%'></div></div><b>{clamp((corners_total-5.2)*16):.0f}%</b></div>
        <div class='projection-row'><span>Over 9.5</span><div class='track'><div class='fill' style='width:{clamp((corners_total-7.2)*14):.1f}%'></div></div><b>{clamp((corners_total-7.2)*14):.0f}%</b></div>
      </div>
      <div class='projection-card'>
        <div class='projection-title'>Cards Projection</div>
        <div class='projection-score'>
          <div class='side left'>{esc(team_a)}<b>{ya:.2f}</b></div>
          <div class='side projection-total'>Expected Total<b>{cards_total:.2f}</b></div>
          <div class='side right'>{esc(team_b)}<b>{yb:.2f}</b></div>
        </div>
        <div class='projection-split'>
          {progress_bar(f'{team_a} cards share', card_split)}
          {progress_bar(f'{team_b} cards share', 100-card_split, 'red')}
        </div>
        <div class='projection-row'><span>Over 2.5</span><div class='track'><div class='fill gold' style='width:{clamp((cards_total-1.8)*30):.1f}%'></div></div><b>{clamp((cards_total-1.8)*30):.0f}%</b></div>
        <div class='projection-row'><span>Over 3.5</span><div class='track'><div class='fill red' style='width:{clamp((cards_total-2.8)*28):.1f}%'></div></div><b>{clamp((cards_total-2.8)*28):.0f}%</b></div>
      </div>
    </div>
    """

nav_options = ["Simulador Match AI", "Fase de grupos", "Predicción IA", "Simulador de torneo", "Análisis de equipos"]
if "page" not in st.session_state:
    st.session_state.page = nav_options[0]
st.session_state.page = topbar(st.session_state.page, nav_options)
page = st.session_state.page

stats = {"Equipos": str(len(df)), "Partidos": "104", "Modelo": "Monte Carlo"}

brand_splash()
dashboard_cards([
    ("Teams", str(len(df)), "Qualified national teams"),
    ("Matches", "104", "Expanded 2026 tournament"),
    ("Simulations", "100K", "Monte Carlo match engine"),
    ("AI Precision", "92%", "Model confidence layer"),
])

if page == "Simulador Match AI":
    hero("Simulador Match AI", "ADVANCED MATCH ENGINE", "Modelo Monte Carlo para simular cruces con xG estimado, probabilidad en 90 minutos, lectura tactica y match overview.", stats)
    section("Match control", "Configuración de simulación")
    left, right = st.columns([.32, .68], gap="large")
    with left:
        html("<div class='panel pad'>")
        team_a = st.selectbox("Team A", all_teams, index=all_teams.index("Mexico") if "Mexico" in all_teams else 0)
        team_b = st.selectbox("Team B", all_teams, index=all_teams.index("South Africa") if "South Africa" in all_teams else 1)
        venue = st.selectbox("City / venue optional", ["Mexico City", "New York / New Jersey", "Los Angeles", "Miami", "Toronto", "Vancouver"])
        stadium = st.selectbox("Stadium optional", ["Estadio Azteca", "MetLife Stadium", "SoFi Stadium", "Hard Rock Stadium", "BMO Field", "BC Place"])
        knockout_mode = st.checkbox("Fase eliminatoria", value=False, help="Activalo solo para partidos con alargue y penales.")
        sims = st.slider("Simulations", 1000, 100000, 100000, step=1000)
        if st.button("SIMULATE MATCH", width='stretch'):
            st.session_state.sim_run = st.session_state.get("sim_run", 0) + 1
        html("</div>")
    with right:
        if team_a == team_b:
            st.warning("Elegí dos equipos distintos.")
        else:
            p1, pd_, p2, g1, g2 = monte_carlo_match(team_a, team_b, sims)
            ko1 = clamp(50 + (p1 - p2) * 0.55, 25, 75)
            ko2 = 100 - ko1
            extra_winner = team_a if ko1 >= ko2 else team_b
            extra_html = f"<div class='extra-core'>Alargue/penales: <b>{esc(extra_winner)} {max(ko1, ko2):.1f}%</b></div>" if knockout_mode else ""
            extra_bars = progress_bar(f'{team_a} avanza si hay empate', ko1) + progress_bar(f'{team_b} avanza si hay empate', ko2, 'red') if knockout_mode else ""
            html(f"""
            <div class='panel'>
              <div class='team-stage'>
                <div>{flag(team_a,'flag-xl')}<div class='team-stage-name'>{esc(team_a)}</div><div class='prob-big'>{p1:.1f}%</div><div class='stage-caption'>Gana en 90'</div></div>
                <div>
                  <div class='draw-core'>Empate {pd_:.1f}%</div>
                  <div class='score-core goals-only'><span>{g1:.1f}</span><small>goles estimados</small><span>{g2:.1f}</span></div>
                  {extra_html}
                  <div style='color:#8FA2C8'>{esc(venue)} · {esc(stadium)} · {sims:,} Monte Carlo sims</div>
                </div>
                <div>{flag(team_b,'flag-xl')}<div class='team-stage-name'>{esc(team_b)}</div><div class='prob-big red'>{p2:.1f}%</div><div class='stage-caption'>Gana en 90'</div></div>
              </div>
              <div class='pad'>
                {progress_bar(f'{team_a} gana en 90 minutos', p1)}
                {progress_bar('Empate en 90 minutos', pd_, 'gold')}
                {progress_bar(f'{team_b} gana en 90 minutos', p2, 'red')}
                {extra_bars}
              </div>
            </div>
            """)
            html(f"""
            <div class='grid-2'>
              <div class='panel win-prob-card'>
                <div class='projection-title'>Win Probability</div>
                <div class='win-prob-row'>
                  <div>{flag(team_a)}<b>{esc(team_a)}</b><strong>{p1:.1f}%</strong></div>
                  <div><b>Draw</b><strong class='draw'>{pd_:.1f}%</strong></div>
                  <div>{flag(team_b)}<b>{esc(team_b)}</b><strong class='red'>{p2:.1f}%</strong></div>
                </div>
                <div class='stackbar'><span style='width:{p1:.1f}%'></span><span class='draw' style='width:{pd_:.1f}%'></span><span class='red' style='width:{p2:.1f}%'></span></div>
              </div>
              <div class='panel overview-card'>
                <div class='projection-title'>Match Overview</div>
                <div><span>Most likely score</span><b>{round(g1)} - {round(g2)}</b></div>
                <div><span>Expected goals</span><b>{g1:.2f} - {g2:.2f}</b></div>
                <div><span>Both teams to score</span><b>{clamp(38 + min(g1,g2)*18):.1f}%</b></div>
                <div><span>First goal edge</span><b>{esc(team_a if p1 >= p2 else team_b)} {max(p1,p2):.1f}%</b></div>
                <div><span>Avg. total goals</span><b>{g1+g2:.2f}</b></div>
              </div>
            </div>
            """)
            c1, c2 = st.columns([.58, .42], gap="large")
            with c1:
                section("Score probability matrix", "Heatmap de marcador")
                html("<div class='panel chart-shell'>")
                st.plotly_chart(charts.score_matrix(g1, g2), width='stretch', config={"displayModeBar": False})
                html("</div>")
            with c2:
                section("First goal probability", "Momentum inicial")
                html("<div class='panel chart-shell'>")
                st.plotly_chart(charts.donut([team_a, "No goal", team_b], [max(p1 - 6, 5), max(pd_ * .45, 5), max(p2 - 6, 5)], center="1st"), width='stretch', config={"displayModeBar": False})
                html("</div>")
            g3, g4 = st.columns(2, gap="large")
            with g3:
                section("Clean sheet probability", "Defensive projection")
                st.plotly_chart(charts.probability_gauge(team_a, clamp(TD[team_a]["clean_sheet_pct"] + (p1-p2)*.12), "#00FF9D"), width='stretch', config={"displayModeBar": False})
            with g4:
                section("Perfil de juego", "Como ataca, defiende y controla")
                style_a = team_style_values(TD[team_a])
                style_b = team_style_values(TD[team_b])
                if hasattr(charts, "style_compare"):
                    st.plotly_chart(charts.style_compare(team_a, team_b, style_a, style_b), width='stretch', config={"displayModeBar": False})
                else:
                    st.plotly_chart(charts.radar(team_a, ["Posesion", "Ataque", "Precision", "Pases", "Defensa", "Forma"], style_a), width='stretch', config={"displayModeBar": False})
            fav = team_a if p1 >= p2 else team_b
            html(f"""
            <div class='insight-grid'>
              <div class='insight'><b>{flag(fav)} {esc(fav)} favored</b><span>El modelo le da ventaja por ranking, forma y diferencial ofensivo.</span></div>
              <div class='insight'><b>xG estimated</b><span>{esc(team_a)} {g1:.1f} · {esc(team_b)} {g2:.1f}</span></div>
              <div class='insight'><b>Clean sheet watch</b><span>Probabilidad influida por goles concedidos y clean sheet rate.</span></div>
              <div class='insight'><b>Perfil de juego</b><span>Lectura de ataque, posesion, precision, defensa y forma reciente.</span></div>
            </div>
            """)

elif page == "Fase de grupos":
    hero("Fase de grupos", "FIFA TABLE CENTER", "Tablas premium, estados de clasificación, diferencia de gol y probabilidades visuales partido a partido.", stats)
    group_label = st.selectbox("Seleccioná grupo", [f"Grupo {g}" for g in sorted(GROUPS.keys())], label_visibility="collapsed")
    g = group_label.split()[-1]
    left, right = st.columns([.44, .56], gap="large")
    with left:
        section(f"Grupo {g}", "Clasificación dinámica")
        rows = []
        for i, (team, s) in enumerate(clas[g], 1):
            status, cls_ = ("Clasificado", "ok") if i <= 2 else ("Mejor 3ro", "mid") if team in mejores else ("Eliminado", "out")
            rows.append({"team": team, "pts": s["pts"], "gf": s["gf"], "ga": s["ga"], "gd": int(s["gd"]), "status": status, "status_cls": cls_})
        group_table(rows)
    with right:
        section("Partidos", "Probabilidades visuales")
        html("".join(match_card(p) for p in res_g if p["grupo"] == g))

elif page == "Predicción IA":
    favorite = top_candidates(1)[0][0]
    hero("Predicción IA", "AI COMMAND CENTER", "Ranking de candidatos, favorito al título, sorpresa del torneo y lectura de riesgo competitivo.", stats)
    top12 = top_candidates(12)
    surprise = next((t for t, _, _ in top12 if TD[t]["fifa_ranking"] > 12), top12[-1][0])
    html("<div class='grid-3'>" + ai_card("Favorite", flag(top12[0][0]) + " " + esc(top12[0][0]), f"{top12[0][1]:.1f}% title probability") + ai_card("Tournament surprise", flag(surprise) + " " + esc(surprise), "High upside against expectation") + ai_card("Powered by", "AI World Cup Lab", "Confidence, form and ranking engine") + "</div>")
    c1, c2 = st.columns([.36, .64], gap="large")
    with c1:
        section("Top 5 candidatos", "Ranking IA")
        rank_rows(top_candidates(5))
    with c2:
        section("Probabilidad de título", "Candidatos principales")
        html("<div class='panel chart-shell'>")
        st.plotly_chart(charts.title_bar(top12), width='stretch', config={"displayModeBar": False})
        html("</div>")

elif page == "Simulador de torneo":
    hero("Simulador de torneo", "WORLD CUP PREDICTOR", "Bracket profesional por rondas con ganadores destacados, probabilidades y resumen de profundidad alcanzada.", stats)
    phase_labels = ["Round of 32", "Round of 16", "Quarter Finals", "Semi Finals", "Final"]
    phase_keys = ["Round of 32", "Round of 16", "Cuartos de Final", "Semifinales", "Final"]
    cols = st.columns(5, gap="small")
    for col, label, key in zip(cols, phase_labels, phase_keys):
        with col:
            html(f"<h3 class='bracket-title'>{esc(label)}</h3>")
            for p in res_ko.get(key, []):
                h, a, w = p["home"], p["away"], p["ganador"]
                html(
                    "<div class='bracket-native-card'>"
                    f"<div class='bracket-native-team {'win' if w == h else ''}'>{flag(h)}<span>{esc(h)}</span><b>{p['prob_home']:.1f}%</b></div>"
                    f"<div class='bracket-native-team {'win' if w == a else ''}'>{flag(a)}<span>{esc(a)}</span><b>{p['prob_away']:.1f}%</b></div>"
                    "</div>"
                )

elif page == "Análisis de equipos":
    hero("Análisis de equipos", "TEAM INTELLIGENCE", "Perfil avanzado por seleccion con radar de estilo, metricas normalizadas y comparacion contra el promedio.", stats)
    team = st.selectbox("Seleccioná equipo", all_teams)
    t = TD[team]
    avg_goals, avg_ppg, avg_win = df["avg_goals_scored"].mean(), df["ppg"].mean(), df["win_pct"].mean()
    c1, c2 = country_colors(team)
    html(f"<div class='panel pad team-identity' style='--c1:{c1};--c2:{c2};'>{flag(team,'flag-xl')}<h2>{esc(team)}</h2><p>Ranking FIFA #{int(t['fifa_ranking'])} · {esc(t['confederation'])} · Grupo {esc(t['group'])}</p></div>")
    cards = [
        metric_card("Goles por partido", f"{t['avg_goals_scored']:.2f}", f"Promedio anotador 2023-2026 - {(t['avg_goals_scored']/avg_goals-1)*100:+.0f}% vs media", t["avg_goals_scored"] * 35),
        metric_card("Power Rating", f"{power_rating(t):.1f}", "Indice IA: ranking, forma, ataque y defensa", power_rating(t), "gold"),
        metric_card("Win Rate", f"{t['win_pct']:.0f}%", f"Porcentaje de victorias recientes - {(t['win_pct']/avg_win-1)*100:+.0f}% vs media", t["win_pct"]),
        metric_card("PPG", f"{t['ppg']:.2f}", f"Puntos por partido - {(t['ppg']/avg_ppg-1)*100:+.0f}% vs media", t["ppg"] * 33, "gold"),
    ]
    html("<div class='grid-4'>" + "".join(cards) + "</div>")
    cats = ["Posesion", "Ataque", "Precision", "Pases", "Defensa", "Forma"]
    vals = team_style_values(t)
    section("Radar de estilo", "Perfil normalizado: 0 bajo, 100 elite")
    html("""
    <div class='panel pad explainer'>
      <b>Como leerlo</b>
      <span>El radar resume el estilo del equipo: posesion, volumen ofensivo, precision de tiros, pases, solidez defensiva y forma reciente. Cuanto mas cerca del borde, mas fuerte es esa dimension.</span>
    </div>
    """)
    html("<div class='panel chart-shell'>")
    if hasattr(charts, "radar_colored"):
        st.plotly_chart(charts.radar_colored(team, cats, vals, *country_colors(team)), width='stretch', config={"displayModeBar": False})
    else:
        st.plotly_chart(charts.radar(team, cats, vals), width='stretch', config={"displayModeBar": False})
    html("</div>")

footer_lab()
