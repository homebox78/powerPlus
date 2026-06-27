@echo off
REM powerPlus add-in installer (per-user, no admin required)
set "DEST=%LOCALAPPDATA%\powerPlus"
if not exist "%DEST%" mkdir "%DEST%"
copy /Y "%~dp0manifest.xml" "%DEST%\manifest.xml" >nul
reg add "HKCU\Software\Microsoft\Office\16.0\WEF\Developer" /v "629c04eb-661e-43a4-abc4-21a298eb92db" /t REG_SZ /d "%DEST%\manifest.xml" /f >nul
echo.
echo   ============================================
echo     powerPlus installed.
echo   ============================================
echo.
echo   Please CLOSE and RESTART PowerPoint.
echo   The [powerPlus] button appears on the Home ribbon.
echo   (See the included guide file for Korean instructions.)
echo.
pause
