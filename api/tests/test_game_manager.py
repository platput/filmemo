import json
from datetime import timedelta, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.bal.game_manager import GameManager
from api.errors.database import GameNotFoundError
from api.errors.game import PlayerLimitMetError, RoundNotExistsError, RoundNotStartedError, \
    GameNotFinishedError
from api.lib import movies
from api.models.game import Game, Player


@pytest.fixture
async def test_client():
    app = FastAPI()
    client = TestClient(app)
    return client


class MockFirestore:
    def __init__(self):
        self.games = {}

    def upsert_game(self, game):
        self.games[game.get("id")] = game

    def get_game(self, game_id):
        return self.games.get(game_id)


class MockGPTManager:
    def __init__(self):
        self.movies = movies.emoji_movies

    def get_movie_names_in_emoji_repr(self, count):
        return [self.movies[0]] * count

    def check_if_right_guess(self, movie_list, emoji, guessed_name):
        if self.movies[0][emoji] == guessed_name:
            return True
        else:
            return False


class TestGameManager:
    def initialize_tests(self, monkeypatch):
        self.game_manager = GameManager()
        # Mock the Firestore functions
        self.mock_firestore = MockFirestore()
        self.mock_gpt = MockGPTManager()
        monkeypatch.setattr(self.game_manager.db_client, "upsert_game", self.mock_firestore.upsert_game)
        monkeypatch.setattr(self.game_manager.db_client, "get_game", self.mock_firestore.get_game)
        monkeypatch.setattr(self.game_manager.gpt_client, "get_movie_names_in_emoji_repr",
                            self.mock_gpt.get_movie_names_in_emoji_repr)
        monkeypatch.setattr(self.game_manager.gpt_client, "check_if_right_guess", self.mock_gpt.check_if_right_guess)

    def test_create_game(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        # Create the game
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=3, round_count=2,
                                             round_duration=timedelta(minutes=1))
        # Assertions
        assert isinstance(game, Game)
        assert game.user_count == 3
        assert game.round_count == 2
        assert game.round_duration == timedelta(minutes=1)

    def test_add_player(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        # Happy path test
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=3, round_count=2,
                                             round_duration=timedelta(minutes=1))
        player = self.game_manager.add_player(game_id=game.id, handle="player_handle", avatar="player_avatar")
        assert isinstance(player, Player)
        assert player.handle == "player_handle"
        assert player.avatar == "player_avatar"
        assert player.score == 0

    def test_add_player_limit_met(self, monkeypatch):
        """
        Tests if players can be added to the game even after meeting the limit of game's user count
        Note: First player is added as soon as the game is created
        Args:
            monkeypatch:
        Returns:
            None
        """
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=2,
                                             round_duration=timedelta(minutes=1))
        with pytest.raises(PlayerLimitMetError):
            self.game_manager.add_player(game_id=game.id, handle="player_handle", avatar="player_avatar")

    def test_add_player_invalid_game_id(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=2,
                                             round_duration=timedelta(minutes=1))
        with pytest.raises(GameNotFoundError):
            self.game_manager.add_player(game_id="invalid_id", handle="player_handle", avatar="player_avatar")

    def test_submit_guess_invalid_player_id(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
                                             round_duration=timedelta(minutes=1))
        with pytest.raises(RoundNotExistsError):
            self.game_manager.submit_guess(game_id=game.id, round_id="invalid_round_id", player_id="invalid_player_id",
                                           movie_name="movie_name")

    def test_submit_guess_invalid_round_id(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
                                             round_duration=timedelta(minutes=1))
        with pytest.raises(RoundNotExistsError):
            self.game_manager.submit_guess(game_id=game.id, round_id="invalid_round_id", player_id="invalid_player_id",
                                           movie_name="movie_name")

    def test_submit_guess_not_started_round_id(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
                                             round_duration=timedelta(minutes=1))
        player = game.players[0]
        game.rounds[0].end_time = game.rounds[0].start_time = None
        with pytest.raises(RoundNotStartedError):
            self.game_manager.submit_guess(game_id=game.id, round_id=game.rounds[0].id, player_id=player.id,
                                           movie_name="movie_name")

    def test_get_game_with_results(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
                                             round_duration=timedelta(minutes=1))
        results = {game.players[0].id: 1}
        game.results = results
        self.game_manager.db_client.upsert_game(game.dict())
        game_with_result = self.game_manager.get_game_with_results(game.id)
        results = game_with_result.results
        assert game.results.get(game.players[0].id) == results.get(game.players[0].id)
        assert game.players[0].id in results.keys()

    def test_get_game_with_results_when_game_has_not_finished(self, monkeypatch):
        self.initialize_tests(monkeypatch)
        game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
                                             round_duration=timedelta(minutes=1))
        with pytest.raises(GameNotFinishedError):
            self.game_manager.get_game_with_results(game.id)

    # @pytest.mark.anyio
    # async def test_submit_guess_ended_round_id(self, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
    #                                          round_duration=timedelta(minutes=1))
    #     game.rounds[0].end_time = datetime.now()
    #     game.rounds[0].start_time = datetime.now() - timedelta(seconds=10)
    #     player = game.players[0]
    #     await self.game_manager.start_round(game.id)
    #     with pytest.raises(RoundAlreadyEndedError):
    #         self.game_manager.submit_guess(game_id=game.id, round_id=game.rounds[0].id, player_id=player.id,
    #                                        movie_name="movie_name")
    #
    # @pytest.mark.anyio
    # async def test_submit_correct_answer(self, test_client, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
    #                                          round_duration=timedelta(minutes=1))
    #     game.rounds[0].start_time = datetime.now()
    #     player = game.players[0]
    #     movie_name = game.rounds[0].movie_name
    #     async with test_client.websocket_connect(f"/ws") as websocket:
    #         await self.game_manager.join_game(game.id, game.players[0].id, websocket)
    #         self.game_manager.submit_guess(game_id=game.id, round_id=game.rounds[0].id, player_id=player.id,
    #                                        movie_name=movie_name)
    #
    # @pytest.mark.anyio
    # async def test_start_round(self, test_client, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1, round_count=1,
    #                                          round_duration=timedelta(minutes=1))
    #     async with test_client.websocket_connect(f"/ws") as websocket:
    #         await self.game_manager.join_game(game.id, game.players[0].id, websocket)
    #         await self.game_manager.start_round(game.id)
    #         message = await websocket.receive()
    #         # assert the contents of the message
    #         message = json.loads(message)
    #         assert message.get("message_type") == "new_round"
    #
    # @pytest.mark.anyio
    # async def test_start_round_invalid_game(self, test_client, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     with pytest.raises(GameNotFoundError):
    #         game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1,
    #                                              round_count=1,
    #                                              round_duration=timedelta(minutes=1))
    #         async with test_client.websocket_connect(f"/ws") as websocket:
    #             await self.game_manager.join_game(game.id, game.players[0].id, websocket)
    #             await self.game_manager.start_round("invalid_game_id")
    #             message = await websocket.receive()
    #             # assert the contents of the message
    #             message = json.loads(message)
    #             assert message.get("message_type") == "new_round"


    # @pytest.mark.anyio
    # async def test_join_game(self, test_client, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=2, round_count=1,
    #                                          round_duration=timedelta(minutes=1))
    #     player = self.game_manager.add_player(game_id=game.id, handle="player_handle", avatar="player_avatar")
    #     websocket = test_client.websocket_connect(f"/ws")
    #     await self.game_manager.join_game(game.id, player.id, websocket)
    #     response = await websocket.receive_json()
    #     assert "success" == response.get("status")
    #     assert self.game_manager.player_connections[game.id][player.id] == websocket
    #     websocket.close()

    # @pytest.mark.anyio
    # async def test_join_game_invalid_player_id(self, test_client, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     with pytest.raises(InvalidPlayerError):
    #         game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1,
    #                                              round_count=1,
    #                                              round_duration=timedelta(minutes=1))
    #         _ = self.game_manager.add_player(game_id=game.id, handle="player_handle", avatar="player_avatar")
    #         async with test_client.websocket_connect(f"/ws") as websocket:
    #             await self.game_manager.join_game(game.id, "Invalid player id", websocket)
    #
    # @pytest.mark.anyio
    # async def test_join_invalid_game_id(self, test_client, monkeypatch):
    #     self.initialize_tests(monkeypatch)
    #     with pytest.raises(GameNotFoundError):
    #         game = self.game_manager.create_game(handle="test_handle", avatar="test_avatar", user_count=1,
    #                                              round_count=1,
    #                                              round_duration=timedelta(minutes=1))
    #         _ = self.game_manager.add_player(game_id=game.id, handle="player_handle", avatar="player_avatar")
    #         async with test_client.websocket_connect(f"/ws") as websocket:
    #             await self.game_manager.join_game(game.id, "Invalid player id", websocket)
