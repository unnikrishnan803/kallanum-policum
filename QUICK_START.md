# 🎮 Kallanum Policum - Quick Start Guide

## ✅ Fixes Applied

I've fixed both critical bugs:

1. **✅ Session ID Mismatch** - Role assignments now work correctly
2. **✅ Missing Session ID in Arrest** - Police can now make arrests

## 🚀 How to Run the Game

### Step 1: Activate Virtual Environment (if using one)

If you have a virtual environment:
```bash
# Activate it first (the command depends on how you created it)
# Examples:
.\venv\Scripts\activate          # Windows venv
.\env\Scripts\activate           # Windows env
.\.venv\Scripts\activate         # Windows .venv
```

### Step 2: Install Dependencies

```bash
pip install django channels daphne
```

### Step 3: Setup Database

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Setup game roles (creates the 12 required roles)
python manage.py shell < setup_roles.py
```

Or manually in Django shell:
```bash
python manage.py shell
```

Then paste this:
```python
from game.models import GameRole

# Clear and create roles
GameRole.objects.all().delete()

roles_data = [
    {"name": "Police", "default_points": 800, "is_police": True},
    {"name": "Thief", "default_points": 1000, "is_thief": True},
    {"name": "King", "default_points": 900},
    {"name": "Queen", "default_points": 800},
    {"name": "Minister", "default_points": 700},
    {"name": "Soldier", "default_points": 600},
    {"name": "Judge", "default_points": 500},
    {"name": "Merchant", "default_points": 400},
    {"name": "Farmer", "default_points": 300},
    {"name": "Banker", "default_points": 200},
    {"name": "Doctor", "default_points": 150},
    {"name": "Teacher", "default_points": 100},
]

for data in roles_data:
    GameRole.objects.create(**data)

print(f"✅ Created {GameRole.objects.count()} roles")
exit()
```

### Step 4: Run the Server

**IMPORTANT:** You MUST use Daphne (Django Channels ASGI server), NOT the regular Django runserver!

```bash
# Run with Daphne
daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application
```

**DO NOT USE:** `python manage.py runserver` ❌ (doesn't support WebSockets)

### Step 5: Test the Game

1. **Open your browser console (F12)** - You'll see debug logs there
2. Navigate to: `http://127.0.0.1:8000/`
3. Create a new game with your name
4. **Open 11 more browser tabs/windows** (use incognito if needed)
5. In each tab, join the game with different names
6. Once you have 12 players, the host can click "Start Game"

## 🐛 Debugging Tips

### Check WebSocket Connection

Open browser console (F12) and look for:
- ✅ `🎮 Initializing game room`
- ✅ `✅ WebSocket connected successfully`
- ✅ `📤 Sent join message`

If you see errors:
- ❌ Make sure you're using Daphne, not runserver
- ❌ Check that port 8000 is not blocked
- ❌ Try a different browser or incognito mode

### Check Role Assignment

After clicking "Start Game":
- Look for: `📨 Received message: {action: 'role_assigned', ...}`
- Should show: `✅ This role is for me!`
- If you're police: `👮 I am POLICE - received player list: 11 players`
- If not police: `🎭 I am NOT police - no player list`

### Check Police Arrest

When clicking arrest button:
- Should show: `🚨 Attempting to arrest: [name]`
- Should show: `📤 Sending arrest message: {...}`
- Result screen should appear for all players

## 📝 What Each Fix Does

### Fix #1: Session ID Field Mismatch

**Before:**
```javascript
if (data.session_id === sessionId) {  // ❌ Wrong field name
```

**After:**
```javascript
if (data.target_session_id === sessionId) {  // ✅ Correct field name
```

**Why:** The backend sends `target_session_id` to route messages to specific players, but the frontend was checking for `session_id`, causing all role assignments to be ignored.

### Fix #2: Missing Session ID in Arrest

**Before:**
```javascript
chatSocket.send(JSON.stringify({
    'action': 'arrest',
    'arrested_player': name
    // ❌ Missing session_id
}));
```

**After:**
```javascript
chatSocket.send(JSON.stringify({
    'action': 'arrest',
    'session_id': sessionId,  // ✅ Added session_id
    'arrested_player': name
}));
```

**Why:** The backend needs to verify that the person making the arrest is actually the police player, which requires the session_id.

## 🎯 Testing Checklist

- [ ] Server running with Daphne (not runserver)
- [ ] 12 roles in database (check with `python manage.py shell` → `from game.models import GameRole; print(GameRole.objects.count())`)
- [ ] Browser console open (F12) to see debug logs
- [ ] 12 players joined before starting game
- [ ] Each player sees chit reveal animation
- [ ] Police player sees arrest buttons
- [ ] Non-police players see waiting message
- [ ] Arrest triggers result screen for all players
- [ ] Leaderboard shows correct scores

## 🆘 Common Issues

### "Need exactly 12 players to start"
**Solution:** You need exactly 12 players. Use multiple browser tabs or windows. Try incognito mode if you run out of regular tabs.

### "Connection lost" / WebSocket closes
**Solution:** 
1. Make sure using Daphne: `daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application`
2. Check server console for errors
3. Try clearing browser cache/cookies

### Chit doesn't flip / No role shown
**Solution:**
1. Check browser console for `role_assigned` messages
2. Verify `target_session_id` matches your `sessionId`
3. Make sure exactly 12 roles exist in database

### Arrest button doesn't work
**Solution:**
1. Check console for arrest message being sent
2. Verify you're the police player
3. Check server logs for verification errors

## 📁 Files Modified

1. ✅ `templates/room.html` - Fixed session_id bugs + added debug logging
2. ✅ `BUG_FIXES.md` - Detailed documentation
3. ✅ `setup_roles.py` - Database setup script
4. ✅ `QUICK_START.md` - This guide

## 🔍 Additional Debugging

If issues persist, check these console logs:

**Initialization:**
```
🎮 Initializing game room
Room Code: ABC123
Player Name: Alice
Session ID: 550e8400-e29b-41d4-a716-446655440000
Is Host: true
✅ WebSocket connected successfully
📤 Sent join message
```

**When game starts:**
```
📨 Received message: {action: 'role_assigned', ...}
🎭 Role assignment message received
   Target: 550e8400-e29b-41d4-a716-446655440000
   My Session: 550e8400-e29b-41d4-a716-446655440000
   Match: true
✅ This role is for me!
👮 I am POLICE - received player list: 11 players
```

**When arresting:**
```
🚨 Attempting to arrest: Bob
   Police Session ID: 550e8400-e29b-41d4-a716-446655440000
📤 Sending arrest message: {action: 'arrest', session_id: '...', arrested_player: 'Bob'}
📨 Received message: {action: 'round_ended', ...}
🏁 Round ended
```

## 🎉 That's It!

Everything should now work correctly. The connectivity issues and police selection problems have been fixed. Open the browser console (F12) to see detailed debug information about what's happening.

Good luck with your game! 🎮
