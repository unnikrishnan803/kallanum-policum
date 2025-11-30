from django.db import models
import random
import string

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Room(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Waiting'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished'),
    ]

    room_code = models.CharField(max_length=10, default=generate_room_code, unique=True)
    host_session_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Game Settings
    timer_duration = models.IntegerField(default=60) # Seconds per round
    max_rounds = models.IntegerField(default=5)
    
    def __str__(self):
        return f"Room {self.room_code} ({self.status})"

class GameRole(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(default="No description available.")
    
    # Scoring Logic
    win_points = models.IntegerField(default=100)  # Points earned if their side wins
    lose_points = models.IntegerField(default=0)   # Points earned if their side loses
    
    # Special Roles
    is_police = models.BooleanField(default=False)
    is_thief = models.BooleanField(default=False)
    
    icon = models.CharField(max_length=100, default="default_icon.png")

    def __str__(self):
        return self.name

class Player(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    session_id = models.CharField(max_length=255)
    name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=100, default="default_avatar.png")
    is_active = models.BooleanField(default=True)
    total_score = models.IntegerField(default=0)
    is_host = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room', 'name')

    def __str__(self):
        return f"{self.name} in {self.room.room_code}"

class Round(models.Model):
    STATUS_CHOICES = [
        ('SHUFFLING', 'Shuffling'),
        ('PLAYING', 'Playing'),
        ('INTERROGATION', 'Interrogation'), # Paused state
        ('COMPLETED', 'Completed'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SHUFFLING')
    
    police_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='police_rounds')
    thief_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='thief_rounds')
    
    winner = models.CharField(max_length=20, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    
    # Timer Logic
    remaining_seconds = models.IntegerField(default=60)
    interrogation_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Round {self.round_number} in {self.room.room_code}"

class RoundParticipation(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='participations')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='participations')
    
    # Role Snapshot
    role_name = models.CharField(max_length=50)
    role_description = models.TextField(default="")
    win_points = models.IntegerField(default=0)
    lose_points = models.IntegerField(default=0)
    
    is_caught = models.BooleanField(default=False)
    is_wrongly_accused = models.BooleanField(default=False)
    
    final_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player.name} as {self.role_name}"
