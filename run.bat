@echo off
cd /d "%~dp0"

set "PY="
set "PYW="
if exist "D:\python\python.exe" set "PY=D:\python\python.exe" & set "PYW=D:\python\pythonw.exe"
if not defined PY if exist "E:\python\python.exe" set "PY=E:\python\python.exe" & set "PYW=E:\python\pythonw.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python314\python.exe" set "PY=%LocalAppData%\Programs\Python\Python314\python.exe" & set "PYW=%LocalAppData%\Programs\Python\Python314\pythonw.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PY=%LocalAppData%\Programs\Python\Python313\python.exe" & set "PYW=%LocalAppData%\Programs\Python\Python313\pythonw.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY=%LocalAppData%\Programs\Python\Python312\python.exe" & set "PYW=%LocalAppData%\Programs\Python\Python312\pythonw.exe"
if not defined PY if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PY=%LocalAppData%\Programs\Python\Python311\python.exe" & set "PYW=%LocalAppData%\Programs\Python\Python311\pythonw.exe"

if not defined PY (
  echo [ERROR] python.exe not found
  pause
  exit /b 1
)

"%PY%" -c "import pyperclip,pynput,pystray,PIL" 2>error.log
if errorlevel 1 (
  echo [ERROR] missing deps, installing...
  "%PY%" -m pip install -r requirements.txt
  if errorlevel 1 (
    type error.log
    pause
    exit /b 1
  )
)

echo.
echo  Starting KeyStride...
echo  - NO console window will stay open. That is normal.
echo  - Look for BLUE tray icon near the clock (click ^ if hidden).
echo  - Hotkey: Ctrl+Shift+V
echo  - Right-click tray icon -^> Exit to quit.
echo.

if exist "%PYW%" (
  start "" "%PYW%" "%~dp0main.py"
) else (
  start "" "%PY%" "%~dp0main.py"
)

ping -n 4 127.0.0.1 >nul

REM Verify process still alive
"%PY%" -c "import time,sys; from pathlib import Path; p=Path(r'%~dp0runtime.log'); time.sleep(0.5); t=p.read_text(encoding='utf-8') if p.exists() else ''; print(t[-500:] if t else 'no runtime.log yet'); sys.exit(0 if ('tray: icon visible' in t or 'app: start' in t or 'already running' in t) else 1)"
if errorlevel 1 (
  echo.
  echo [WARN] App may have failed. See runtime.log / error.log
  pause
) else (
  echo OK - app is running in tray.
  ping -n 3 127.0.0.1 >nul
)
exit /b 0
