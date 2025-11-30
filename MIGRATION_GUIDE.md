# 🔄 Migration Guide

I have updated the game logic to include:
- ✅ **Timer System** (60s countdown)
- ✅ **Interrogation Logic** (Pause timer)
- ✅ **Advanced Scoring** (Win/Loss points)
- ✅ **Role Descriptions**
- ✅ **Game Over / Podium Screen**

## ⚠️ Action Required: Update Database

Since the database models have changed, you need to update your database schema.

### Step 1: Create Migrations
Run this command in your terminal:
```bash
python manage.py makemigrations game
```

### Step 2: Apply Migrations
Run this command:
```bash
python manage.py migrate
```

### Step 3: Update Roles
Run the setup script to update the roles with new descriptions and points:
```bash
python manage.py shell < setup_roles.py
```
*Or if that doesn't work:*
```bash
python setup_roles.py
```
*(Make sure Django settings are loaded if running directly)*

### Step 4: Restart Server
Stop the running server (Ctrl+C) and start it again:
```bash
daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application
```

## 🎮 What's New?

1. **Timer**: A 60-second timer now runs during the game.
2. **Interrogation**: The Police player has an "Interrogate" button that pauses the timer for 10 seconds.
3. **Descriptions**: Players now see a description of their role on the chit.
4. **Game Over**: After 5 rounds (default), the game ends and shows a Podium with Gold, Silver, and Bronze winners.
