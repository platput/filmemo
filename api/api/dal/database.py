from typing import Protocol

from api.models.game import Game


class Database(Protocol):
    """
    Database interface to be implemented by all database stores.

    Methods:
        get_game(game_id: str) -> Game: Get a game by ID.
        upsert_game(game: Game) -> Game: Upsert a game.
    """
    def get_game(self, game_id: str) -> Game:
        """
        Gets the game with the given ID.
        Args:
            game_id: ID of the game

        Returns:
            Game: Game with the given ID
        """
        ...

    def upsert_game(self, game: Game) -> Game:
        """
        Creates or updates a game object in the database
        Args:
            game: The game object to be created or updated in database

        Returns:
            Game: The upserted game object
        """
        ...
