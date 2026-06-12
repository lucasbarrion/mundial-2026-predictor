from __future__ import annotations

import base64
import html as _html
import mimetypes
import textwrap
from pathlib import Path
import streamlit as st

FLAG_CODES = {
    "France":"fr","Spain":"es","Argentina":"ar","England":"gb-eng","Portugal":"pt","Brazil":"br",
    "Netherlands":"nl","Morocco":"ma","Belgium":"be","Germany":"de","Croatia":"hr","Colombia":"co",
    "Senegal":"sn","Mexico":"mx","United States":"us","Uruguay":"uy","Japan":"jp","Switzerland":"ch",
    "Iran":"ir","Austria":"at","Ecuador":"ec","South Korea":"kr","Australia":"au","Egypt":"eg",
    "Canada":"ca","Ivory Coast":"ci","Qatar":"qa","Algeria":"dz","Sweden":"se","Tunisia":"tn",
    "Czech Republic":"cz","Turkey":"tr","Norway":"no","Scotland":"gb-sct","DR Congo":"cd",
    "Bosnia and Herzegovina":"ba","Panama":"pa","Saudi Arabia":"sa","South Africa":"za","Iraq":"iq",
    "New Zealand":"nz","Cape Verde":"cv","Uzbekistan":"uz","Jordan":"jo","Curaçao":"cw","Curacao":"cw",
    "Haiti":"ht","Paraguay":"py","Ghana":"gh","Nigeria":"ng",
}

FLAGS = {
    "France":"🇫🇷","Spain":"🇪🇸","Argentina":"🇦🇷","England":"🏴","Portugal":"🇵🇹","Brazil":"🇧🇷",
    "Netherlands":"🇳🇱","Morocco":"🇲🇦","Belgium":"🇧🇪","Germany":"🇩🇪","Croatia":"🇭🇷","Colombia":"🇨🇴",
    "Senegal":"🇸🇳","Mexico":"🇲🇽","United States":"🇺🇸","Uruguay":"🇺🇾","Japan":"🇯🇵","Switzerland":"🇨🇭",
    "Iran":"🇮🇷","Austria":"🇦🇹","Ecuador":"🇪🇨","South Korea":"🇰🇷","Australia":"🇦🇺","Egypt":"🇪🇬",
    "Canada":"🇨🇦","Ivory Coast":"🇨🇮","Qatar":"🇶🇦","Algeria":"🇩🇿","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Czech Republic":"🇨🇿","Turkey":"🇹🇷","Norway":"🇳🇴","Scotland":"🏴","DR Congo":"🇨🇩",
    "Bosnia and Herzegovina":"🇧🇦","Panama":"🇵🇦","Saudi Arabia":"🇸🇦","South Africa":"🇿🇦","Iraq":"🇮🇶",
    "New Zealand":"🇳🇿","Cape Verde":"🇨🇻","Uzbekistan":"🇺🇿","Jordan":"🇯🇴","Curaçao":"🇨🇼","Curacao":"🇨🇼",
    "Haiti":"🇭🇹","Paraguay":"🇵🇾","Ghana":"🇬🇭","Nigeria":"🇳🇬",
}

def esc(value) -> str:
    return _html.escape(str(value))

def html(markup: str) -> None:
    cleaned = textwrap.dedent(markup).strip()
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

def load_css(path: str = "styles.css") -> None:
    with open(path, "r", encoding="utf-8") as f:
        html(f"<style>{f.read()}</style>")


def asset_data_uri(filename: str) -> str:
    path = Path(__file__).resolve().parent / "assets" / filename
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"

def asset_img(filename: str, cls: str, alt: str) -> str:
    return f"<img class='{cls}' src='{asset_data_uri(filename)}' alt='{esc(alt)}'>"

def main_logo(cls: str = "brand-logo-img") -> str:
    return asset_img("fifa_2026_logo_transparent.png", cls, "FIFA 2026 logo")

def ball_logo(cls: str = "ball-logo-img") -> str:
    return asset_img("worldcup_ball_transparent.png", cls, "World Cup ball")

