@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo               MailTrace AI - Starting All Services
echo ========================================================
echo.

echo [1/3] Starting FastAPI Backend on Port 8000...
start "MailTrace - Backend (Port 8000)" /D "%~dp0backend" cmd /k "python -m uvicorn app.main:app --reload --port 8000"

ping 127.0.0.1 -n 3 > nul

echo [2/3] Starting User Webmail Dashboard on Port 3000...
start "MailTrace - User Webmail (Port 3000)" /D "%~dp0" cmd /k "npm run dev:user"

ping 127.0.0.1 -n 2 > nul

echo [3/3] Starting Security Gateway Dashboard on Port 3001...
start "MailTrace - Security Gateway (Port 3001)" /D "%~dp0" cmd /k "npm run dev:security"

echo.
echo Waiting for servers to initialize...
ping 127.0.0.1 -n 4 > nul

echo Opening both dashboards in your browser...
start "" "http://localhost:3000"
start "" "http://localhost:3001"

echo.
echo ========================================================
echo All services are running and opened in your browser!
echo.
echo   * User Webmail:      http://localhost:3000
echo   * Security Gateway:  http://localhost:3001
echo   * Backend API:       http://localhost:8000/docs
echo.
echo Note: Keep the command windows open while working.
echo ========================================================
echo.
pause
