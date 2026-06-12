Set-Location "C:\Users\malvi\Downloads\MUNDIAL DATOS"

Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object { $_.CommandLine -like '*streamlit run*app.py*' -and $_.CommandLine -like '*MUNDIAL DATOS*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Start-Process "http://127.0.0.1:8501"

& ".\venv\Scripts\python.exe" -m streamlit run app.py `
  --server.address 127.0.0.1 `
  --server.port 8501 `
  --server.headless false `
  --server.enableCORS false `
  --server.enableXsrfProtection false `
  --browser.gatherUsageStats false
