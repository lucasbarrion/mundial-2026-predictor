import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE_DIR, "data", "equipos.csv"))
print(f"✅ Dataset cargado: {len(df)} equipos, {len(df.columns)} columnas")

FEATURE_NAMES = [
    "fifa_ranking", "world_cups_won", "appearances", "is_host", "is_debut",
    "avg_goals_scored", "avg_goals_conceded", "win_pct", "draw_pct", "loss_pct",
    "clean_sheet_pct", "ppg", "goal_diff", "avg_possession",
    "avg_shots_pg", "avg_shots_on_target_pg", "avg_passes_pg"
]

def get_features(t):
    return [t[f] for f in FEATURE_NAMES]

def calc_strength(t):
    score = 0
    score += (100 - t["fifa_ranking"]) * 0.15
    score += t["ppg"] * 3.0
    score += t["avg_goals_scored"] * 2.0
    score -= t["avg_goals_conceded"] * 1.5
    score += t["win_pct"] * 0.05
    score += t["clean_sheet_pct"] * 0.03
    score += t["avg_shots_on_target_pg"] * 0.5
    score += t["avg_possession"] * 0.02
    score += t["world_cups_won"] * 1.5
    score += t["appearances"] * 0.1
    if t["is_host"] == 1:    score += 3.0
    if t["is_debut"] == 1:   score -= 4.0
    if t["appearances"] < 3: score -= 2.0
    if t["confederation"] in ["UEFA", "CONMEBOL"]: score += 1.5
    if t["confederation"] == "OFC":                score -= 3.0
    if t["goal_diff"] > 20:  score += 2.0
    elif t["goal_diff"] < 0: score -= 2.0
    return score

np.random.seed(42)
X, y = [], []
teams = df.to_dict("records")

for _ in range(8000):
    t1, t2 = np.random.choice(teams, 2, replace=False)
    diff = [a - b for a, b in zip(get_features(t1), get_features(t2))]
    X.append(diff)
    s1 = calc_strength(t1) + np.random.normal(0, 1.2)
    s2 = calc_strength(t2) + np.random.normal(0, 1.2)
    if s1 > s2 * 1.08:   y.append(0)
    elif s2 > s1 * 1.08: y.append(2)
    else:                 y.append(1)

X = np.array(X)
y = np.array(y)
print(f"✅ Partidos generados: {len(X)}")
print(f"   Victoria E1: {(y==0).sum()} | Empates: {(y==1).sum()} | Victoria E2: {(y==2).sum()}")

model = RandomForestClassifier(n_estimators=300, max_depth=10, min_samples_split=8, random_state=42, n_jobs=-1)
model.fit(X, y)
print(f"✅ Modelo entrenado")

model_path = os.path.join(BASE_DIR, "modelo", "modelo_mundial.pkl")
with open(model_path, "wb") as f:
    pickle.dump({"model": model, "features": FEATURE_NAMES}, f)

print(f"✅ Modelo guardado en: modelo/modelo_mundial.pkl")
print("\n🔍 Importancia de features:")
for feat, imp in sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1]):
    print(f"   {feat:<35} {imp:.3f}")
