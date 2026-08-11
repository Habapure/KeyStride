@echo off
chcp 65001 >nul
title KeyStride Build

setlocal enabledelayedexpansion

cd /d "%~dp0"

:: 查找 Python
set "PY="
if exist "D:\python\python.exe" set "PY=D:\python\python.exe"
if not defined PY if exist "E:\python\python.exe" set "PY=E:\python\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python314\python.exe" set "PY=%LocalAppData%\Programs\Python\Python314\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PY=%LocalAppData%\Programs\Python\Python311\python.exe"

if not defined PY (
    echo [ERROR] Python 未找到！
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════╗
echo ║   键步如飞 KeyStride — Build            ║
echo ╚══════════════════════════════════════════╝
echo.
echo  Python: %PY%
echo.

:: 安装依赖
"%PY%" -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] 依赖安装失败
    pause
    exit /b 1
)

:: 清理旧构建
if exist "dist\KeyStride.exe" del "dist\KeyStride.exe"
if exist "build" rmdir /s /q "build" 2>nul
if exist "KeyStride.spec" del "KeyStride.spec"

echo.
echo 正在打包，请稍候...
echo.

"%PY%" -m PyInstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "KeyStride" ^
    --icon "icons\app.ico" ^
    --add-data "icons;icons" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "PySide6.QtGui" ^
    --clean ^
    --noconsole ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] 打包失败！
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════
echo  ✔ 打包成功！
echo.
echo  输出文件: %~dp0dist\KeyStride.exe
echo.
echo  文件大小：
for %%I in ("%~dp0dist\KeyStride.exe") do @echo   %%~zI 字节
echo.
echo  使用方法：
echo   1. 把 KeyStride.exe 放到任意文件夹
echo   2. 双击运行（会在同目录生成 config.json）
echo   3. 右键右下角托盘图标操作
echo.
echo  ⚡ 热键: Ctrl+Shift+V  ·  ESC 中断
echo ═══════════════════════════════════════════

pause
