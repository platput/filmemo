import asyncio
import uuid
from collections import defaultdict
from datetime import timedelta, datetime

from fastapi import WebSocket

from api.constants import EntityNames
from api.dal.database import Database
from api.dal.firestore import Firestore
import numpy as np
from api.errors.game import PlayerLimitMetError, InvalidAnswerSubmission
from api.lib.chatgpt import ChatGPTManager
from api.models.game import Game, Player, Round


class GameManager:
    def __init__(self):
        self.db_client: Database = Firestore()
        self.gpt_client = ChatGPTManager()
        self.game = None
        self.player_connections = defaultdict(dict[str:WebSocket])
        self.game_events: dict[str:dict[str:asyncio.Event]] = {}
        self.game_started_flag = False

    def create_game(
            self,
            handle: str,
            avatar: str,
            user_count: int,
            round_count: int,
            round_duration: timedelta,
    ) -> Game:
        """
        Creates the game with the creator specified settings
        Args:
            avatar: Player avatar
            handle: Player handle
            user_count: Number of players allowed in the game
            round_count: Number of rounds for this game
            round_duration: Time limit for the rounds in the game

        Returns:
            Game object
        """
        player = Player(
            handle=handle,
            avatar=avatar,
            score=0
        )
        rounds = self.create_rounds(round_count)
        game = Game(
            created_by=player.id,
            user_count=user_count,
            round_count=round_count,
            round_duration=round_duration,
            rounds=rounds,
            players=[player]
        )
        self.db_client.upsert_game(game=game)
        return game

    def add_player(self, game_id: str, handle: str, avatar: str) -> Player:
        """
        Adds a player to the game
        Args:
            game_id: ID of the game to which the player has to be added
            handle: Player handle/username
            avatar: Player avatar/display picture

        Returns:
            Player: Player object
        """
        game = self.db_client.get_game(game_id)
        player = Player(
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
        """
        Creates a connection between the player and the server
        Args:
            game_id: Game ID to which the player belongs
            player_id: Player ID
            websocket: Websocket connection

        Returns:
            None
        """
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
                    "message_type": "player_join",
                    "meta": {
                        "player_id": p.id,
                        "handle": p.handle,
                        "avatar": p.avatar,
                    },
                }
                if game.user_count == len(current_game_connections):
                    message_to_broadcast = {
                        "status": "success",
                        "message": "All players have joined the game, get ready to start guessing...",
                        "message_type": "announcement"
                    }
                    await self.start_round_if_everyone_joined(game_id)
        await self.broadcast_to_all_players(game_id, message_to_broadcast)

    async def start_round(self, game_id: str):
        """
        Starts a new round by broadcasting a new emoji from the new round to all players.
        If no new rounds are available, this method will end the game.
        Args:
            game_id: Game ID to start the round in.

        Returns:
            None
        """
        game = self.db_client.get_game(game_id=game_id)
        current_round = None
        for r in game.rounds:
            if r.start_time is None:
                current_round = r
                current_round.start_time = datetime.now()
                self.db_client.upsert_game(game)
        if current_round is None:
            self.end_game(game_id)
            message_to_broadcast = {
                "message_type": "game_end"
            }
        else:
            message_to_broadcast = {
                "status": "success",
                "message": "Guess the movie",
                "meta": {
                    "round_id": current_round.id,
                    "emoji": current_round.emoji
                },
                "message_type": "new_round"
            }
            round_ended_event = asyncio.Event()
            self.game_events[game_id] = {
                current_round.id: round_ended_event
            }
            await self.handle_round(game_id, current_round.id)
        await self.broadcast_to_all_players(game_id, message_to_broadcast)

    async def start_round_if_everyone_joined(self, game_id: str, force_start: bool = False):
        if force_start:
            await self.start_round(game_id=game_id)
        else:
            current_game_connections = self.player_connections[game_id]
            game = self.db_client.get_game(game_id=game_id)
            if len(current_game_connections) == game.user_count:
                await self.start_round(game_id=game_id)

    def submit_guess(self, game_id: str, round_id: str, player_id: str, movie_name: str):
        """
        Submit the guessed movie name and populates the round results dictionary
        Args:
            game_id: Game ID
            round_id: Round ID
            player_id: Player ID
            movie_name: Guessed movie name

        Returns:
            None
        """
        game = self.db_client.get_game(game_id=game_id)
        movie_emoji_dict = []
        for r in game.rounds:
            movie_emoji_dict.append({
                "movie_name": r.movie_name,
                "emoji": r.emoji
            })
        for r in game.rounds:
            if r.end_time is not None:
                raise InvalidAnswerSubmission(
                    "Invalid submission: The answer for the round you are trying to submit answer has already ended."
                )
            if r.id == round_id:
                r.results[player_id] = self.gpt_client.check_if_right_guess(movie_emoji_dict, r.emoji, movie_name)
                guessed_players = np.array(r.results.keys())
                current_players = np.array(self.player_connections[game_id].keys())
                if np.array_equal(guessed_players, current_players):
                    if round_end_event := self.game_events.get(game_id, {}).get(round_id):
                        # Setting the round end event which will be picked up by the handle_round function
                        round_end_event.set()
        self.handle_round(game_id, round_id)

    def end_round(self, game_id: str, current_round_id: str):
        """
        Ends the game by setting the end_time attribute of the current round
        and by setting False as the guess for all the players who haven't yet made any guesses.
        Then upserts the game object.
        Args:
            game_id:
            current_round_id:

        Returns:
            None
        """
        game = self.db_client.get_game(game_id=game_id)
        for r in game.rounds:
            if r.id == current_round_id:
                r.end_time = datetime.now()
                players_with_guesses = set(r.results.keys())
                all_players = set([p.id for p in game.players])
                players_without_guesses = list(all_players - players_with_guesses)
                for p in players_without_guesses:
                    r.results[p] = False
        self.db_client.upsert_game(game)

    async def broadcast_to_all_players(self, game_id: str, message: dict):
        """
        Broadcasts given message to all the connected players
        Args:
            game_id: Game ID
            message: Message to broadcast

        Returns:
            None
        """
        current_game_connections = self.player_connections[game_id]
        for _, ws in current_game_connections:
            ws.send_json(message)

    async def handle_round(self, game_id: str, current_round_id: str):
        """
        Goes into an infinite loop which will exit once the round duration finishes by ending the round.
        In case the round is ended before the duration met, it will exit the infinite loop as well.
        Args:
            game_id: Game ID
            current_round_id: Current round ID

        Returns:
            None
        """
        game = self.db_client.get_game(game_id=game_id)
        current_round = None
        for r in game.rounds:
            if r.id == current_round_id:
                current_round = r
        while True:
            if current_round.start_time + game.round_duration >= datetime.now():
                break
            if round_end_event := self.game_events.get(game_id, {}).get(current_round_id):
                if round_end_event.is_set():
                    break
        self.end_round(game_id, current_round_id)
        self.game_events.get(game_id, {}).pop(current_round_id)
        await self.start_round(game_id)

    def end_game(self, game_id: str):
        """
        Ends the game and populates the scores for all the players in the game. The updates the game in the db
        TODO: Also frees up the websocket list from self.player_connections[game_id] belonging to this game.
        Args:
            game_id: Game ID

        Returns:
            None
        """
        game = self.db_client.get_game(game_id=game_id)
        results = defaultdict(int)
        rounds = game.rounds
        for r in rounds:
            for k, v in r.results:
                if v:
                    results[k] += 1
        game.results = results
        self.db_client.upsert_game(game)
        self.player_connections.pop(game_id)

    def get_game(self, game_id: str) -> Game:
        """
        Gets the game from the db based on the given ID
        Args:
            game_id: Game ID to get.

        Returns:
            Game object
        """
        return self.db_client.get_game(game_id=game_id)

    def create_rounds(self, count: int) -> list[Round]:
        """
        Creates the rounds by getting the movie name and emoji dictionary
        Args:
            count: Number of rounds in the game

        Returns:
            List of rounds
        """
        rounds: list[Round] = []
        emoji_movies_list = self.gpt_client.get_movie_names_in_emoji_repr(count)
        for em in emoji_movies_list:
            game_ground = Round(
                id=uuid.uuid4().hex,
                emoji=em.get(EntityNames.EMOJI),
                movie_name=em.get(EntityNames.MOVIE_NAME),
            )
            rounds.append(game_ground)
        return rounds
