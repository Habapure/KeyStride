@echo off
chcp 65001 >nul
title 创建桌面快捷方式

:: 确认 exe 存在
set "EXE=%~dp0dist\KeyStride.exe"
if not exist "%EXE%" (
    echo [ERROR] KeyStride.exe 未找到，请先运行 build.bat
    pause
    exit /b 1
)

:: 获取桌面路径
set "DESKTOP=%USERPROFILE%\Desktop"

:: 用 PowerShell 创建快捷方式
powershell -Command ^
    $ws = New-Object -ComObject WScript.Shell; ^
    $sc = $ws.CreateShortcut("%DESKTOP%\键步如飞·KeyStride.lnk"); ^
    $sc.TargetPath = "%EXE%"; ^
    $sc.WorkingDirectory = "%~dp0dist"; ^
    $sc.IconLocation = "%EXE%, 0"; ^
    $sc.Description = "键步如飞 KeyStride — 复制文本后模拟真人逐字输入"; ^
    $sc.Save(); ^
    Write-Host "快捷方式已创建到桌面"

if errorlevel 1 (
    echo [ERROR] 创建快捷方式失败
) else (
    echo.
    echo ═══════════════════════════════════════
    echo  ✔ 桌面快捷方式已创建！
    echo.
    echo  双击桌面 "键步如飞·KeyStride" 即可启动
    echo  热键: Ctrl+Shift+V  ·  ESC 中断
    echo ═══════════════════════════════════════
)

pause
