@echo off
chcp 65001 >nul
title 景区二消产品搜罗平台 - 生产模式

echo ================================================
echo   景区二消产品搜罗平台 v1.0 (生产模式)
echo   单端口运行: 前后端合一
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
    echo [错误] 未找到 Python！
    pause
    exit /b 1
)

:: 检查前端是否已构建
if not exist "frontend\dist\index.html" (
    echo [警告] 前端未构建！正在构建...
    cd frontend
    if not exist "node_modules" (
        echo [安装] 前端依赖...
        call npm install
    )
    call npx vite build
    cd ..
)

:: 初始化数据
echo [数据] 检查种子数据...
%PYTHON_PATH% -c "from database import SessionLocal, init_db; from models import Product; init_db(); db=SessionLocal(); print(f'产品数: {db.query(Product).count()}'); db.close()"

:: 启动（生产模式 - 直接运行，不开启debug重载）
echo.
echo [启动] http://localhost:8000
echo ================================================
echo.
echo   📱 手机访问 (同WiFi下):
echo      查看电脑IP: 运行 ipconfig
echo      http://你的IP:8000
echo      Chrome打开 -> 菜单 -> 添加到主屏幕
echo.
echo   按 Ctrl+C 停止服务
echo ================================================
echo.

:: 不开启reload的生产模式
%PYTHON_PATH% -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000)"
