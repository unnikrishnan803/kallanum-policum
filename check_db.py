"""
Script to check if database migrations are applied correctly
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kallanum_policum.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError

def check_db():
    print("🔍 Checking database status...")
    
    try:
        with connection.cursor() as cursor:
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['game_room', 'game_gamerole', 'game_player', 'game_round']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"❌ Missing tables: {', '.join(missing_tables)}")
                print("⚠️  You need to run migrations!")
                return False
                
            # Check columns in GameRole
            cursor.execute("PRAGMA table_info(game_gamerole)")
            columns = [row[1] for row in cursor.fetchall()]
            required_columns = ['win_points', 'lose_points', 'description']
            missing_columns = [c for c in required_columns if c not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns in GameRole: {', '.join(missing_columns)}")
                print("⚠️  You need to run migrations!")
                return False
                
            print("✅ Database structure looks correct!")
            return True
            
    except OperationalError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if check_db():
        print("\n✅ You are ready to play!")
    else:
        print("\n⚠️  PLEASE RUN: python manage.py migrate")
