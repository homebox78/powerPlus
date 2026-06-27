@echo off
REM powerPlus add-in uninstaller
reg delete "HKCU\Software\Microsoft\Office\16.0\WEF\Developer" /v "629c04eb-661e-43a4-abc4-21a298eb92db" /f >nul 2>&1
rmdir /S /Q "%LOCALAPPDATA%\powerPlus" >nul 2>&1
echo.
echo   powerPlus removed. Please restart PowerPoint.
echo.
pause
