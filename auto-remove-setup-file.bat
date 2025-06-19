@echo off
REM ===== REMOVE AUTO-START SCREEN RECORDER =====
REM This batch file removes the screen recorder from auto-start

echo Removing Auto-Start Screen Recorder...
echo.

REM Remove registry entry
echo Removing from Windows startup registry...
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "ScreenRecorder" /f

if %ERRORLEVEL% == 0 (
    echo SUCCESS: Screen recorder removed from startup!
    echo The screen recorder will no longer start automatically.
) else (
    echo ERROR: Failed to remove from startup registry!
    echo The entry may not exist or you may need Administrator privileges.
)

echo.
pause
