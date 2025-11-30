# Bug Fixes Applied - Kallanum Policum

## Issues Fixed

### 1. ✅ Session ID Field Name Mismatch
**Problem:** The backend consumer was sending `target_session_id` but the frontend JavaScript was checking for `session_id`, causing role assignments to fail silently.

**Location:** `templates/room.html` line 162

**Fix Applied:**
```javascript
// BEFORE (BROKEN):
if (data.session_id === sessionId) {

// AFTER (FIXED):
if (data.target_session_id === sessionId) {
```

**Impact:** This was preventing players from seeing their assigned roles after the chit reveal. The WebSocket messages were being sent but ignored by all clients because the field name didn't match.

---

### 2. ✅ Missing Session ID in Arrest Action
**Problem:** When the police player tried to arrest someone, the WebSocket message didn't include the `session_id`, causing the backend to fail verification.

**Location:** `templates/room.html` line 284-291

**Fix Applied:**
```javascript
// BEFORE (BROKEN):
chatSocket.send(JSON.stringify({
    'action': 'arrest',
    'arrested_player': name
}));

// AFTER (FIXED):
chatSocket.send(JSON.stringify({
    'action': 'arrest',
    'session_id': sessionId,
    'arrested_player': name
}));
```

**Impact:** This was preventing the police from making any arrests. The backend's `verify_police()` function needs the session_id to verify that the person making the arrest is actually the police player.

---

## How the Fix Works

### Message Flow Overview:
1. **Player joins** → WebSocket connects → sends 'join' action
2. **Host starts game** → Backend assigns roles → Sends individual `role_assigned` messages
3. **Each client receives ALL messages** but only processes messages where `target_session_id === sessionId`
4. **Police makes arrest** → Sends session_id with arrest action → Backend verifies it's actually the police
5. **Backend processes arrest** → Broadcasts result to all players

### Key Components:
- **Session ID:** Uniquely identifies each player across page refreshes
- **Target Session ID:** Routes role assignment messages to the correct player
- **Group Messaging:** All players in a room receive all messages, but filter based on target

---

## Testing Instructions

### Before Running:
1. Ensure Django Channels is installed: `pip install channels daphne`
2. Ensure you have 12 game roles in the database (see below)
3. Run with Daphne (the ASGI server): `daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application`

### Verify Database Setup:
```bash
python manage.py shell
```

```python
from game.models import GameRole

# Check if roles exist
roles = GameRole.objects.all()
print(f"Total roles: {roles.count()}")  # Should be 12

# If not 12, create them:
if roles.count() < 12:
    GameRole.objects.all().delete()  # Clear existing
    
    # Create the 12 required roles
    GameRole.objects.create(name="Police", default_points=800, is_police=True)
    GameRole.objects.create(name="Thief", default_points=1000, is_thief=True)
    GameRole.objects.create(name="King", default_points=900)
    GameRole.objects.create(name="Queen", default_points=800)
    GameRole.objects.create(name="Minister", default_points=700)
    GameRole.objects.create(name="Soldier", default_points=600)
    GameRole.objects.create(name="Judge", default_points=500)
    GameRole.objects.create(name="Merchant", default_points=400)
    GameRole.objects.create(name="Farmer", default_points=300)
    GameRole.objects.create(name="Banker", default_points=200)
    GameRole.objects.create(name="Doctor", default_points=150)
    GameRole.objects.create(name="Teacher", default_points=100)
    
    print("✅ Created 12 roles")
```

### Testing the Fixes:

#### Test 1: Connectivity Check
1. Open browser console (F12)
2. Navigate to game room
3. Look for WebSocket messages in console:
   - ✅ `WebSocket is already in CONNECTING or OPEN state.` is GOOD
   - ❌ `Chat socket closed unexpectedly` is BAD

#### Test 2: Role Assignment (Testing Fix #1)
1. Create a room with 12 players (use multiple browser tabs/incognito windows)
2. Host clicks "Start Game"
3. Each player should see the chit screen (🎴)
4. **Verify in console:** Look for `Message: {action: 'role_assigned', target_session_id: '...', role: '...'}
5. Click the chit to reveal - role should flip and show

**Expected Behavior:**
- ✅ Chit flips to reveal role name and points
- ✅ "Ready to Play" button appears
- ❌ If chit doesn't flip, check session_id in console

#### Test 3: Police Arrest (Testing Fix #2)
1. After revealing role, if you're the Police:
   - Click "Ready to Play"
   - You should see a list of all other players
   - Each has an "🚨 Arrest" button
2. Click arrest on any player
3. Confirm the arrest

**Expected Behavior:**
- ✅ Result screen appears for all players
- ✅ Shows if thief was caught or escaped
- ❌ If nothing happens, check browser console for errors

---

## Debug Checklist

If issues persist, check these in order:

### 1. WebSocket Connection
- [ ] Browser console shows WebSocket connected
- [ ] No CORS or connection errors
- [ ] Server running with Daphne, not `runserver`

### 2. Session Handling
- [ ] Django sessions middleware is enabled
- [ ] Cookies are enabled in browser
- [ ] Each tab has unique session_id (check in console)

### 3. Database
- [ ] Exactly 12 roles exist in GameRole table
- [ ] Room has exactly 12 players before starting
- [ ] No database migration errors

### 4. Message Routing
- [ ] Console shows: `Message: {action: 'role_assigned', target_session_id: '...'}`
- [ ] target_session_id matches local sessionId variable
- [ ] Role data is present in message

---

## Common Errors & Solutions

### Error: "Need exactly 12 players to start"
**Solution:** You need 12 players in the room. Use multiple browser tabs or incognito windows.

### Error: WebSocket closes immediately
**Solution:** 
1. Make sure you're running with Daphne: `daphne -b 127.0.0.1 -p 8000 kallanum_policum.asgi:application`
2. NOT with: `python manage.py runserver` (doesn't support WebSockets)

### Error: Chit doesn't flip / No role shown
**Solution:** 
1. Check browser console for `role_assigned` message
2. Verify `target_session_id` matches your `sessionId`
3. Make sure you have exactly 12 roles in database

### Error: Arrest button doesn't work
**Solution:**
1. Verify session_id is being sent (check Network tab → WS → Messages)
2. Make sure only police player has arrest buttons
3. Check backend logs for verification errors

---

## Additional Improvements Suggested

### 1. Better Error Handling
Add error messages to the UI when WebSocket fails:

```javascript
chatSocket.onerror = function(e) {
    console.error('WebSocket error:', e);
    alert('Connection error! Please refresh the page.');
};
```

### 2. Reconnection Logic
Add automatic reconnection if connection drops:

```javascript
chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
    setTimeout(() => {
        console.log('Attempting to reconnect...');
        location.reload();
    }, 2000);
};
```

### 3. Loading States
Show loading indicators while waiting for role assignment.

---

## Files Modified

1. `templates/room.html` (2 changes)
   - Line 162: Fixed session_id field mismatch
   - Line 287: Added session_id to arrest message

## Architecture Notes

### Why the fixes were necessary:

**Backend Design (consumers.py):**
- Group messaging is used to broadcast to all players in a room
- Individual targeting is achieved by including `target_session_id` in messages
- Each client receives ALL messages but filters based on their own session_id

**Frontend Design (room.html):**
- Client-side filtering prevents players from seeing each other's roles
- Police gets special `all_players` list that others don't receive
- Session ID must be included in actions that require verification

The bugs occurred because:
1. Field name mismatch prevented proper message filtering
2. Missing session_id prevented backend verification of police identity

Both are critical for game security and functionality.
