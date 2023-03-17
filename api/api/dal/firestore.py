from google.cloud import firestore

from api.constants import EntityNames
from api.dal.database import Database
from api.errors.database import GameNotFoundError, PlayerNotFoundInGameError, NoPlayersFoundInGameError
from api.models.game import Game, Player, Round


class Firestore(Database):
    def __init__(self):
        self.client = firestore.Client()

    def create_game(self, game: Game) -> Game:
        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict())
        return game

    def add_player(self, game: Game, player: Player) -> Player:
        game_ref = self.client.collection(EntityNames.GAMES).document(game.id).get()
        if game_ref.exists:
            game.players.append(player)
            self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
        else:
            raise GameNotFoundError(f"Game with id: {game.id} was not found in the database!")
        return player

    def submit_answer(self, game: Game, player: Player, game_round: Round, movie_name: str) -> None:
        game_ref = self.client.collection(EntityNames.GAMES).document(game.id).get()
        if game_ref.exists:
            players = game_ref.to_dict().get("players", [])
            if players:
                for p in players:
                    if p.id == player.id:
                        if movie_name == game_round.movie_name:
                            game_round.results[player.id] = True
                        else:
                            game_round.results[player.id] = False
                        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
                    else:
                        raise PlayerNotFoundInGameError(
                            f"Player with id: {player.id} was not found in the game: {game.id}"
                        )
            else:
                raise NoPlayersFoundInGameError(f"Players were not found in the game with id: {game.id}")
        else:
            raise GameNotFoundError(f"Game with id: {game.id} was not found in the database!")

    def start_round(self, game: Game, game_round: Round) -> Round:
        ...

    def end_round(self, game: Game, game_round: Round) -> Round:
        ...

    def end_game(self, game: Game) -> Game:
        ...
