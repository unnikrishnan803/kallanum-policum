from django.shortcuts import render, redirect
from .models import Room, Player
import uuid

def index(request):
    if request.method == "POST":
        action = request.POST.get('action')
        name = request.POST.get('name')
        
        if not request.session.get('session_id'):
            request.session['session_id'] = str(uuid.uuid4())
        session_id = request.session['session_id']

        if action == 'create':
            room = Room.objects.create(host_session_id=session_id)
            # Create player for host
            Player.objects.create(room=room, name=name, session_id=session_id, is_host=True)
            return redirect('room', room_code=room.room_code)
        
        elif action == 'join':
            room_code = request.POST.get('room_code').upper()
            try:
                room = Room.objects.get(room_code=room_code)
                # Check if player already exists with this session
                player, created = Player.objects.get_or_create(
                    room=room, session_id=session_id,
                    defaults={'name': name}
                )
                if not created and player.name != name:
                    player.name = name
                    player.save()
                return redirect('room', room_code=room.room_code)
            except Room.DoesNotExist:
                return render(request, 'index.html', {'error': 'Room not found'})

        # Play Online Removed

    return render(request, 'index.html')

def room(request, room_code):
    try:
        room = Room.objects.get(room_code=room_code)
    except Room.DoesNotExist:
        return redirect('index')
    
    session_id = request.session.get('session_id')
    try:
        player = Player.objects.get(room=room, session_id=session_id)
    except Player.DoesNotExist:
        return redirect('index')

    return render(request, 'room.html', {
        'room': room,
        'player': player,
        'is_host': player.is_host
    })
