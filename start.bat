@echo off
chcp 65001 >nul
title 景区二消产品搜罗平台

echo ================================================
echo   景区二消产品搜罗平台 v1.0
echo ================================================
echo.

:: 检测 Python
set PYTHON_PATH=
for %%p in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Python312\python.exe"
    "python.exe"
) do (
    if exist %%p (
        set PYTHON_PATH=%%~p
        goto :python_found
    )
)

:python_found
if "%PYTHON_PATH%"=="" (
    echo [错误] 未找到 Python！请安装 Python 3.12
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [Python] %PYTHON_PATH%

:: 安装后端依赖（如需要）
echo [检查] 后端依赖...
%PYTHON_PATH% -c "import fastapi, uvicorn, sqlalchemy, bcrypt, httpx, bs4" 2>nul
if errorlevel 1 (
    echo [安装] 正在安装后端依赖...
    %PYTHON_PATH% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
)

:: 启动后端服务
echo [启动] 后端服务 http://localhost:8000
start "景区投资-后端" %PYTHON_PATH% backend\main.py

:: 等待后端启动
echo [等待] 等待后端启动...
timeout /t 3 /nobreak >nul

:: 检测 Node.js
where node >nul 2>nul
if errorlevel 1 (
    echo [警告] 未找到 Node.js，跳过前端开发服务器
    echo [提示] 请直接在浏览器打开 http://localhost:8000/docs 使用API
) else (
    :: 安装前端依赖（如需要）
    if not exist "frontend\node_modules" (
        echo [安装] 正在安装前端依赖...
        cd frontend
        call npm install
        cd ..
    )

    :: 启动前端开发服务器
    echo [启动] 前端服务 http://localhost:5173
    cd frontend
    start "景区投资-前端" npx vite --host 0.0.0.0
    cd ..
)

echo.
echo ================================================
echo   启动完成！
echo   后端: http://localhost:8000
echo   前端: http://localhost:5173
echo   API文档: http://localhost:8000/docs
echo.
echo   📱 手机访问：
echo      确保手机和电脑在同一WiFi下
echo      查看电脑IP地址，手机浏览器访问：
echo      http://你的电脑IP:5173
echo      Chrome浏览器会自动提示"添加到桌面"
echo ================================================
echo.
echo 按任意键停止所有服务...
pause >nul

:: 清理进程
taskkill /f /fi "WINDOWTITLE eq 景区投资*" >nul 2>nul
echo 服务已停止
