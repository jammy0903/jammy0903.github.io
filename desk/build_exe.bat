@echo off
rem Build desk.exe (single file, no console window).
rem Needs PyInstaller:  py -m pip install pyinstaller
rem ASCII only on purpose - cmd reads .bat in the ANSI codepage.

cd /d "%~dp0"

where py >nul 2>&1 && (set PY=py) || (set PY=python)

%PY% make_icon.py || goto :fail
%PY% -m PyInstaller --onefile --noconsole --name desk --icon icon.ico ^
     --clean --noconfirm desk.py || goto :fail

echo.
echo Done: dist\desk.exe
echo Copy it anywhere you like. It needs no Python installed.
pause
exit /b

:fail
echo.
echo Build failed. If PyInstaller is missing:
echo     py -m pip install pyinstaller
pause
exit /b 1
