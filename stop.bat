@echo off
echo Stopping Virtual Sports AI processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
taskkill /FI "WINDOWTITLE eq VSA Backend*" /F 2>nul
taskkill /FI "WINDOWTITLE eq VSA Frontend*" /F 2>nul
echo Done.
pause
