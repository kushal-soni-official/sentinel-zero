@echo off
echo ===================================================
echo Starting Sentinel Zero - Dashboard ^& Triage Server
echo ===================================================
echo.
echo Launching uvicorn server on http://localhost:8001...
echo.
echo [NOTE] Browser will open automatically in 3 seconds once server is ready.
echo [NOTE] Press Ctrl+C to stop the server.
echo.
start /B python app.py
timeout /t 3 /nobreak > nul
start http://localhost:8001
echo.
echo Dashboard launched. Server is running in this window.
pause