def world_cup_mark(size: int = 76) -> str:
    return f"""<svg class='wc-mark' width='{size}' height='{size}' viewBox='0 0 96 96' role='img' aria-label='World Cup 2026 AI Lab mark'>
    <defs>
      <linearGradient id='g1' x1='0' x2='1' y1='0' y2='1'><stop stop-color='#FFF2A6'/><stop offset='.48' stop-color='#F4C84A'/><stop offset='1' stop-color='#8B6A12'/></linearGradient>
      <linearGradient id='g2' x1='0' x2='1'><stop stop-color='#00E5FF'/><stop offset='.55' stop-color='#F4C84A'/><stop offset='1' stop-color='#FF3DF2'/></linearGradient>
    </defs>
    <rect x='13' y='6' width='70' height='84' rx='20' fill='rgba(255,255,255,.04)' stroke='url(#g2)' stroke-width='2'/>
    <path d='M31 20h34c-1 20-8 32-17 37-9-5-16-17-17-37z' fill='url(#g1)'/>
    <path d='M31 23c-12 2-15 11-10 19 3 6 9 9 18 10' fill='none' stroke='#F4C84A' stroke-width='5' stroke-linecap='round'/>
    <path d='M65 23c12 2 15 11 10 19-3 6-9 9-18 10' fill='none' stroke='#F4C84A' stroke-width='5' stroke-linecap='round'/>
    <rect x='43' y='56' width='10' height='12' rx='2' fill='#F4C84A'/>
    <path d='M34 75h28l5 9H29z' fill='url(#g1)'/>
    <text x='48' y='38' text-anchor='middle' font-size='11' font-weight='900' fill='#07112C'>FIFA</text>
    <text x='48' y='69' text-anchor='middle' font-size='10' font-weight='900' fill='#F8FBFF'>2026</text>
    </svg>"""

def flag(team: str, cls: str = "flag-sm") -> str:
    team_e = esc(team)
    code = FLAG_CODES.get(team)
    fallback = FLAGS.get(team, "🏳️")
    if not code:
        return f"<span class='flag-fallback' style='display:inline-block'>{fallback}</span>"
    return (
        f"<span class='flag-fallback'>{fallback}</span>"
        f"<img class='{cls}' src='https://flagcdn.com/w160/{code}.png' alt='{team_e} flag' "
        "onerror=\"this.style.display='none';this.previousElementSibling.style.display='inline-block';\">"
    )

def topbar(active: str, options: list[str]) -> str:
    html(f"""
    <div class='topbar'>
      <div class='brand-row'>
        <div class='brand-left'>
          {main_logo("brand-logo-img")}
          <div>
            <div class='brand-title'>WORLD CUP AI PREDICTION</div>
            <div class='brand-sub'>FIFA 2026 MONTE CARLO INTELLIGENCE</div>
          </div>
        </div>
        <div class='nav-shell'>{ball_logo("top-ball-img")}</div>
      </div>
      <div class='rgb-line'></div>
    </div>
    """)
    return st.radio(
        "Navegacion principal",
        options,
        index=options.index(active) if active in options else 0,
        horizontal=True,
        label_visibility="collapsed",
    )

def hero(title: str, eyebrow: str, copy: str, stats: dict[str, str]) -> None:
    stat_html = "".join(f"<div class='mini-stat'><b>{esc(v)}</b><span>{esc(k)}</span></div>" for k, v in stats.items())
    html(f"""
    <div class='hero'>
      <div class='hero-grid'>
        <div>
          <div class='eyebrow'>{esc(eyebrow)}</div>
          <h1>{esc(title)}</h1>
          <p>{esc(copy)}</p>
          <div class='badge-row'>
            <span class='badge hot'>FIFA 2026</span>
            <span class='badge'>AI Prediction</span>
            <span class='badge'>Advanced simulation</span>
            <span class='badge'>World Cup Lab</span>
          </div>
        </div>
        <div class='hero-side'>
          {main_logo("hero-logo-img")}
          <div class='hero-side-title'>WORLD CUP AI PREDICTION</div>
          <div class='hero-ball'>{ball_logo("hero-ball-img")}</div>
          <div class='mini-stats'>{stat_html}</div>
        </div>
      </div>
    </div>
    """)

def section(title: str, sub: str = "") -> None:
    html(f"<div class='section-head'><h2>{esc(title)}</h2><p>{esc(sub)}</p></div>")

def progress_bar(label: str, value: float, cls: str = "") -> str:
    value = max(0, min(100, float(value)))
    return f"<div class='prob-line'><span>{esc(label)}</span><div class='track'><div class='fill {cls}' style='width:{value:.1f}%'></div></div><b>{value:.1f}%</b></div>"

