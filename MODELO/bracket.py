# ─────────────────────────────────────────────────────────────
# BRACKET OFICIAL FIFA WORLD CUP 2026
# ─────────────────────────────────────────────────────────────

GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Switzerland", "Bosnia and Herzegovina", "Qatar"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

FIXTURE_GRUPOS = [
    ("A","Mexico","South Africa"), ("A","South Korea","Czech Republic"),
    ("A","Mexico","South Korea"), ("A","Czech Republic","South Africa"),
    ("A","Mexico","Czech Republic"), ("A","South Africa","South Korea"),
    ("B","Canada","Bosnia and Herzegovina"), ("B","Qatar","Switzerland"),
    ("B","Canada","Qatar"), ("B","Switzerland","Bosnia and Herzegovina"),
    ("B","Canada","Switzerland"), ("B","Bosnia and Herzegovina","Qatar"),
    ("C","Brazil","Morocco"), ("C","Haiti","Scotland"),
    ("C","Brazil","Haiti"), ("C","Morocco","Scotland"),
    ("C","Brazil","Scotland"), ("C","Morocco","Haiti"),
    ("D","United States","Paraguay"), ("D","Australia","Turkey"),
    ("D","United States","Australia"), ("D","Turkey","Paraguay"),
    ("D","United States","Turkey"), ("D","Paraguay","Australia"),
    ("E","Germany","Curaçao"), ("E","Ivory Coast","Ecuador"),
    ("E","Germany","Ivory Coast"), ("E","Ecuador","Curaçao"),
    ("E","Germany","Ecuador"), ("E","Curaçao","Ivory Coast"),
    ("F","Netherlands","Japan"), ("F","Sweden","Tunisia"),
    ("F","Netherlands","Sweden"), ("F","Japan","Tunisia"),
    ("F","Netherlands","Tunisia"), ("F","Sweden","Japan"),
    ("G","Belgium","Egypt"), ("G","Iran","New Zealand"),
    ("G","Belgium","Iran"), ("G","Egypt","New Zealand"),
    ("G","Belgium","New Zealand"), ("G","Egypt","Iran"),
    ("H","Spain","Cape Verde"), ("H","Saudi Arabia","Uruguay"),
    ("H","Spain","Saudi Arabia"), ("H","Uruguay","Cape Verde"),
    ("H","Spain","Uruguay"), ("H","Cape Verde","Saudi Arabia"),
    ("I","France","Senegal"), ("I","Iraq","Norway"),
    ("I","France","Iraq"), ("I","Norway","Senegal"),
    ("I","France","Norway"), ("I","Senegal","Iraq"),
    ("J","Argentina","Algeria"), ("J","Austria","Jordan"),
    ("J","Argentina","Austria"), ("J","Algeria","Jordan"),
    ("J","Argentina","Jordan"), ("J","Algeria","Austria"),
    ("K","Portugal","DR Congo"), ("K","Uzbekistan","Colombia"),
    ("K","Portugal","Uzbekistan"), ("K","Colombia","DR Congo"),
    ("K","Portugal","Colombia"), ("K","DR Congo","Uzbekistan"),
    ("L","England","Croatia"), ("L","Ghana","Panama"),
    ("L","England","Ghana"), ("L","Croatia","Panama"),
    ("L","England","Panama"), ("L","Croatia","Ghana"),
]

# ─────────────────────────────────────────────────────────────
# ROUND OF 32 - CRUCES OFICIALES
# Los slots "3XXXX" se rellenan con el mejor 3ro
# de esos grupos según puntos/GD/GF/ranking FIFA
# ─────────────────────────────────────────────────────────────
ROUND_OF_32 = [
    # LADO IZQUIERDO
    ("1E",  "3ABCDF"),
    ("1I",  "3CDFGH"),
    ("2A",  "2B"),
    ("1F",  "2C"),
    ("2K",  "2L"),
    ("1H",  "2J"),
    ("1D",  "3BEFIJ"),
    ("1G",  "3AEHIJ"),
    # LADO DERECHO
    ("1C",  "2F"),
    ("2E",  "2I"),
    ("1A",  "3CFH"),
    ("1L",  "3EHK"),
    ("1J",  "2H"),
    ("2D",  "2G"),
    ("1B",  "3EFGJ"),
    ("1K",  "3DFIL"),
]

# Grupos de origen permitidos para cada slot de 3ro
THIRD_PLACE_SLOTS = {
    "3ABCDF":  list("ABCDF"),
    "3CDFGH":  list("CDFGH"),
    "3BEFIJ":  list("BEFIJ"),
    "3AEHIJ":  list("AEHIJ"),
    "3CFH":    list("CFH"),
    "3EHK":    list("EHK"),
    "3EFGJ":   list("EFGJ"),
    "3DFIL":   list("DFIL"),
}

# ─────────────────────────────────────────────────────────────
# CRITERIOS DE DESEMPATE para 3ros (orden oficial FIFA)
# 1. Puntos
# 2. Diferencia de goles
# 3. Goles a favor
# 4. Fair play (menos tarjetas)
# 5. Ranking FIFA
# ─────────────────────────────────────────────────────────────
def rank_third_place_teams(thirds):
    """
    Recibe lista de dicts con info de los 12 terceros.
    Retorna los 8 mejores ordenados por criterios FIFA.
    """
    ranked = sorted(thirds, key=lambda t: (
        -t["points"],
        -t["goal_diff"],
        -t["goals_for"],
        t["yellow_cards"] + t["red_cards"] * 3,  # fair play
        t["fifa_ranking"],
    ))
    return ranked[:8]

def assign_third_place_to_slots(best_8_thirds, slots):
    """
    Asigna cada 3ro clasificado al slot correspondiente
    según su grupo de origen.
    slot_groups = grupos elegibles para ese slot
    """
    assignments = {}
    used = set()
    for slot, eligible_groups in slots.items():
        for team in best_8_thirds:
            if team["group"] in eligible_groups and team["name"] not in used:
                assignments[slot] = team["name"]
                used.add(team["name"])
                break
    return assignments

# Round of 16 (ganadores del R32 por pares)
ROUND_OF_16_PAIRS = [(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15)]

# Cuartos de final
QUARTERS_PAIRS = [(0,1),(2,3),(4,5),(6,7)]

# Semifinales
SEMIS_PAIRS = [(0,1),(2,3)]

if __name__ == "__main__":
    print("✅ Bracket oficial FIFA 2026")
    print(f"\n{'─'*50}")
    print("ROUND OF 32:")
    print("LADO IZQUIERDO:")
    for i,(s1,s2) in enumerate(ROUND_OF_32[:8],1):
        print(f"  L{i:02d}: {s1:<12} vs {s2}")
    print("\nLADO DERECHO:")
    for i,(s1,s2) in enumerate(ROUND_OF_32[8:],9):
        print(f"  L{i:02d}: {s1:<12} vs {s2}")
    print(f"\n{'─'*50}")
    print("CRITERIOS 3ros clasificados (orden FIFA):")
    print("  1. Puntos")
    print("  2. Diferencia de goles")
    print("  3. Goles a favor")
    print("  4. Fair play (tarjetas)")
    print("  5. Ranking FIFA")
