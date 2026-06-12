# FIFA 2026 Predictor AI

## Resumen
Aplicacion Streamlit premium para simulacion del Mundial 2026 con estetica FIFA-style, dashboard oscuro, probabilidades visuales y motor Monte Carlo.

## Modelo
- Base ML: RandomForest entrenado con features del dataset de selecciones.
- Capa de calibracion: suaviza probabilidades extremas y pondera ranking FIFA actual, forma, ataque, defensa, posesion y experiencia.
- Simulador Match AI: ejecuta Monte Carlo usando el numero de simulaciones elegido en el slider.
- Bracket: muestra probabilidad de avanzar, por eso cada cruce suma 100%.

## Features usadas
- Ranking FIFA
- Goles a favor y contra
- Win rate
- PPG
- Clean sheets
- Posesion
- Tiros y tiros al arco
- Pases
- Confederacion
- Experiencia mundialista
- Localia controlada para Mexico, Canada y Estados Unidos

## Ajustes aplicados
- Reduccion de sesgo para anfitriones.
- Mayor peso al ranking FIFA para equipos elite como Francia.
- Reduccion de upside para Japon/AFC y Marruecos en probabilidades de titulo.
- Match overview con marcador probable, xG, ambos anotan, primer gol y total de goles.
- Fondo visual inspirado en Mundial 2026 usando logo provisto.

## Limitaciones
- Corners y tarjetas son estimaciones proxy porque el CSV actual no trae datos reales de corners, faltas o tarjetas.
- No hay datos minuto a minuto reales; por eso se reemplazo Momentum por Perfil de Juego.

## Como ejecutar
```powershell
cd "C:\Users\malvi\Downloads\MUNDIAL DATOS"
.\venv\Scripts\python.exe -m streamlit run app.py
```

## Futuras mejoras
- Agregar dataset real de corners, tarjetas, faltas y arbitros.
- Guardar historico de simulaciones.
- Exportar reportes PDF por partido.
- Integrar API deportiva real para lesiones, convocatorias y fixtures actualizados.
