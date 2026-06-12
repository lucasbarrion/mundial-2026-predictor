@echo off
title Mundial 2026 Predictor AI
cd /d "C:\Users\malvi\Downloads\MUNDIAL DATOS"

echo Cerrando instancias viejas de Streamlit...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process -Filter \"name = 'python.exe'\" | Where-Object { $_.CommandLine -like '*streamlit run*app.py*' -and $_.CommandLine -like '*MUNDIAL DATOS*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>nul

echo.
echo Abriendo Mundial 2026 Predictor AI...
echo URL: http://127.0.0.1:8501
echo.
echo Si el navegador no abre solo, copia y pega esta URL:
echo http://127.0.0.1:8501
echo.

start "" "http://127.0.0.1:8501"
.\venv\Scripts\python.exe -m streamlit run app.py ^
  --server.address 127.0.0.1 ^
  --server.port 8501 ^
  --server.headless false ^
  --server.enableCORS false ^
  --server.enableXsrfProtection false ^
  --browser.gatherUsageStats false

pause
