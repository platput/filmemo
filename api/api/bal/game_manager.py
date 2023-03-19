import uuid
from collections import defaultdict
from datetime import timedelta, datetime

from fastapi import WebSocket

from api.dal.database import Database
from api.dal.firestore import Firestore
import numpy as np
from api.errors.game import PlayerLimitMetError
from api.models.game import Game, Player


class GameManager:
    def __init__(self):
        self.db_client: Database = Firestore()
        self.game = None
        self.player_connections = defaultdict(dict[str:WebSocket])
        self.game_started_flag = False

    def create_game(
            self,
            created_by: str,
            user_count: int,
            round_count: int,
            round_duration: timedelta,
    ):
        game = Game(
            id=uuid.uuid4().hex,
            created_by=created_by,
            user_count=user_count,
            round_count=round_count,
            round_duration=round_duration,
            players=[created_by]
        )
        self.db_client.upsert_game(game=game)

    def add_player(self, game_id: str, player_id: str, handle: str, avatar: str) -> Player:
        game = self.db_client.get_game(game_id)
        player = Player(
            id=player_id,
            handle=handle,
            avatar=avatar,
            score=0
        )
        if len(game.players) == len(self.player_connections[game_id].keys()):
            raise PlayerLimitMetError("All available seats are filled in this game room.")
        game.players.append(player)
        self.db_client.upsert_game(game)
        return player

    async def join_game(self, game_id: str, player_id: str, websocket: WebSocket):
        current_game_connections = self.player_connections[game_id]
        game = self.db_client.get_game(game_id=game_id)
        current_game_connections[player_id] = websocket
        await websocket.accept()
        message_to_broadcast = {}
        for p in game.players:
            if p.id == player_id:
                message_to_broadcast = {
                    "status": "success",
                    "message": f"{p.handle} has joined the game.",
                    "action": None
                }
                if len(game.players) == len(current_game_connections):
                    message_to_broadcast = {
                        "status": "success",
                        "message": "All players have joined the game, get ready to start guessing...",
                        "action": "start_round"
                    }
        await self.broadcast_to_all_players(game_id, message_to_broadcast)

    async def start_round(self, game_id: str):
        game = self.db_client.get_game(game_id=game_id)
        current_round = None
        for r in game.rounds:
            if r.start_time is None:
                current_round = r
                r.start_time = datetime.now()
        # TODO: Handle if there are no more rounds here.
        message_to_broadcast = {
            "status": "success",
            "message": "Guess the movie",
            "meta": {
                "round_id": current_round.id,
                "emoji": current_round.emoji
            }
        }
        await self.broadcast_to_all_players(game_id, message_to_broadcast)
        self.db_client.upsert_game(game)

    def submit_guess(self, game_id: str, round_id: str, player_id: str, movie_name: str):
        game = self.db_client.get_game(game_id=game_id)
        for r in game.rounds:
            if r.id == round_id:
                if r.movie_name == movie_name:
                    r.results[player_id] = True
                else:
                    r.results[player_id] = False
        self.handle_round(game_id, round_id)

    async def broadcast_to_all_players(self, game_id: str, message: dict):
        current_game_connections = self.player_connections[game_id]
        for _, ws in current_game_connections:
            ws.send_json(message)

    def handle_round(self, game_id: str, current_round_id: str):
        game = self.db_client.get_game(game_id=game_id)
        for r in game.rounds:
            if r.id == current_round_id:
                guessed_players = np.array(r.results.keys())
                current_players = np.array(self.player_connections[game_id].keys())
                if np.array_equal(guessed_players, current_players):
                    r.end_time = datetime.now()
                    self.db_client.upsert_game(game)
                    self.start_round(game_id)
