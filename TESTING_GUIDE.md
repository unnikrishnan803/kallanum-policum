# Test Game Flow

## How to Test the Complete Game:

### Step 1: Create a Room
1. Open http://127.0.0.1:8000/ in your first browser/tab
2. Enter name "Alice" and click "Create New Game"
3. Note the room code (e.g., "ABC123")

### Step 2: Join with More Players
1. Open http://127.0.0.1:8000/ in 2-3 more browser tabs/windows (incognito mode)
2. Enter different names: "Bob", "Charlie", "Diana"
3. Enter the room code from Step 1
4. Click "Join Game"

### Step 3: Start the Game
1. In Alice's window (the host), click "🎮 Start Game"
2. All players will see a folded chit (🎴)

### Step 4: Reveal Roles
1. Each player clicks on their chit to reveal their role
2. Roles assigned: Police, Thief, King, Minister, etc.
3. Click "✅ Ready to Play"

### Step 5: Police Investigation
- **If you are Police**: You'll see all player names with "🚨 Arrest" buttons
- **If you are NOT Police**: You'll see your role and points, waiting for police

### Step 6: Make an Arrest
- Police player clicks "🚨 Arrest" on a suspect
- Confirms the arrest

### Step 7: See Results
- If Police caught the Thief: "👮 Police Wins!"
- If Police arrested wrong person: "🎭 Thief Escapes!"
- Leaderboard shows updated scores

### Step 8: Next Round
- Host clicks "▶️ Next Round" to play again

## Features Implemented:
✅ Room creation with unique codes
✅ Multi-player join
✅ Real-time WebSocket communication
✅ Random role assignment (Police, Thief, + custom roles)
✅ Beautiful chit reveal animation
✅ Police sees all player names
✅ Other players only see their own role
✅ Arrest mechanism
✅ Scoring system
✅ Leaderboard with medals (🥇🥈🥉)
✅ Round results
