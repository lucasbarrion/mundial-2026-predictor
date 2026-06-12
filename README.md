# 🏆 FIFA World Cup 2026 — AI Predictor

<div align="center">

![FIFA 2026](https://img.shields.io/badge/FIFA-World%20Cup%202026-gold?style=for-the-badge&logo=fifa&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-RandomForest-orange?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge)

**Aplicación web de predicción del Mundial 2026 con inteligencia artificial.**  
Motor Random Forest + simulaciones Monte Carlo + visualizaciones premium estilo Sofascore / Opta Analyst.

[🚀 Ver App en vivo](#) · [📊 Dataset](#dataset) · [🤖 Modelo IA](#modelo-de-ia) · [⚙️ Instalación](#instalación)

</div>

---

## ¿Qué es este proyecto?

FIFA World Cup 2026 AI Predictor es una aplicación web interactiva que combina **machine learning**, **datos reales de selecciones nacionales** y **visualizaciones de nivel profesional** para simular y predecir el torneo más grande del fútbol.

El sistema analiza **48 selecciones clasificadas** usando 17 métricas reales (ranking FIFA, goles por partido, posesión, win rate, clean sheets, PPG y más) para calcular probabilidades de victoria en cada partido, simular la fase de grupos completa y proyectar el bracket eliminatorio hasta el campeón.

---

## ✨ Funcionalidades

| Sección | Descripción |
|---|---|
| ⚽ **Simulador Match AI** | Simulá cualquier cruce con probabilidades, xG estimado, heatmap de marcadores y análisis táctico |
| 🏟️ **Fase de Grupos** | Tablas estilo FIFA con estados de clasificación, diferencia de gol y probabilidades partido a partido |
| 🧠 **Predicción IA** | Ranking de candidatos al título, sorpresa del torneo, posible decepción y final más probable |
| 🗺️ **Simulador de Torneo** | Bracket completo Round of 32 → Final con probabilidades por llave y campeón predicho |
| 📊 **Análisis de Equipos** | Perfil avanzado por selección: radar de estilo, métricas normalizadas y comparación 1 vs 1 |

---

## 🗂️ Estructura del proyecto

```
mundial-2026-predictor/
│
├── app.py                     # ⭐ Archivo principal — Streamlit app
├── components.py              # Componentes visuales reutilizables (navbar, hero, cards, flags)
├── charts.py                  # Gráficos Plotly (radar, donut, gauge, heatmap, barras)
├── styles.css                 # Diseño premium: glassmorphism, colores FIFA, tipografías
├── requirements.txt           # Dependencias del proyecto
│
├── DATA/
│   ├── equipos.csv            # Base de datos de las 48 selecciones (17 métricas por equipo)
│   └── fixture_grupos.csv     # Fixture oficial fase de grupos (72 partidos)
│
├── MODELO/
│   ├── bracket.py             # Grupos, fixtures y cruces oficiales del Mundial 2026
│   ├── simulador.py           # Simulador auxiliar de consola
│   ├── train_model.py         # Script para entrenar el modelo desde cero
│   └── modelo_mundial.pkl     # Modelo Random Forest entrenado
│
└── assets/                    # Logos e imágenes
```

---

## ⚙️ Cómo funciona el ecosistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        VISUAL STUDIO CODE                        │
│                                                                   │
│   app.py ──────────────────────────────────────────────────────  │
│     │                                                             │
│     ├── components.py     →  navbar, hero, cards, banderas        │
│     ├── charts.py         →  radar, donut, heatmap, gauges        │
│     ├── styles.css        →  diseño premium glassmorphism         │
│     │                                                             │
│     ├── DATA/equipos.csv           →  estadísticas reales         │
│     ├── MODELO/modelo_mundial.pkl  →  predicciones ML             │
│     └── MODELO/bracket.py         →  cruces oficiales FIFA        │
│                                                                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
              Streamlit Server
                        │
                        ▼
           localhost:8501 / URL pública
```

**En simple:**
- **`app.py`** es el cerebro — conecta todo y renderiza la interfaz
- **`DATA/equipos.csv`** aporta las estadísticas reales de cada selección
- **`modelo_mundial.pkl`** predice probabilidades de resultado
- **`bracket.py`** conoce los grupos y cruces oficiales del Mundial
- **`components.py`** y **`charts.py`** dan el look premium visual

---

## 📊 Dataset — `DATA/equipos.csv`

Base de datos de las **48 selecciones clasificadas** con estadísticas reales 2023–2026.

**Fuentes reales utilizadas:**
- 🌍 `martj42/international_results` (GitHub) — 49.000+ partidos internacionales
- ⚽ StatsBomb Open Data — Copa América 2024, UEFA Euro 2024, AFCON 2023

| Columna | Descripción |
|---|---|
| `fifa_ranking` | Ranking FIFA oficial |
| `avg_goals_scored` | Goles por partido (2023–2026) |
| `avg_goals_conceded` | Goles recibidos por partido |
| `win_pct / draw_pct / loss_pct` | % de resultados reales |
| `clean_sheet_pct` | % de partidos sin goles en contra |
| `ppg` | Puntos por partido |
| `avg_possession` | Posesión promedio % |
| `avg_shots_pg` | Disparos por partido |
| `avg_shots_on_target_pg` | Disparos al arco por partido |
| `avg_passes_pg` | Pases por partido |
| `world_cups_won` | Copas del Mundo ganadas históricamente |
| `is_host` | 1 si es sede (USA, México, Canadá) |
| `is_debut` | 1 si debuta en el Mundial 2026 |

---

## 🤖 Modelo de IA

**Algoritmo:** Random Forest Classifier (scikit-learn)  
**Entrenamiento:** 8.000 partidos sintéticos generados con lógica de fortaleza competitiva  
**Features:** 17 métricas por equipo  
**Salida:** Probabilidades para 3 clases — Victoria / Empate / Derrota  

### Importancia de features

| Feature | Importancia |
|---|---|
| `fifa_ranking` | 35.5% |
| `appearances` | 16.3% |
| `goal_diff` | 8.7% |
| `ppg` | 6.5% |
| `win_pct` | 5.1% |
| `avg_passes_pg` | 4.1% |
| `avg_possession` | 3.4% |
| otros 10 features | 20.4% |

### Calibración adicional

Las probabilidades crudas del modelo se calibran con reglas de negocio:

- 🏠 **Ventaja local** → +3 pts de fortaleza (USA, México, Canadá)
- 🌟 **Debut** → -4 pts de fortaleza (Cape Verde, Curaçao, Jordan, Uzbekistan)
- 🌍 **Confederación** → UEFA y CONMEBOL tienen +1.5 pts históricos
- 📉 **Poca experiencia** → equipos con menos de 3 mundiales reciben penalización
- 🔝 **Top 5 FIFA** → piso mínimo de probabilidad en cualquier cruce

---

## 🏟️ Bracket oficial FIFA 2026

El sistema implementa el formato oficial del Mundial 2026:

- **12 grupos** (A–L) con 4 equipos cada uno → 72 partidos
- **Clasifican:** Top 2 de cada grupo (24) + 8 mejores terceros = **32 equipos**
- **Eliminación directa:** Round of 32 → R16 → Cuartos → Semis → Final

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

Abrí **http://localhost:8501** en tu navegador.

---

## 🛠️ Stack tecnológico

| Tecnología | Uso |
|---|---|
| Python 3.11+ | Lenguaje principal |
| Streamlit | Framework web |
| Scikit-learn | Modelo Random Forest |
| Pandas + NumPy | Procesamiento de datos |
| Plotly | Visualizaciones interactivas |
| CSS / HTML | Diseño premium personalizado |

---

## 🗺️ Roadmap

- [ ] Deploy público en Streamlit Cloud
- [ ] API REST con FastAPI para exponer predicciones
- [ ] Simulación Monte Carlo con 10.000+ torneos
- [ ] Integración con API deportiva en tiempo real
- [ ] Exportar reportes PDF por equipo o partido
- [ ] Modo apuestas con value picks y cuotas estimadas

---

## 👤 Autor

**Lucas Barrionuevo**  
📧 lucasbarrionuevo374@gmail.com  


---

## 📄 Licencia

MIT License — libre para usar, modificar y distribuir con atribución.

---

<div align="center">
<i>Construido con Python, datos reales y pasión por el fútbol y los datos.</i>
</div>
