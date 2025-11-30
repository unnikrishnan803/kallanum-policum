@echo off
echo ==========================================
echo 🎮 Kallanum Policum - Auto Setup & Run
echo ==========================================

echo.
echo [1/4] 📦 Making Migrations...
python manage.py makemigrations game
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to make migrations. Please check your python installation.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/4] 🗄️ Applying Migrations...
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to migrate database.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/4] 🎭 Setting up Game Roles...
python setup_roles.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to setup roles.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [4/4] 🚀 Starting Server...
echo.
echo Server will be available at: http://127.0.0.1:8000/
echo Press Ctrl+C to stop.
echo.

daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application
