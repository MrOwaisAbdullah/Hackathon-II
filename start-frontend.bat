@echo off
REM TeamFlow Frontend Service Launcher for Windows
REM This script launches the Minikube service tunnel for the frontend

echo ========================================
echo TeamFlow - Frontend Service Launcher
echo ========================================
echo.

REM Check if WSL is available
where wsl.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WSL not found. Please install WSL2.
    pause
    exit /b 1
)

echo Starting TeamFlow frontend service tunnel...
echo.
echo Please keep this window OPEN - the service tunnel must stay running.
echo.
echo When ready, open your browser and navigate to the URL shown below.
echo.

REM Execute minikube service command through WSL
wsl.exe ~/.local/bin/minikube service teamflow-frontend -n teamflow

echo.
echo Service tunnel stopped. Press any key to exit...
pause >nul
