@echo off
chcp 65001 >nul
title 景区 - 公网

set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYTHON_PATH%" set PYTHON_PATH=C:\Python312\python.exe
if not exist "%PYTHON_PATH%" (echo Python not found & pause & exit /b 1)

:: Build frontend if needed
if not exist "frontend\dist\index.html" (
    cd frontend & call npm install & call npx vite build & cd ..
)

:: Kill old processes
taskkill /f /fi "WINDOWTITLE eq 景区*" >nul 2>nul

:: Start backend in background
start "景区-后端" /MIN %PYTHON_PATH% -c "from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

timeout /t 4 /nobreak >nul

:: Start tunnel
echo.
echo ======================================
echo  正在创建公网隧道（约10秒）...
echo  获取URL后填入手机APP "服务器地址"
echo ======================================
npx localtunnel --port 8000
pause
