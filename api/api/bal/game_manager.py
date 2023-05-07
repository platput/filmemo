import asyncio
import logging
import uuid
from collections import defaultdict
from datetime import timedelta, datetime
from json import JSONDecodeError

import pytz
from typing import Tuple

from fastapi import WebSocket
from websockets.exceptions import ConnectionClosedError

from api.constants import EntityNames, LogConstants
from api.dal.database import Database
from api.dal.firestore import Firestore
import numpy as np

from api.errors.database import GameNotFoundError
from api.errors.game import RoundNotExistsError, InvalidPlayerError, \
    RoundAlreadyEndedError, RoundNotStartedError, GameNotFinishedError, ActionNotPermittedError
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
        self.tz = pytz.timezone('UTC')

    def __get_game_from_db(self, game_id: str) -> Game:
        """
        Gets the game from the db based on the given ID
        Args:
            game_id: Game ID to get.

        Returns:
            Game object
        """
        if game_dict := self.db_client.get_game(game_id):
            game_dict["round_duration"] = timedelta(minutes=int(game_dict['round_duration']))
            return Game(**game_dict)
        else:
            raise GameNotFoundError(f"Game with id: {game_id} was not found in the database!")

    async def create_game(
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
        rounds = await self.create_rounds(round_count)
        game = Game(
            created_by=player.id,
            user_count=user_count,
            round_count=round_count,
            round_duration=round_duration,
            rounds=rounds,
            players=[player]
        )
        self.db_client.upsert_game(game=game.dict())
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
        game = self.__get_game_from_db(game_id)
        player = Player(
            handle=handle,
            avatar=avatar,
            score=0
        )
        game.players.append(player)
        self.db_client.upsert_game(game.dict())
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
        game = self.__get_game_from_db(game_id)
        if len(self.player_connections[game_id].keys()) >= game.user_count:
            logging.getLogger(LogConstants.APP_NAME).info("Maximum number of players are already in the room.")
            await websocket.close()
            return
        if player_id not in [p.id for p in game.players]:
            raise InvalidPlayerError("Can't join the game before the player is added to the game.")
        await websocket.accept()
        self.player_connections[game_id][player_id] = websocket
        for p in game.players:
            if p.id == player_id:
                message_to_broadcast = {
                    "status": "success",
                    "message": f"{p.handle} has joined the game.",
                    "message_type": "player_join",
                    "meta": {
                        "new_player": {
                            "id": p.id,
                            "handle": p.handle,
                            "avatar": p.avatar,
                        },
                        "existing_players": game.dict().get("players", [])
                    },
                }
                await self.broadcast_to_all_players(game_id, message_to_broadcast)
        # Wait until all players join the game!
        if player_id == game.created_by:
            while True:
                await asyncio.sleep(1)
                if game.user_count == len(self.player_connections[game_id].keys()):
                    message_to_broadcast = {
                        "status": "success",
                        "message": "All players have joined the game, get ready to start guessing...",
                        "message_type": "game_start"
                    }
                    await self.broadcast_to_all_players(game_id, message_to_broadcast)
                    break
            await self.start_round_if_everyone_joined(game_id, player_id)

    async def start_round(self, game_id: str):
        """
        Starts a new round by broadcasting a new emoji from the new round to all players.
        If no new rounds are available, this method will end the game.
        Args:
            game_id: Game ID to start the round in.

        Returns:
            None
        """
        game = self.__get_game_from_db(game_id)
        current_round = None
        for r in game.rounds:
            if r.start_time is None:
                current_round = r
                current_round.start_time = datetime.now(self.tz)
                self.db_client.upsert_game(game.dict())
                break
        if current_round is None:
            await self.end_game(game_id)
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
            await self.broadcast_to_all_players(game_id, message_to_broadcast)
            await self.handle_round(game_id, current_round.id)

    async def start_round_if_everyone_joined(self, game_id: str, player_id: str, force_start: bool = False):
        game = self.__get_game_from_db(game_id)
        for r in game.rounds:
            if r.start_time is not None:
                raise ActionNotPermittedError("The game has been started already.")
        if game.created_by == player_id and force_start:
            await self.start_round(game_id=game_id)
        elif game.created_by != player_id and force_start:
            raise ActionNotPermittedError("Only game creators can force start the game!")
        else:
            current_game_connections = self.player_connections[game_id]
            if len(current_game_connections.keys()) == game.user_count:
                await self.start_round(game_id=game_id)

    async def submit_guess(self, game_id: str, round_id: str, player_id: str, movie_name: str):
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
        game = self.__get_game_from_db(game_id)
        movie_emoji_dict = []
        for r in game.rounds[:(game.round_count + 1)]:
            movie_emoji_dict.append({
                "movie_name": r.movie_name,
                "emoji": r.emoji
            })
        round_found_flag = False
        for r in game.rounds:
            if r.id == round_id:
                round_found_flag = True
                if r.start_time is None:
                    raise RoundNotStartedError(
                        "Invalid submission: The answer for the round you are trying to submit answer has not started"
                        " yet"
                    )
                if r.end_time is not None:
                    raise RoundAlreadyEndedError(
                        "Invalid submission: The answer for the round you are trying to submit answer has already "
                        "ended."
                    )
                is_guess_correct = self.gpt_client.check_if_right_guess(movie_emoji_dict, r.emoji, movie_name)
                r.results[player_id] = is_guess_correct
                player_socket = self.player_connections[game_id][player_id]
                message_to_send = {
                    "status": "success",
                    "message": "Is guess correct?",
                    "meta": {
                        "player_id": player_id,
                        "guess_result": is_guess_correct
                    },
                    "message_type": "guess_result"
                }
                await player_socket.send_json(message_to_send)
                self.db_client.upsert_game(game.dict())
                guessed_players = np.array(r.results.keys())
                current_players = np.array(self.player_connections[game_id].keys())
                if np.array_equal(guessed_players, current_players):
                    if round_end_event := self.game_events.get(game_id, {}).get(round_id):
                        # Setting the round end event which will be picked up by the handle_round function
                        round_end_event.set()
        if not round_found_flag:
            raise RoundNotExistsError(
                "Invalid submission: The answer was submitted for a round which doesn't exist."
            )

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
        game = self.__get_game_from_db(game_id)
        for r in game.rounds:
            if r.id == current_round_id:
                r.end_time = datetime.now(self.tz)
                players_with_guesses = set(r.results.keys())
                all_players = set([p.id for p in game.players])
                players_without_guesses = list(all_players - players_with_guesses)
                for p in players_without_guesses:
                    r.results[p] = False
        self.db_client.upsert_game(game.dict())

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
        for player_id, ws in current_game_connections.items():
            try:
                await ws.send_json(message)
            except ConnectionClosedError:
                del self.player_connections[game_id][player_id]

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
        game = self.__get_game_from_db(game_id)
        current_round = None
        for r in game.rounds:
            if r.id == current_round_id:
                current_round = r
        while True:
            await asyncio.sleep(1)
            if current_round.start_time + game.round_duration <= datetime.now(self.tz):
                break
            if round_end_event := self.game_events.get(game_id, {}).get(current_round_id):
                if round_end_event.is_set():
                    break
        self.end_round(game_id, current_round_id)
        self.game_events.get(game_id, {}).pop(current_round_id)
        await self.start_round(game_id)

    async def end_game(self, game_id: str):
        """
        Ends the game and populates the scores for all the players in the game. The updates the game in the db
        TODO: Also frees up the websocket list from self.player_connections[game_id] belonging to this game.
        Args:
            game_id: Game ID

        Returns:
            None
        """
        game = self.__get_game_from_db(game_id)
        results = {}
        for player in game.players:
            results[player.id] = 0
        rounds = game.rounds
        for r in rounds:
            for k, v in r.results.items():
                if v:
                    results[k] += 1
        sorted_result = dict(sorted(results.items(), key=lambda x: x[1]))
        game.results = sorted_result
        message_to_broadcast = {
            "status": "success",
            "message": "Game ended",
            "meta": {
                "game_id": game.id,
                "game_results": game.results
            },
            "message_type": "end_game"
        }
        await self.broadcast_to_all_players(game_id=game.id, message=message_to_broadcast)
        self.db_client.upsert_game(game.dict())
        self.player_connections.pop(game_id)

    async def create_rounds(self, count: int) -> list[Round]:
        """
        Creates the rounds by getting the movie name and emoji dictionary
        Args:
            count: Number of rounds in the game

        Returns:
            List of rounds
        """
        rounds: list[Round] = []
        while True:
            await asyncio.sleep(1)
            try:
                emoji_movies_list = self.gpt_client.get_movie_names_in_emoji_repr(count)
                break
            except JSONDecodeError:
                logging.getLogger(LogConstants.APP_NAME).warning("Improper json content from chatgpt! Retrying...")
        for em in emoji_movies_list:
            game_ground = Round(
                id=uuid.uuid4().hex,
                emoji=em.get(EntityNames.EMOJI),
                movie_name=em.get(EntityNames.MOVIE_NAME),
            )
            rounds.append(game_ground)
        return rounds[:count+1]

    def is_game_valid(self, game_id: str) -> Tuple[bool, Game | None]:
        """
        Checks if a game id is valid and returns a boolean value to indicate if the game id is valid along with
        the game's object if the game exists
        Args:
            game_id:

        Returns:
            bool, Game | None
        """
        game = self.__get_game_from_db(game_id)
        if game.results:
            return False, game
        else:
            return True, game

    def get_game_with_results(self, game_id: str) -> Game:
        """
        Gets games results and returns the game object.
        Args:
            game_id:

        Returns:
            Game
        """
        game = self.__get_game_from_db(game_id)
        if game.results:
            return game
        else:
            raise GameNotFinishedError("Game has not finished yet!")
