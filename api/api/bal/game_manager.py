import uuid
from datetime import timedelta

from fastapi import WebSocket

from api.dal.database import Database
from api.dal.firestore import Firestore
from api.errors.game import PlayerLimitMetError
from api.models.game import Game, Player


class GameManager:
    def __init__(
            self,
            creator_socket: WebSocket,
            created_by: str,
            user_count: int,
            round_count: int,
            round_duration: timedelta,
    ):
        self.game = Game(
            id=uuid.uuid4().hex,
            created_by=created_by,
            user_count=user_count,
            round_count=round_count,
            round_duration=round_duration,
            players=[created_by]
        )
        self.db_client: Database = Firestore()
        self.db_client.create_game(game=self.game)
        creator_socket.accept()
        self.player_connections = [creator_socket]

    def join_game(self, player_id: str, handle: str, avatar: str, websocket: WebSocket):
        if len(self.game.players) == len(self.player_connections):
            raise PlayerLimitMetError("All available seats are filled in this game room.")
        player = Player(
            id=player_id,
            handle=handle,
            avatar=avatar,
            score=0
        )
        websocket.accept()
        self.player_connections.append(websocket)
        self.db_client.add_player(game=self.game, player=player)

