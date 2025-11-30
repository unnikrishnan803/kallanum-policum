import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kallanum_policum.settings')
django.setup()

from game.models import GameRole

print("🔍 Checking Roles...")
roles = GameRole.objects.all()
police_count = 0
thief_count = 0

for role in roles:
    flags = []
    if role.is_police: 
        flags.append("👮 POLICE")
        police_count += 1
    if role.is_thief: 
        flags.append("🦹 THIEF")
        thief_count += 1
        
    print(f"- {role.name}: {', '.join(flags)}")

print(f"\nSummary: {police_count} Police, {thief_count} Thief")

if police_count != 1 or thief_count != 1:
    print("❌ ERROR: Must have exactly 1 Police and 1 Thief!")
else:
    print("✅ Roles configuration is CORRECT.")
