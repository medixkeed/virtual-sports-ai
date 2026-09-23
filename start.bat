@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   Virtual Sports AI - Starting...
echo ============================================

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python not found. Install Python 3.11+ from https://www.python.org/downloads/
  pause
  exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js not found. Install LTS from https://nodejs.org/
  echo        Then restart Cursor/terminal so PATH updates.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv backend\.venv
  if errorlevel 1 (
    echo Failed to create venv.
    pause
    exit /b 1
  )
)

echo Installing backend dependencies...
backend\.venv\Scripts\python.exe -m pip install -q --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -q -r backend\requirements.txt
if errorlevel 1 (
  echo Backend pip install failed.
  pause
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo Installing frontend dependencies...
  pushd frontend
  call npm install
  if errorlevel 1 (
    echo Frontend npm install failed.
    popd
    pause
    exit /b 1
  )
  popd
)

echo Starting backend on http://127.0.0.1:8001 ...
start "VSA Backend" cmd /k "cd /d %~dp0backend && set DATA_PROVIDER=betpawa && ..\\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001"

timeout /t 3 /nobreak >nul

echo Starting frontend on http://127.0.0.1:5173 ...
start "VSA Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo   App URLs:
echo   Frontend: http://127.0.0.1:5173
echo   API docs: http://127.0.0.1:8001/docs
echo   Admin:    admin@virtualsports.ai / Admin123!
echo ============================================
echo Close the Backend/Frontend windows or run stop.bat to stop.
pause
