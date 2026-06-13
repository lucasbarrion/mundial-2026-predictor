# 🏆 FIFA World Cup 2026 — AI Predictor

<div align="center">

![FIFA 2026](https://img.shields.io/badge/FIFA-World%20Cup%202026-gold?style=for-the-badge&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-RandomForest-orange?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge)

**Aplicación web de predicción del Mundial 2026 con inteligencia artificial.**

Motor Random Forest + simulaciones Monte Carlo + visualizaciones premium estilo Sofascore / Opta Analyst.

### [🚀 Ver App en vivo](https://mundial-2026-predictor-8qyeoouyfkefauwagvn2x7.streamlit.app/)

</div>

---

## ⚙️ Cómo funciona el ecosistema

![Ecosistema FIFA 2026 AI Predictor](assets/DIAGRAMA%20MUNDIAL%20PREDICTOR.png)

## ¿Qué es este proyecto?

FIFA World Cup 2026 AI Predictor es una aplicación web interactiva que combina **machine learning**, **datos reales de selecciones nacionales** y **visualizaciones de nivel profesional** para simular y predecir el torneo más grande del fútbol.

El sistema analiza **48 selecciones clasificadas** usando métricas reales (ranking FIFA, goles por partido, posesión, win rate, clean sheets, PPG y más) para calcular probabilidades de victoria en cada partido, simular la fase de grupos completa y proyectar el bracket eliminatorio hasta el campeón.

---

## ✨ Funcionalidades

| Sección | Descripción |
|---|---|
| ⚽ **Simulador Match AI** | Simulá cualquier cruce con Monte Carlo, probabilidades en 90', xG estimado, heatmap de marcadores, corners y tarjetas proyectadas, clean sheet gauge y análisis de perfil de juego |
| 🏟️ **Fase de Grupos** | Tablas estilo FIFA con estados de clasificación, diferencia de gol y probabilidades partido a partido |
| 🧠 **Predicción IA** | Ranking de candidatos al título, sorpresa del torneo y barra de probabilidades comparativa entre los 12 principales |
| 🗺️ **Simulador de Torneo** | Bracket completo Round of 32 → Final con probabilidades por llave y campeón predicho |
| 📊 **Análisis de Equipos** | Perfil avanzado por selección: radar de estilo, métricas normalizadas (Power Rating, Win Rate, PPG, goles) y comparación contra el promedio global |

---

## 🗂️ Estructura del proyecto

```
mundial-2026-predictor/
├── app.py                      # Archivo principal — Streamlit app
├── components.py               # Componentes visuales (navbar, hero, cards, flags)
├── charts.py                   # Gráficos Plotly (radar, donut, gauge, heatmap, barras)
├── styles.css                  # Diseño premium: glassmorphism, colores FIFA
├── requirements.txt            # Dependencias del proyecto
├── DATA/
│   ├── equipos.csv             # Base de datos de las 48 selecciones
│   └── fixture_grupos.csv      # Fixture oficial fase de grupos (72 partidos)
├── MODELO/
│   ├── bracket.py              # Grupos, fixtures y cruces oficiales del Mundial 2026
│   ├── simulador.py            # Simulador auxiliar de consola
│   ├── train_model.py          # Script para entrenar el modelo desde cero
│   └── modelo_mundial.pkl      # Modelo Random Forest entrenado
└── assets/                     # Logos e imágenes
```

---

## ⚙️ Cómo funciona

```
app.py
├── components.py   →  navbar, hero, cards, banderas
├── charts.py       →  radar, donut, heatmap, gauges
├── styles.css      →  diseño premium glassmorphism
├── DATA/equipos.csv           →  estadísticas reales
├── MODELO/modelo_mundial.pkl  →  predicciones ML
└── MODELO/bracket.py          →  cruces oficiales FIFA
        │
        ▼
  Streamlit Server
        │
        ▼
  https://mundial-2026-predictor-8qyeoouyfkefauwagvn2x7.streamlit.app/
```

- **`app.py`** es el cerebro — conecta todo y renderiza la interfaz
- **`DATA/equipos.csv`** aporta las estadísticas reales de cada selección
- **`modelo_mundial.pkl`** predice probabilidades de resultado con Random Forest
- **`bracket.py`** conoce los grupos y cruces oficiales del Mundial
- **`components.py`** y **`charts.py`** dan el look premium visual

---

## 📊 Dataset — `DATA/equipos.csv`

Base de datos de las **48 selecciones clasificadas** con estadísticas reales 2023–2026.

**Fuentes:**
- `martj42/international_results` (GitHub) — 49.000+ partidos internacionales
- StatsBomb Open Data — Copa América 2024, UEFA Euro 2024, AFCON 2023

| Columna | Descripción |
|---|---|
| `team` | Nombre del equipo |
| `group` | Grupo asignado (A–L) |
| `confederation` | UEFA / CONMEBOL / AFC / CAF / CONCACAF / OFC |
| `fifa_ranking` | Ranking FIFA oficial |
| `world_cups_won` | Copas del Mundo ganadas |
| `appearances` | Participaciones históricas en Mundiales |
| `is_host` | 1 si es sede (USA, México, Canadá) |
| `is_debut` | 1 si debuta en 2026 |
| `avg_goals_scored` | Promedio de goles anotados por partido |
| `avg_goals_conceded` | Promedio de goles recibidos por partido |
| `win_pct / draw_pct / loss_pct` | % de victorias, empates y derrotas |
| `clean_sheet_pct` | % de partidos sin goles en contra |
| `ppg` | Puntos por partido |
| `goal_diff` | Diferencia de goles acumulada |
| `avg_possession` | Posesión promedio % |
| `avg_shots_pg` | Disparos por partido |
| `avg_shots_on_target_pg` | Disparos al arco por partido |
| `avg_passes_pg` | Pases por partido |

---

## 🤖 Modelo de IA

**Algoritmo:** Random Forest Classifier (scikit-learn)  
**Features:** métricas del dataset (diferencia entre equipo local y visitante)  
**Salida:** Probabilidades para 3 clases — Victoria / Empate / Derrota

### Power Rating

| Dimensión | Peso | Variables |
|---|---|---|
| Ataque | 30% | `avg_goals_scored`, `avg_shots_on_target_pg` |
| Defensa | 25% | `avg_goals_conceded`, `clean_sheet_pct` |
| Forma | 25% | `win_pct`, `ppg` |
| Ranking | 20% | `fifa_ranking` |

### Calibración

Las probabilidades combinan el output del Random Forest (34%) con un modelo de fortaleza diferencial (66%):

- 🏠 **Ventaja local** → ajuste para USA, México y Canadá (máximo +5.5 pts)
- 🌟 **Debut** → −4 pts (Cape Verde, Curaçao, Jordan, Uzbekistan)
- 🌍 **Confederación** → UEFA y CONMEBOL +0.9 pts; AFC −1.2 pts; OFC −3 pts
- 📉 **Poca experiencia** → penalización para equipos con menos de 3 mundiales
- 🔝 **Top 3 FIFA** → piso mínimo garantizado en cualquier cruce (≥30%)
- 🔢 **Top 5 vs fuera del top 10** → piso de 52% para el favorito

### Simulación Monte Carlo

Hasta **100.000 simulaciones** por cruce usando `numpy.random.default_rng` con seed reproducible.

---

## 🏟️ Bracket oficial FIFA 2026

- **12 grupos** (A–L) con 4 equipos → **72 partidos**
- **Clasifican:** Top 2 de cada grupo (24) + 8 mejores terceros = **32 equipos**
- **Eliminación directa:** Round of 32 → R16 → Cuartos → Semis → Final
- Terceros clasificados asignados por criterio FIFA (puntos, DG, GF)

---

## 🚀 Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/lucasbarrion/mundial-2026-predictor.git
cd mundial-2026-predictor

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Entrenar el modelo (solo la primera vez)
python MODELO/train_model.py

# 5. Ejecutar la app
streamlit run app.py
```

En Windows también podés ejecutar directamente `ABRIR_APP_MUNDIAL.bat`.

---

## 🛠️ Stack tecnológico

| Tecnología | Uso |
|---|---|
| Python 3.11+ | Lenguaje principal |
| Streamlit 1.35+ | Framework web |
| Scikit-learn | Modelo Random Forest |
| Pandas + NumPy | Procesamiento de datos y simulaciones |
| Plotly | Visualizaciones interactivas |
| CSS / HTML | Diseño premium glassmorphism |
| flagcdn.com | Banderas en tiempo real |
| StatsBomb Open Data | Estadísticas reales Copa América / Euro |

---

## ⚠️ Limitaciones conocidas

- Corners y tarjetas son estimaciones proxy — el CSV no contiene datos reales de corners, faltas ni tarjetas.
- No hay datos minuto a minuto; el perfil de juego reemplaza al momentum real.
- Las probabilidades de título no contemplan lesiones, convocatorias ni contexto de fixture real.

---

## 🗺️ Roadmap

- [x] Deploy en Streamlit Cloud
- [ ] API REST con FastAPI para exponer predicciones
- [ ] Integración con API deportiva en tiempo real
- [ ] Exportar reportes PDF por equipo o partido
- [ ] Guardar histórico de simulaciones entre sesiones
- [ ] Dataset real de corners, tarjetas y faltas

---

## 👤 Autor

**Lucas Barrionuevo**  
📧 lucasbarrionuevo374@gmail.com  
🎓 Administración de Empresas — Universidad Empresarial Siglo 21, Córdoba, Argentina  
💼 Data Analytics — Power BI · SQL · Python · BigQuery · Streamlit · AppSheet

---

## 📄 Licencia

MIT License — libre para usar, modificar y distribuir con atribución.

---

<div align="center">
<i>Construido con Python, datos reales y pasión por el fútbol y los datos.</i>
</div>
