"""
Quick Setup Script for Kallanum Policum Game
This script sets up the game roles in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kallanum_policum.settings')
django.setup()

from game.models import GameRole

def setup_game_roles():
    """Create the 12 required game roles"""
    
    # Clear existing roles
    existing_count = GameRole.objects.count()
    print(f"📊 Found {existing_count} existing roles")
    
    if existing_count != 12:
        print("🗑️ Clearing existing roles...")
        GameRole.objects.all().delete()
        
        print("🎭 Creating 12 game roles...")
        
        roles = [
            {
                "name": "Police", 
                "win_points": 1000, "lose_points": 0,
                "is_police": True, "is_thief": False,
                "description": "Find the thief! You have 60 seconds. You can interrogate once to pause time."
            },
            {
                "name": "Thief", 
                "win_points": 1500, "lose_points": 0,
                "is_police": False, "is_thief": True,
                "description": "Don't get caught! Survive for 60 seconds or trick the police into arresting someone else."
            },
            {
                "name": "King", 
                "win_points": 900, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "You are the ruler. If Police wins, you get 900 points."
            },
            {
                "name": "Queen", 
                "win_points": 800, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Royal consort. If Police wins, you get 800 points."
            },
            {
                "name": "Minister", 
                "win_points": 700, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Advisor to the King. If Police wins, you get 700 points."
            },
            {
                "name": "Soldier", 
                "win_points": 600, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Defender of the realm. If Police wins, you get 600 points."
            },
            {
                "name": "Judge", 
                "win_points": 500, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Keeper of law. If Police wins, you get 500 points."
            },
            {
                "name": "Merchant", 
                "win_points": 400, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Wealthy trader. If Police wins, you get 400 points."
            },
            {
                "name": "Farmer", 
                "win_points": 300, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Honest worker. If Police wins, you get 300 points."
            },
            {
                "name": "Banker", 
                "win_points": 200, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Money handler. If Police wins, you get 200 points."
            },
            {
                "name": "Doctor", 
                "win_points": 150, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Healer. If Police wins, you get 150 points."
            },
            {
                "name": "Teacher", 
                "win_points": 100, "lose_points": 0,
                "is_police": False, "is_thief": False,
                "description": "Educator. If Police wins, you get 100 points."
            },
        ]
        
        for role_data in roles:
            role = GameRole.objects.create(**role_data)
            emoji = "👮" if role.is_police else "🦹" if role.is_thief else "🎭"
            print(f"   {emoji} {role.name} (Win: {role.win_points})")
        
        print("✅ Successfully created 12 roles!")
    else:
        print("✅ All 12 roles already exist!")
        for role in GameRole.objects.all():
            emoji = "👮" if role.is_police else "🦹" if role.is_thief else "🎭"
            print(f"   {emoji} {role.name} (Win: {role.win_points})")

if __name__ == "__main__":
    setup_game_roles()
