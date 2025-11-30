from django.contrib import admin
from .models import Room, Player, GameRole, Round, RoundParticipation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_code', 'status', 'created_at']
    list_filter = ['status']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'total_score', 'is_host']
    list_filter = ['is_host']

@admin.register(GameRole)
class GameRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'win_points', 'lose_points', 'is_police', 'is_thief']
    list_filter = ['is_police', 'is_thief']

@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ['room', 'round_number', 'status', 'winner']
    list_filter = ['status']

@admin.register(RoundParticipation)
class RoundParticipationAdmin(admin.ModelAdmin):
    list_display = ['player', 'round', 'role_name', 'final_score']
