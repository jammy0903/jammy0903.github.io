@echo off
rem Launch desk on Windows. Double-click this file.
rem Uses pythonw/pyw so no black console window appears.
rem ASCII only on purpose: cmd reads .bat in the ANSI codepage (949 here),
rem so UTF-8 Korean text in a .bat comes out as garbage and can break parsing.

cd /d "%~dp0"

where pyw >nul 2>&1 && (
    start "" pyw "%~dp0desk.py"
    exit /b
)

where pythonw >nul 2>&1 && (
    start "" pythonw "%~dp0desk.py"
    exit /b
)

where python >nul 2>&1 && (
    start "" python "%~dp0desk.py"
    exit /b
)

echo Python not found.
echo Install from https://www.python.org/downloads/
echo and make sure "Add python.exe to PATH" is checked.
pause
