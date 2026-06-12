🏆 FIFA World Cup 2026 — AI Predictor

<div align="center">
Mostrar imagen
Mostrar imagen
Mostrar imagen
Mostrar imagen
Mostrar imagen

Aplicación web de predicción del Mundial 2026 con inteligencia artificial.

Motor Random Forest + simulaciones Monte Carlo + visualizaciones premium estilo Sofascore / Opta Analyst.

🚀 Ver App en vivo · 🤖 Modelo IA · ⚙️ Instalación

</div>

¿Qué es este proyecto?

FIFA World Cup 2026 AI Predictor es una aplicación web interactiva que combina machine learning, datos reales de selecciones nacionales y visualizaciones de nivel profesional para simular y predecir el torneo más grande del fútbol.

El sistema analiza 48 selecciones clasificadas usando métricas reales (ranking FIFA, goles por partido, posesión, win rate, clean sheets, PPG y más) para calcular probabilidades de victoria en cada partido, simular la fase de grupos completa y proyectar el bracket eliminatorio hasta el campeón.


✨ Funcionalidades

SecciónDescripción⚽ Simulador Match AISimulá cualquier cruce con Monte Carlo, probabilidades en 90', xG estimado, heatmap de marcadores, corners y tarjetas proyectadas, clean sheet gauge y análisis de perfil de juego🏟️ Fase de GruposTablas estilo FIFA con estados de clasificación, diferencia de gol y probabilidades partido a partido🧠 Predicción IARanking de candidatos al título, sorpresa del torneo y barra de probabilidades comparativa entre los 12 principales🗺️ Simulador de TorneoBracket completo Round of 32 → Final con probabilidades por llave y campeón predicho📊 Análisis de EquiposPerfil avanzado por selección: radar de estilo, métricas normalizadas (Power Rating, Win Rate, PPG, goles) y comparación contra el promedio global


🗂️ Estructura del proyecto

mundial-2026-predictor/
│
├── app.py                     # ⭐ Archivo principal — Streamlit app
├── components.py              # Componentes visuales reutilizables (navbar, hero, cards, flags)
├── charts.py                  # Gráficos Plotly (radar, donut, gauge, heatmap, barras, style_compare)
├── styles.css                 # Diseño premium: glassmorphism, colores FIFA, tipografías
├── requirements.txt           # Dependencias del proyecto
│
├── DATA/
│   ├── equipos.csv            # Base de datos de las 48 selecciones
│   └── fixture_grupos.csv     # Fixture oficial fase de grupos (72 partidos)
│
├── MODELO/
│   ├── bracket.py             # Grupos, fixtures y cruces oficiales del Mundial 2026
│   ├── simulador.py           # Simulador auxiliar de consola
│   ├── train_model.py         # Script para entrenar el modelo desde cero
│   └── modelo_mundial.pkl     # Modelo Random Forest entrenado
│
└── assets/                    # Logos e imágenes


⚙️ Cómo funciona el ecosistema

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

En simple:


app.py es el cerebro — conecta todo y renderiza la interfaz
DATA/equipos.csv aporta las estadísticas reales de cada selección
modelo_mundial.pkl predice probabilidades de resultado con Random Forest
bracket.py conoce los grupos y cruces oficiales del Mundial
components.py y charts.py dan el look premium visual



📊 Dataset — DATA/equipos.csv

Base de datos de las 48 selecciones clasificadas con estadísticas reales 2023–2026.

ColumnaDescripciónfifa_rankingRanking FIFA oficialavg_goals_scoredGoles por partido (2023–2026)avg_goals_concededGoles recibidos por partidowin_pct / draw_pct / loss_pct% de resultados realesclean_sheet_pct% de partidos sin goles en contrappgPuntos por partidoavg_possessionPosesión promedio %avg_shots_pgDisparos por partidoavg_shots_on_target_pgDisparos al arco por partidoavg_passes_pgPases por partidogoal_diffDiferencia de goles acumuladaappearancesMundiales disputados históricamenteworld_cups_wonCopas del Mundo ganadas históricamenteconfederationConfederación (UEFA, CONMEBOL, AFC, etc.)groupGrupo asignado en el Mundial 2026is_host1 si es sede (USA, México, Canadá)is_debut1 si debuta en el Mundial 2026


