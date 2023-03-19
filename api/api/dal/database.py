from typing import Protocol

from api.models.game import Game, Player, Round


class Database(Protocol):
    """
    An interface representing a database.

    Methods:
    --------
    upsert_game(game: Game) -> Game:
        Creates/Updates a game document in the database and returns the game object.
    get_game(game_id: str) -> Game:
        Gets the game from the database based on the game id.
    submit_answer(game: Game, player: Player, movie_name: str) -> None:
        Updates the player's document in the database with the submitted answer.
    start_round(game: Game, game_round: Round) -> Round:
        Starts a new round in the game and returns the updated round object.
    end_round(game: Game, game_round: Round) -> Round:
        Ends the current round in the game and returns the updated round object.
    end_game(game: Game) -> Game:
        Ends the game and calculates the final scores, updates the game document in the database, and returns the
        updated game object.
    """
    def get_game(self, game_id: str) -> Game:
        ...

    def upsert_game(self, game: Game) -> Game:
        ...
