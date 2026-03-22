@echo off
echo Setting up Converter command...

:: Get Python Scripts directory
for /f "tokens=*" %%i in ('where pip') do set PIP_PATH=%%i
for %%i in ("%PIP_PATH%") do set SCRIPTS_DIR=%%~dpi

:: Create batch file
echo @echo off > "%SCRIPTS_DIR%Converter.bat"
echo python "%~dp0..\..\..\..\Desktop\file-converter\main.py" %%* >> "%SCRIPTS_DIR%Converter.bat"

echo Done! You can now run "Converter" from any terminal.
pause
