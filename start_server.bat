@echo off
echo.
echo ========================================
echo   Kallanum Policum Game Server
echo ========================================
echo.
echo Starting Django Channels ASGI server...
echo Server will be available at: http://127.0.0.1:8000/
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Run the Daphne server
daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application
pause
