import plotly.graph_objects as go

CYAN = "#00E5FF"
GREEN = "#00FF9D"
GOLD = "#F4C84A"
RED = "#FF476F"
MAGENTA = "#FF3DF2"
PURPLE = "#8A4DFF"

def theme(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#DDE8FF", family="Inter"),
        margin=dict(l=28, r=28, t=24, b=30),
    )
    return fig

def donut(labels, values, colors=None, center="AI"):
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=.62,
        marker_colors=colors or [CYAN, "#34405F", RED],
        textinfo="label+percent",
        sort=False,
    ))
    fig.update_layout(showlegend=False, annotations=[dict(text=center, x=.5, y=.5, showarrow=False, font_size=18, font_color=CYAN)])
    return theme(fig, 320)

def radar(title, categories, values):
    vals = list(values) + [values[0]]
    cats = list(categories) + [categories[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals,
        theta=cats,
        fill="toself",
        fillcolor="rgba(0,229,255,.20)",
        line=dict(color=CYAN, width=3),
        marker=dict(color=GOLD, size=7),
        name=title,
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,.10)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,.10)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
    )
    return theme(fig, 360)

def title_bar(candidates):
    colors = [GREEN, GREEN, CYAN, CYAN, GOLD, GOLD, MAGENTA, MAGENTA, PURPLE, PURPLE, RED, RED]
    items = list(reversed(candidates))
    fig = go.Figure(go.Bar(
        x=[x[1] for x in items],
        y=[x[0] for x in items],
        orientation="h",
        marker_color=list(reversed(colors[:len(items)])),
        text=[f"{x[1]:.1f}%" for x in items],
        textposition="outside",
    ))
    fig.update_layout(xaxis=dict(visible=False, range=[0, max([x[1] for x in candidates]) + 12]), yaxis=dict(tickfont=dict(size=12)))
    return theme(fig, 430)

def score_matrix(g1, g2):
    x, y, z = [], [], []
    for hg in range(6):
        row = []
        for ag in range(6):
            dist = abs(hg - g1) + abs(ag - g2)
            row.append(max(1, 18 - dist * 4))
        z.append(row)
    fig = go.Figure(go.Heatmap(
        z=z,
        x=[str(i) for i in range(6)],
        y=[str(i) for i in range(6)],
        colorscale=[[0, "#111A3A"], [.45, "#2F7DFF"], [.75, "#FF3DF2"], [1, "#FF476F"]],
        showscale=False,
        text=[[f"{r[c]:.1f}%" for c in range(6)] for r in z],
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"},
    ))
    fig.update_layout(xaxis_title="Away goals", yaxis_title="Home goals")
    return theme(fig, 330)

def stage_bar(scores, labels, colors):
    fig = go.Figure(go.Bar(
        x=labels,
        y=scores,
        marker_color=colors,
        text=labels,
        textposition="outside",
    ))
    fig.update_layout(yaxis=dict(visible=False, range=[0, 7.4]), xaxis=dict(tickangle=-35), bargap=.32)
    return theme(fig, 430)


def momentum_chart(home, away, p_home, p_away):
    minutes = list(range(0, 91, 10))
    base = []
    for i, m in enumerate(minutes):
        swing = ((i % 4) - 1.5) * 2.8
        base.append(max(5, min(95, p_home + swing - (m / 90) * (p_home - p_away) * .15)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=minutes, y=base, mode="lines+markers", name=home, line=dict(color=CYAN, width=3), fill="tozeroy", fillcolor="rgba(0,229,255,.12)"))
    fig.add_trace(go.Scatter(x=minutes, y=[100 - x for x in base], mode="lines+markers", name=away, line=dict(color=RED, width=3)))
    fig.update_layout(yaxis=dict(range=[0,100], title="Momentum"), xaxis=dict(title="Minute"), legend=dict(orientation="h"))
    return theme(fig, 300)

def probability_gauge(label, value, color=CYAN):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": label, "font": {"color": "#DDE8FF", "size": 14}},
        number={"suffix": "%", "font": {"color": "#F8FBFF", "size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#8FA2C8"},
            "bar": {"color": color},
            "bgcolor": "rgba(255,255,255,.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35], "color": "rgba(255,71,111,.16)"},
                {"range": [35, 65], "color": "rgba(248,210,74,.14)"},
                {"range": [65, 100], "color": "rgba(0,255,157,.14)"},
            ],
        },
    ))
    return theme(fig, 250)


def style_compare(team_a, team_b, values_a, values_b):
    labels = ["Posesion", "Ataque", "Precision", "Pases", "Defensa", "Forma"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values_a,
        y=labels,
        orientation="h",
        name=team_a,
        marker_color=CYAN,
        text=[f"{v:.0f}" for v in values_a],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=[-v for v in values_b],
        y=labels,
        orientation="h",
        name=team_b,
        marker_color=RED,
        text=[f"{v:.0f}" for v in values_b],
        textposition="outside",
    ))
    fig.update_layout(
        barmode="relative",
        xaxis=dict(range=[-105, 105], zeroline=True, zerolinecolor="rgba(255,255,255,.35)", tickvals=[-100, -50, 0, 50, 100], ticktext=["100", "50", "0", "50", "100"]),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h"),
    )
    return theme(fig, 300)


def radar_colored(title, categories, values, primary=CYAN, secondary=GOLD):
    vals = list(values) + [values[0]]
    cats = list(categories) + [categories[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals,
        theta=cats,
        fill="toself",
        fillcolor="rgba(255,255,255,.16)",
        line=dict(color=primary, width=4),
        marker=dict(color=secondary, size=8),
        name=title,
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,.10)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,.10)", tickfont=dict(color="#F8FBFF")),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
    )
    return theme(fig, 390)