🤖 Modelo de IA

Algoritmo: Random Forest Classifier (scikit-learn)

Features: métricas del dataset de selecciones (diferencia entre equipo local y visitante)

Salida: Probabilidades para 3 clases — Victoria (0) / Empate (1) / Derrota (2)

Power Rating

Cada selección recibe un índice calculado en tiempo real como combinación de cuatro dimensiones:

DimensiónPesoVariables usadasAtaque30%avg_goals_scored, avg_shots_on_target_pgDefensa25%avg_goals_conceded, clean_sheet_pctForma25%win_pct, ppgRanking20%fifa_ranking

Calibración de probabilidades

Las probabilidades crudas del modelo pasan por una capa de calibración que combina el output del Random Forest (34%) con un modelo de fortaleza diferencial (66%):


🏠 Ventaja local → ajuste controlado para USA, México y Canadá (máximo +5.5 pts, solo si la ventaja es excesiva)
🌟 Debut → −4 pts de fortaleza (Cape Verde, Curaçao, Jordan, Uzbekistan)
🌍 Confederación → UEFA y CONMEBOL reciben +0.9 pts; AFC −1.2 pts; OFC −3 pts
📉 Poca experiencia → equipos con menos de 3 mundiales reciben penalización adicional
🔝 Top 3 FIFA → piso mínimo de probabilidad garantizado en cualquier cruce (≥30%)
🔢 Top 5 vs fuera del top 10 → piso de 52% de win probability para el favorito


Simulación Monte Carlo

El Simulador Match AI ejecuta hasta 100.000 simulaciones por cruce usando numpy.random.default_rng con seed reproducible, permitiendo variar resultados con el botón de re-simulación sin perder consistencia entre sesiones.


🏟️ Bracket oficial FIFA 2026

El sistema implementa el formato oficial del Mundial 2026:


12 grupos (A–L) con 4 equipos cada uno → 72 partidos en fase de grupos
Clasifican: Top 2 de cada grupo (24) + 8 mejores terceros = 32 equipos
Eliminación directa: Round of 32 → R16 → Cuartos → Semis → Final
Los terceros clasificados se asignan según criterio FIFA (puntos, diferencia de gol, goles a favor)



🚀 Instalación local

bash# 1. Clonar el repositorio
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

O en Windows, ejecutar directamente ABRIR_APP_MUNDIAL.bat.

Abrí http://127.0.0.1:8501 en tu navegador.


🛠️ Stack tecnológico

TecnologíaUsoPython 3.11+Lenguaje principalStreamlitFramework webScikit-learnModelo Random ForestPandas + NumPyProcesamiento de datos y simulacionesPlotlyVisualizaciones interactivas (radar, donut, gauge, heatmap, barras)CSS / HTMLDiseño premium personalizado con glassmorphism


⚠️ Limitaciones conocidas


Corners y tarjetas son estimaciones proxy calculadas desde variables del dataset (shots, posesión, goles concedidos, ranking). El CSV no contiene datos reales de corners, faltas o tarjetas.
No hay datos minuto a minuto; el perfil de juego reemplaza al momentum real.
Las probabilidades de título son orientativas — no contemplan lesiones, convocatorias ni contexto de fixture real.



🗺️ Roadmap


 API REST con FastAPI para exponer predicciones
 Integración con API deportiva en tiempo real (lesiones, convocatorias)
 Exportar reportes PDF por equipo o partido
 Guardar histórico de simulaciones entre sesiones
 Modo apuestas con value picks y cuotas estimadas



👤 Autor

Lucas Barrionuevo

📧 lucasbarrionuevo374@gmail.com

🎓 Administración de Empresas — Universidad Empresarial Siglo 21, Córdoba, Argentina

💼 Data Analytics — Power BI · SQL · Python · BigQuery · Streamlit · AppSheet


📄 Licencia

MIT License — libre para usar, modificar y distribuir con atribución.


<div align="center">
<i>Construido con Python, datos reales y pasión por el fútbol y los datos.</i>
</div>
