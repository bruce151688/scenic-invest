@echo off
chcp 65001 >nul
title 构建 Android APK

echo ================================================
echo   景区投资 APK 构建脚本
echo   需要: Java JDK 17+ 和 Android SDK
echo ================================================
echo.

:: 检查 JAVA_HOME
if "%JAVA_HOME%"=="" (
    echo [提示] 未设置 JAVA_HOME
    echo 尝试自动检测...
    for %%p in (
        "C:\Users\%USERNAME%\jdk17\jdk-17.0.13+11"
        "C:\Program Files\Java\jdk-17"
    ) do (
        if exist %%p (
            set JAVA_HOME=%%~p
            echo [检测] JAVA_HOME = %%p
            goto :jdk_found
        )
    )
    echo [错误] 未找到 JDK！请安装 JDK 17
    echo 下载: https://adoptium.net/download/
    pause
    exit /b 1
)

:jdk_found
set PATH=%JAVA_HOME%\bin;%PATH%

:: 检查 ANDROID_HOME
if "%ANDROID_HOME%"=="" (
    set ANDROID_HOME=C:\Users\%USERNAME%\Android
    echo [设置] ANDROID_HOME = %ANDROID_HOME%
)

:: 检查 Android SDK
if not exist "%ANDROID_HOME%\platforms" (
    echo.
    echo ================================================
    echo [重要] Android SDK 未安装！
    echo.
    echo 请按以下步骤操作:
    echo 1. 下载 Android Studio:
    echo    https://developer.android.com/studio
    echo 或
    echo 2. 只下载命令行工具:
    echo    https://developer.android.com/studio#command-line-tools-only
    echo.
    echo 3. 安装后设置环境变量:
    echo    set ANDROID_HOME=C:\Users\你的用户名\AppData\Local\Android\Sdk
    echo.
    echo 4. 使用 sdkmanager 安装必要组件:
    echo    sdkmanager "platforms;android-35" "build-tools;35.0.0"
    echo ================================================
    echo.
    echo 跳过APK构建，改为生成 PWA 部署包...
)

:: 检查前端是否构建
if not exist "frontend\dist\index.html" (
    echo [构建] 前端...
    cd frontend
    if not exist "node_modules" ( call npm install )
    call npx vite build
    cd ..
)

:: 使用 Capacitor 构建
if exist "android-app\android\gradlew.bat" (
    echo [构建] 开始 Android APK 构建...
    cd android-app

    :: 复制最新前端
    if exist "www" ( rmdir /s /q www )
    xcopy /e /y ..\frontend\dist www\

    :: 同步到 Android
    call npx cap sync android

    :: 构建 APK
    cd android
    call gradlew.bat assembleDebug

    :: 查找生成的 APK
    echo.
    echo [完成] 查找 APK 文件...
    for /r %%f in (*.apk) do (
        echo 找到: %%f
        copy "%%f" "%USERPROFILE%\Desktop\景区投资.apk"
        echo 已复制到桌面: 景区投资.apk
    )
    cd ..\..
) else (
    echo [跳过] Capacitor 项目不存在
)

echo.
echo ================================================
echo 完成！如果构建成功，APK 在桌面上。
echo 如果失败了，请确认 Android SDK 已正确安装。
echo ================================================
pause
