from collections import defaultdict
from datetime import datetime

from google.cloud import firestore

from api.constants import EntityNames
from api.dal.database import Database
from api.errors.database import GameNotFoundError, PlayerNotFoundInGameError, NoPlayersFoundInGameError, \
    RoundNotFoundInGameError, NoRoundsFoundInGameError
from api.models.game import Game, Player, Round


class Firestore(Database):
    def __init__(self):
        self.client = firestore.Client()

    def get_game(self, game_id: str) -> Game:
        game_ref = self.client.collection(EntityNames.GAMES).document(game_id).get()
        if game_ref.exists:
            return Game(**game_ref.to_dict())
        else:
            raise GameNotFoundError(f"Game with id: {game_id} was not found in the database!")

    def upsert_game(self, game: Game) -> Game:
        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
        return game


    def submit_answer(self, game: Game, player: Player, game_round: Round, movie_name: str) -> None:
        game_ref = self.client.collection(EntityNames.GAMES).document(game.id).get()
        if game_ref.exists:
            players = game_ref.to_dict().get(EntityNames.PLAYERS, [])
            player_found_flag = False
            if players:
                for p in players:
                    if p[EntityNames.ID] == player.id:
                        player_found_flag = True
                        if movie_name == game_round.movie_name:
                            game_round.results[player.id] = True
                        else:
                            game_round.results[player.id] = False
                        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
                if not player_found_flag:
                    raise PlayerNotFoundInGameError(
                        f"Player with id: {player.id} was not found in game: {game.id}"
                    )
            else:
                raise NoPlayersFoundInGameError(f"Players were not found in game with id: {game.id}")
        else:
            raise GameNotFoundError(f"Game with id: {game.id} was not found in the database!")

    def start_round(self, game: Game, game_round: Round) -> Round:
        game_ref = self.client.collection(EntityNames.GAMES).document(game.id).get()
        if game_ref.exists:
            rounds = game_ref.to_dict().get(EntityNames.ROUNDS, [])
            round_found_flag = False
            if rounds:
                for r in rounds:
                    if r[EntityNames.ID] == game_round.id:
                        round_found_flag = True
                        game_round.start_time = datetime.now()
                        game.rounds = game_round
                        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
                if not round_found_flag:
                    raise RoundNotFoundInGameError(
                        f"Round with id: {game_round.id} was not found in game with id: {game.id}"
                    )
            else:
                raise NoRoundsFoundInGameError(f"Round were not found in game with id: {game.id}")
        else:
            raise GameNotFoundError(f"Game with id: {game.id} was not found in the database!")
        return game_round

    def end_round(self, game: Game, game_round: Round) -> Round:
        game_ref = self.client.collection(EntityNames.GAMES).document(game.id).get()
        if game_ref.exists:
            rounds = game_ref.to_dict().get(EntityNames.ROUNDS, [])
            round_found_flag = False
            if rounds:
                for r in rounds:
                    if r[EntityNames.ID] == game_round.id:
                        round_found_flag = True
                        game_round.end_time = datetime.now()
                        game.rounds = game_round
                        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
                if not round_found_flag:
                    raise RoundNotFoundInGameError(
                        f"Round with id: {game_round.id} was not found in game with id: {game.id}"
                    )
            else:
                raise NoRoundsFoundInGameError(f"Round were not found in game with id: {game.id}")
        else:
            raise GameNotFoundError(f"Game with id: {game.id} was not found in the database!")
        return game_round

    def end_game(self, game: Game) -> Game:
        game_ref = self.client.collection(EntityNames.GAMES).document(game.id).get()
        results = defaultdict(int)
        if game_ref.exists:
            rounds = game.rounds
            for r in rounds:
                for k, v in r.results:
                    if v:
                        results[k] += 1
        game.results = results
        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
        return game
