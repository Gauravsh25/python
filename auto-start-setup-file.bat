@echo off
REM ===== AUTO-START SCREEN RECORDER SETUP =====
REM This batch file sets up the screen recorder to start automatically when user logs in

echo Setting up Auto-Start Screen Recorder...
echo.

REM Get current directory
set CURRENT_DIR=%~dp0
set EXE_PATH=%CURRENT_DIR%screen_recorder.exe

REM Check if executable exists
if not exist "%EXE_PATH%" (
    echo ERROR: screen_recorder.exe not found in current directory!
    echo Please make sure the executable is in the same folder as this batch file.
    pause
    exit /b 1
)

echo Found executable: %EXE_PATH%
echo.

REM Create registry entry for auto-start
echo Adding to Windows startup registry...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "ScreenRecorder" /t REG_SZ /d "\"%EXE_PATH%\"" /f

if %ERRORLEVEL% == 0 (
    echo SUCCESS: Screen recorder added to startup!
    echo.
    echo The screen recorder will now start automatically when you log in.
    echo.
    echo IMPORTANT NOTES:
    echo - Recording starts 30 seconds after login
    echo - Recordings are saved to D:\ScreenRecordings\[Username]\
    echo - Logs are saved to D:\ScreenRecordings\Logs\
    echo - If D: drive is not available, files are saved to Documents folder
    echo.
    echo To REMOVE auto-start, run: remove_autostart.bat
) else (
    echo ERROR: Failed to add to startup registry!
    echo Please run this batch file as Administrator.
)

echo.
pause
