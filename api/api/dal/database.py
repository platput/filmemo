from typing import Protocol

from api.models.game import Game, Player, Round


class Database(Protocol):
    """
    An interface representing a database.

    Methods:
    --------
    create_game(game: Game) -> Game:
        Creates a new game document in the database and returns the updated game object.
    add_player(game: Game, player: Player) -> Player:
        Adds a new player document to the game's collection in the database and returns the updated player object.
    submit_answer(game: Game, player: Player, movie_name: str) -> None:
        Updates the player's document in the database with the submitted answer.
    start_round(game: Game, game_round: Round) -> Round:
        Starts a new round in the game and returns the updated round object.
    end_round(game: Game, game_round: Round) -> Round:
        Ends the current round in the game and returns the updated round object.
    end_game(game: Game) -> Game:
        Ends the game and calculates the final scores, updates the game document in the database, and returns the updated
        game object.
    """
    def create_game(self, game: Game) -> Game:
        ...

    def add_player(self, game: Game, player: Player) -> Player:
        ...

    def submit_answer(self, game: Game, player: Player, game_round: Round, movie_name: str) -> None:
        ...

    def start_round(self, game: Game, game_round: Round) -> Round:
        ...

    def end_round(self, game: Game, game_round: Round) -> Round:
        ...

    def end_game(self, game: Game) -> Game:
        ...
