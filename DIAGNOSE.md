# 🩺 Connectivity & Database Diagnosis

If you are seeing "Disconnected" or having issues, follow these steps.

## Step 1: Check Database Status

Run this script to see if your database is up to date:
```bash
python check_db.py
```

**If it says "Missing tables" or "Missing columns":**
You MUST run migrations:
```bash
python manage.py makemigrations game
python manage.py migrate
```

## Step 2: Check Server Logs

Look at the terminal where you are running `daphne`.
I have added detailed error logging.

**If you see:**
- `❌ Error in connect`: The server is crashing when you try to join. Likely a DB issue.
- `❌ Error in receive`: The server crashed while processing a message.

## Step 3: Verify Server Port

Ensure you are running the server with Daphne on port 8000:
```bash
daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application
```

And accessing the game at: `http://127.0.0.1:8000/`

**DO NOT** use `runserver` or open the HTML file directly.

## Step 4: Reset Database (Last Resort)

If nothing works, you can reset the database completely:

1. Delete `db.sqlite3` file
2. Delete `game/migrations/000*.py` (keep `__init__.py`)
3. Run:
   ```bash
   python manage.py makemigrations game
   python manage.py migrate
   python setup_roles.py
   ```
