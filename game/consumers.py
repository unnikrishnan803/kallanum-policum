import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta
from .models import Room, Player, GameRole, Round, RoundParticipation

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept immediately to establish connection
        await self.accept()
        try:
            self.room_code = self.scope['url_route']['kwargs']['room_code']
            self.room_group_name = f'room_{self.room_code}'
            self.timer_task = None
            
            print(f"🔌 Connecting to room: {self.room_code}")
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            print(f"✅ Connected to {self.room_group_name}")
            
            # Send current player list to all connected clients
            players = await self.get_players_in_room()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_update',
                    'players': players
                }
            )
            
        except Exception as e:
            print(f"❌ Error in connect: {str(e)}")
            import traceback
            traceback.print_exc()
            # Send error to client
            try:
                await self.send(text_data=json.dumps({
                    'action': 'error',
                    'message': f'Connection failed: {str(e)}'
                }))
            except:
                pass
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name'):
                print(f"🔌 Disconnecting from {self.room_group_name} (Code: {close_code})")
                
                # Handle Player Disconnect Logic
                if 'session' in self.scope and self.scope['session'].session_key:
                    await self.handle_player_disconnect(self.scope['session'].session_key)
                
                if self.timer_task:
                    self.timer_task.cancel()
                    
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            else:
                print(f"🔌 Disconnecting (Code: {close_code}) - No room group")
        except Exception as e:
            print(f"❌ Error in disconnect: {e}")
            print(f"❌ Error in disconnect: {str(e)}")
            import traceback
            traceback.print_exc()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            session_id = data.get('session_id')
            
            print(f"📩 Received action: {action} from {session_id}")

            if action == 'get_settings':
                settings = await self.get_game_settings_data()
                await self.send(text_data=json.dumps({
                    'action': 'settings_data',
                    'settings': settings
                }))

            elif action == 'update_settings':
                max_rounds = int(data.get('max_rounds', 5))
                roles_data = data.get('roles', [])
                
                await self.update_game_settings_advanced(max_rounds, roles_data)
                
                # Confirm save
                await self.send(text_data=json.dumps({
                    'action': 'settings_saved',
                    'message': 'Settings updated successfully!'
                }))

            elif action == 'next_round':
                print(f"🔄 Next Round requested by {session_id}")
                
                can_start = await self.check_max_rounds()
                if not can_start:
                    print("🏁 Max rounds reached. Ending game.")
                    final_scores = await self.get_final_scores()
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_over',
                            'scores': final_scores
                        }
                    )
                else:
                    # Broadcast reset to all players
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'reset_round'
                        }
                    )

            elif action == 'join':
                players = await self.get_players_in_room()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_update',
                        'players': players
                    }
                )
        
            elif action == 'start_game':
                # Remove any existing bots first - REMOVED for performance
                # await self.remove_bots()
                
                # Broadcast updated player list (without bots)
                players = await self.get_players_in_room()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_update',
                        'players': players
                    }
                )
                
                player_count = await self.get_player_count()
                
                if player_count < 2:
                    await self.send(text_data=json.dumps({
                        'action': 'error',
                        'message': f'Need at least 2 players to start. Currently have {player_count}.'
                    }))
                    return
                
                if player_count > 12:
                     await self.send(text_data=json.dumps({
                        'action': 'error',
                        'message': f'Maximum 12 players allowed. Currently have {player_count}.'
                    }))
                     return

                # Check max rounds
                print(f"🔄 Checking max rounds for Room {self.room_code}...")
                can_start = await self.check_max_rounds()
                print(f"🔄 Check Max Rounds Result: {can_start}")
                
                if not can_start:
                    print("🏁 Max rounds reached (in start_game). Ending game.")
                    # GAME OVER LOGIC
                    final_scores = await self.get_final_scores()
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_over',
                            'scores': final_scores
                        }
                    )
                    return

                print(f"🚀 Starting new round for Room {self.room_code} with {player_count} players...")
                try:
                    game_data = await self.start_new_round(player_count)
                    print(f"✅ Round started successfully. Round ID: {game_data.get('round_id')}")
                except Exception as e:
                    print(f"❌ Error in start_new_round: {e}")
                    import traceback
                    traceback.print_exc()
                    await self.send(text_data=json.dumps({
                        'action': 'error',
                        'message': f'Failed to start round: {str(e)}'
                    }))
                    return
                
                # Start Timer Task
                if self.timer_task:
                    self.timer_task.cancel()
                self.timer_task = asyncio.create_task(self.run_timer(game_data['round_id']))
                
                # Send roles
                for player_data in game_data['players']:
                    message = {
                        'type': 'send_role_to_player',
                        'target_session_id': player_data['session_id'],
                        'role': player_data['role'],
                        'description': player_data['description'],
                        'points': player_data['points'], # Win points shown initially
                        'is_police': player_data['is_police'],
                        'is_thief': player_data['is_thief'],
                        'all_players': game_data['all_players'] if player_data['is_police'] else None
                    }
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        message
                    )
            elif action == 'arrest':
                arrested_player_name = data.get('arrested_player')
                print(f"🚨 Arrest Request: {session_id} wants to arrest {arrested_player_name}")
                
                is_valid_police = await self.verify_police(session_id)
                if not is_valid_police:
                    print(f"❌ Invalid Police: {session_id}")
                    return
                
                print(f"✅ Valid Police. Processing arrest...")
                result = await self.process_arrest(arrested_player_name)
                
                if self.timer_task:
                    self.timer_task.cancel()
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'round_result',
                        'winner': result['winner'],
                        'thief_name': result['thief_name'],
                        'scores': result['scores'],
                        'all_roles': result['all_roles']
                    }
                )
                
        except Exception as e:
            print(f"❌ Error in receive: {str(e)}")
            import traceback
            traceback.print_exc()

    async def run_timer(self, round_id):
        """Timer loop that runs for 60 seconds"""
        print(f"⏰ Timer STARTED for Round {round_id}")
        try:
            for i in range(60, -1, -1):
                # Check if round is still playing
                status = await self.get_round_status(round_id)
                
                if status == 'COMPLETED':
                    print(f"⏰ Timer STOPPED: Round {round_id} completed early.")
                    break
                
                # Broadcast timer tick
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_update',
                        'seconds': i
                    }
                )
                
                if i == 0:
                    print(f"⏰ Timer EXPIRED for Round {round_id}")
                    # Timeout - Thief Wins
                    result = await self.process_timeout(round_id)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'round_result',
                            'winner': result['winner'],
                            'thief_name': result['thief_name'],
                            'scores': result['scores'],
                            'all_roles': result['all_roles']
                        }
                    )
                    break
                
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print(f"⏰ Timer CANCELLED for Round {round_id}")
            pass
        except Exception as e:
            print(f"❌ Timer CRASHED for Round {round_id}: {e}")
            import traceback
            traceback.print_exc()

    async def player_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'player_joined',
            'players': event['players']
        }))

    async def send_role_to_player(self, event):
        await self.send(text_data=json.dumps({
            'action': 'role_assigned',
            'target_session_id': event['target_session_id'],
            'role': event['role'],
            'description': event['description'],
            'points': event['points'],
            'is_police': event['is_police'],
            'all_players': event.get('all_players')
        }))

    async def round_result(self, event):
        await self.send(text_data=json.dumps({
            'action': 'round_ended',
            'winner': event['winner'],
            'thief_name': event['thief_name'],
            'scores': event['scores'],
            'all_roles': event.get('all_roles', [])
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game_over',
            'scores': event['scores']
        }))

    async def timer_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'timer_tick',
            'seconds': event['seconds']
        }))

    async def reset_round(self, event):
        await self.send(text_data=json.dumps({
            'action': 'reset_round'
        }))

    @database_sync_to_async
    def get_round_status(self, round_id):
        try:
            round_obj = Round.objects.get(id=round_id)
            return round_obj.status
        except Round.DoesNotExist:
            return 'COMPLETED'

    @database_sync_to_async
    def get_players_in_room(self):
        room = Room.objects.get(room_code=self.room_code)
        return [{'name': p.name, 'avatar': p.avatar, 'session_id': p.session_id} for p in room.players.all()]

    @database_sync_to_async
    def get_player_count(self):
        room = Room.objects.get(room_code=self.room_code)
        return room.players.count()

    @database_sync_to_async
    def remove_bots(self):
        room = Room.objects.get(room_code=self.room_code)
        room.players.filter(name__startswith="Bot_").delete()



    @database_sync_to_async
    def get_game_settings_data(self):
        room = Room.objects.get(room_code=self.room_code)
        roles = GameRole.objects.all().order_by('id')
        
        roles_data = []
        for r in roles:
            roles_data.append({
                'id': r.id,
                'name': r.name,
                'win_points': r.win_points
            })
            
        return {
            'max_rounds': room.max_rounds,
            'roles': roles_data
        }

    @database_sync_to_async
    def update_game_settings_advanced(self, max_rounds, roles_data):
        # Update Room
        room = Room.objects.get(room_code=self.room_code)
        room.max_rounds = max_rounds
        room.save()
        
        # Update Roles
        for r_data in roles_data:
            try:
                role = GameRole.objects.get(id=r_data['id'])
                role.name = r_data['name']
                role.win_points = int(r_data['win_points'])
                role.save()
            except GameRole.DoesNotExist:
                pass

    @database_sync_to_async
    def check_max_rounds(self):
        room = Room.objects.get(room_code=self.room_code)
        current_rounds = room.rounds.count()
        print(f"📊 Round Check: Current {current_rounds} / Max {room.max_rounds}")
        return current_rounds < room.max_rounds

    @database_sync_to_async
    def get_final_scores(self):
        room = Room.objects.get(room_code=self.room_code)
        room.status = 'FINISHED'
        room.save()
    @database_sync_to_async
    def verify_police(self, session_id):
        room = Room.objects.get(room_code=self.room_code)
        # Get the latest playing round
        current_round = room.rounds.filter(status='PLAYING').order_by('-id').first()
        
        if not current_round:
            print("❌ verify_police: No playing round found")
            return False
            
        if not current_round.police_player:
            print("❌ verify_police: No police player assigned")
            return False
            
        is_match = current_round.police_player.session_id == session_id
        print(f"👮 Verify Police Check:")
        print(f"   - Round ID: {current_round.id}")
        print(f"   - Round Status: {current_round.status}")
        print(f"   - Expected Police Session: {current_round.police_player.session_id} ({current_round.police_player.name})")
        print(f"   - Actual Requester Session: {session_id}")
        print(f"   - Match: {is_match}")
        return is_match

    @database_sync_to_async
    def start_new_round(self, player_count):
        room = Room.objects.get(room_code=self.room_code)
        
        # CRITICAL FIX: Close any existing playing rounds to prevent "zombie rounds"
        active_rounds = room.rounds.filter(status='PLAYING')
        if active_rounds.exists():
            print(f"⚠️ Found {active_rounds.count()} active rounds. Closing them...")
            for r in active_rounds:
                r.status = 'ABANDONED'
                r.save()
        
        room.status = 'IN_PROGRESS'
        room.save()
        
        players = list(room.players.all())
        all_roles_qs = list(GameRole.objects.all())
        
        # Auto-create roles if missing (First run on Render)
        if not all_roles_qs:
            print("⚠️ No roles found! Creating default roles...")
            police = GameRole.objects.create(name="Police", is_police=True, win_points=100)
            thief = GameRole.objects.create(name="Thief", is_thief=True, win_points=100)
            civilian = GameRole.objects.create(name="Civilian", win_points=50)
            all_roles_qs = [police, thief, civilian]
            print("✅ Default roles created.")
        
        # Select roles: Must have Police and Thief
        police_role = next(r for r in all_roles_qs if r.is_police)
        thief_role = next(r for r in all_roles_qs if r.is_thief)
        other_roles = [r for r in all_roles_qs if not r.is_police and not r.is_thief]
        
        random.shuffle(other_roles)
        
        # We need (player_count - 2) other roles
        # If not enough roles, reuse civilians (just in case)
        while len(other_roles) < player_count - 2:
             other_roles.append(other_roles[0]) # Duplicate first role if needed
             
        selected_roles = [police_role, thief_role] + other_roles[:player_count-2]
        
        # Verify we have Police and Thief
        has_police = any(r.is_police for r in selected_roles)
        has_thief = any(r.is_thief for r in selected_roles)
        print(f"🎲 Starting Round with {player_count} players. Roles: {[r.name for r in selected_roles]}")
        print(f"👮 Has Police: {has_police}, 🦹 Has Thief: {has_thief}")
        
        if not has_police or not has_thief:
            print("❌ CRITICAL ERROR: Missing Police or Thief in selected roles!")
            raise Exception("Failed to assign required roles (Police/Thief)")
        
        # --- SMART SHUFFLE LOGIC ---
        # Get last round's roles to avoid immediate repeats
        last_round = room.rounds.filter(status__in=['COMPLETED', 'ABANDONED']).order_by('-id').first()
        last_police_id = last_round.police_player.id if last_round and last_round.police_player else None
        last_thief_id = last_round.thief_player.id if last_round and last_round.thief_player else None
        
        max_retries = 5
        for attempt in range(max_retries):
            random.shuffle(players)
            random.shuffle(selected_roles)
            
            # If it's the first round or we ran out of retries, accept it
            if not last_police_id and not last_thief_id:
                break
            if attempt == max_retries - 1:
                print("⚠️ Smart Shuffle: Max retries reached, accepting shuffle.")
                break
                
            # Check assignments
            # Find who got Police and Thief in this proposed shuffle
            # players[i] gets selected_roles[i]
            
            proposed_police = None
            proposed_thief = None
            
            for i in range(len(players)):
                if selected_roles[i].is_police:
                    proposed_police = players[i]
                elif selected_roles[i].is_thief:
                    proposed_thief = players[i]
            
            # Check for repeats
            repeat_police = (proposed_police and proposed_police.id == last_police_id)
            repeat_thief = (proposed_thief and proposed_thief.id == last_thief_id)
            
            if repeat_police or repeat_thief:
                print(f"🔄 Smart Shuffle: Retry {attempt+1}/{max_retries} (Police Repeat: {repeat_police}, Thief Repeat: {repeat_thief})")
                continue
            else:
                print("✅ Smart Shuffle: Good distribution found.")
                break
        # ---------------------------
        
        round_obj = Round.objects.create(
            room=room,
            round_number=room.rounds.count() + 1,
            status='PLAYING'
        )
        
        player_data = []
        all_players_info = []
        
        for i in range(player_count):
            player = players[i]
            role = selected_roles[i]
            
            RoundParticipation.objects.create(
                round=round_obj,
                player=player,
                role_name=role.name,
                role_description=role.description,
                win_points=role.win_points,
                lose_points=role.lose_points
            )
            
            if role.is_police:
                round_obj.police_player = player
            elif role.is_thief:
                round_obj.thief_player = player
            
            player_data.append({
                'session_id': player.session_id,
                'name': player.name,
                'role': role.name,
                'description': role.description,
                'points': role.win_points,
                'is_police': role.is_police,
                'is_thief': role.is_thief
            })
            
            all_players_info.append({
                'name': player.name,
                'avatar': player.avatar,
                'session_id': player.session_id
            })
        
        round_obj.save()
        
        return {
            'round_id': round_obj.id,
            'players': player_data,
            'all_players': all_players_info
        }

    @database_sync_to_async
    def process_arrest(self, arrested_player_name):
        room = Room.objects.get(room_code=self.room_code)
        current_round = room.rounds.filter(status='PLAYING').first()
        
        if not current_round:
            return {'winner': 'ERROR', 'thief_name': '', 'scores': [], 'all_roles': []}
        
        thief = current_round.thief_player
        arrested_player = room.players.filter(name=arrested_player_name).first()
        
        # Determine Winner
        if arrested_player == thief:
            current_round.winner = 'POLICE'
            # Police wins
            for p in current_round.participations.all():
                if p.role_name == 'Police':
                    p.final_score = p.win_points
                elif p.role_name == 'Thief':
                    p.final_score = 0  # Loser gets 0
                    p.is_caught = True
                else:
                    # Civilians always get points
                    p.final_score = p.win_points
                
                p.save()
                p.player.total_score += p.final_score
                p.player.save()
        else:
            current_round.winner = 'THIEF'
            # Thief wins
            for p in current_round.participations.all():
                if p.role_name == 'Police':
                    p.final_score = 0  # Loser gets 0
                elif p.role_name == 'Thief':
                    p.final_score = p.win_points
                else:
                    # Civilians always get points
                    p.final_score = p.win_points
                
                if p.player == arrested_player:
                    p.is_wrongly_accused = True
                
                p.save()
                p.player.total_score += p.final_score
                p.player.save()
        
        current_round.status = 'COMPLETED'
        current_round.save()
        
        return self._get_round_result_data(room, current_round)

    @database_sync_to_async
    def process_timeout(self, round_id):
        round_obj = Round.objects.get(id=round_id)
        round_obj.winner = 'THIEF'
        round_obj.status = 'COMPLETED'
        round_obj.save()
        
        thief = round_obj.thief_player
        
        # Thief wins by timeout
        for p in round_obj.participations.all():
            if p.role_name == 'Police':
                p.final_score = 0  # Loser gets 0
            elif p.role_name == 'Thief':
                p.final_score = p.win_points
            else:
                # Civilians always get points
                p.final_score = p.win_points
            
            p.save()
            p.player.total_score += p.final_score
            p.player.save()
            
        return self._get_round_result_data(room, round_obj)

    def _get_round_result_data(self, room, round_obj):
        all_roles_reveal = []
        for participation in round_obj.participations.all():
            all_roles_reveal.append({
                'name': participation.player.name,
                'role': participation.role_name
            })
            
        # Get updated scores
        scores = []
        for p in room.players.all():
             scores.append({
                 'name': p.name,
                 'score': p.total_score,
                 'avatar': p.avatar
             })
             
        thief_name = round_obj.thief_player.name if round_obj.thief_player else "Unknown"
        
        return {
            'winner': round_obj.winner,
            'thief_name': thief_name,
            'scores': scores,
            'all_roles': all_roles_reveal
        }

    @database_sync_to_async
    def remove_player_from_room(self, session_id):
        try:
            room = Room.objects.get(room_code=self.room_code)
            player = room.players.filter(session_id=session_id).first()
            if player:
                print(f"👋 Removing player {player.name} from room")
                player.delete()
                return True
            return False
        except Exception as e:
            print(f"Error removing player: {e}")
            return False

    async def handle_player_disconnect(self, session_id):
        await self.remove_player_from_room(session_id)
        
        # Broadcast update
        players = await self.get_players_in_room()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_update',
                'players': players
            }
        )

    async def host_change(self, event):
        await self.send(text_data=json.dumps({
            'action': 'host_change',
            'new_host_session_id': event['new_host_session_id']
        }))

    async def round_aborted(self, event):
        await self.send(text_data=json.dumps({
            'action': 'error',
            'message': f"Round Aborted: {event['reason']}"
        }))
        # Reset UI
        await self.send(text_data=json.dumps({
            'action': 'reset_round'
        }))