def metric_card(label: str, value: str, note: str, pct: float, cls: str = "") -> str:
    return f"""<div class='panel metric-card'>
      <div class='metric-label'>{esc(label)}</div>
      <div class='metric-value'>{esc(value)}</div>
      <div class='metric-note'>{esc(note)}</div>
      <div class='track'><div class='fill {cls}' style='width:{max(0,min(100,float(pct))):.1f}%'></div></div>
    </div>"""

def group_table(rows: list[dict]) -> None:
    body = []
    for r in rows:
        body.append(
            "<div class='group-row'>"
            f"<div>{flag(r['team'])}</div>"
            f"<div class='team-name'>{esc(r['team'])}</div>"
            f"<div>{r['pts']}</div><div>{r['gf']}</div><div>{r['ga']}</div>"
            f"<div class=\"{'dg-pos' if r['gd'] >= 0 else 'dg-neg'}\">{r['gd']:+d}</div>"
            f"<div class='status {r['status_cls']}'>{esc(r['status'])}</div>"
            "</div>"
        )
    html("<div class='panel group-table'><div class='group-row head'><div></div><div>Equipo</div><div>PTS</div><div>GF</div><div>GC</div><div>DG</div><div>Estado</div></div>" + "".join(body) + "</div>")

def match_card(p: dict) -> str:
    h, a = p["home"], p["away"]
    return f"""<div class='panel match-card'>
      <div class='match-line'>
        <div>{flag(h,'flag-lg')}<div class='match-name'>{esc(h)}</div><div>{p['prob_home']:.1f}% win</div></div>
        <div><div class='match-score'>{p['goles_home']:.0f} - {p['goles_away']:.0f}</div><div>{p['prob_draw']:.1f}% draw</div></div>
        <div>{flag(a,'flag-lg')}<div class='match-name'>{esc(a)}</div><div>{p['prob_away']:.1f}% win</div></div>
      </div>
      {progress_bar(h, p['prob_home'])}
      {progress_bar('Draw', p['prob_draw'], 'gold')}
      {progress_bar(a, p['prob_away'], 'red')}
    </div>"""

def rank_rows(items: list[tuple[str, float, float]]) -> None:
    rows = []
    for i, (team, prob, power) in enumerate(items, 1):
        rows.append(
            "<div class='panel rank-row'>"
            f"<div class='rank-no'>#{i}</div>"
            f"<div><div class='rank-team'>{flag(team)} {esc(team)}</div><div class='rank-meta'>Power {power:.1f}</div></div>"
            f"<div class='rank-prob'>{prob:.1f}%</div>"
            "</div>"
        )
    html("".join(rows))


def secondary_trophy(size: int = 34) -> str:
    return world_cup_mark(size)

def brand_splash() -> None:
    html(f"""
    <div class='splash'>
      <div>{main_logo("splash-logo-img")}</div>
      <div>
        <div class='splash-title'>WORLD CUP AI PREDICTION</div>
        <div class='splash-copy'>Modelo analitico construido sobre mas de 100 variables competitivas de selecciones nacionales entre 2023 y 2026.</div>
        <div class='splash-meta'>Plataforma de inteligencia deportiva impulsada por IA que combina analitica avanzada, simulaciones Monte Carlo y metricas competitivas para modelar el desempeno de las selecciones participantes del Mundial 2026.</div>
      </div>
      <div>{ball_logo("splash-ball-img")}</div>
    </div>
    """)

def dashboard_cards(items: list[tuple[str, str, str]]) -> None:
    cards = []
    for label, value, note in items:
        cards.append(f"""
        <div class='panel dashboard-card'>
          <div class='trophy-mini'>{main_logo("card-logo-img")}</div>
          <b>{esc(value)}</b>
          <span>{esc(label)}</span>
          <small>{esc(note)}</small>
        </div>
        """)
    html("<div class='grid-4'>" + "".join(cards) + "</div>")

def ai_card(label: str, value: str, note: str) -> str:
    return f"""
    <div class='panel ai-card'>
      <div class='trophy-mini'>{main_logo("card-logo-img")}</div>
      <div class='ai-label'>{esc(label)}</div>
      <div class='ai-main'>{value}</div>
      <div class='ai-sub'>{esc(note)}</div>
    </div>
    """

def footer_lab() -> None:
    html(f"""
    <div class='footer-lab'>
      <div>{main_logo("footer-logo-img")}</div>
      <div><strong>WORLD CUP AI PREDICTION</strong><br>Powered by AI World Cup Lab · Premium tournament simulation interface</div>
      <div>{ball_logo("footer-ball-img")}</div>
    </div>
    """)
