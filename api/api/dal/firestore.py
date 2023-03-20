from google.cloud import firestore

from api.constants import EntityNames
from api.dal.database import Database
from api.errors.database import GameNotFoundError
from api.models.game import Game


class Firestore(Database):
    """
    Firestore Database store which is the implementation of the interface Database

    """
    def __init__(self):
        self.client = firestore.Client()

    def get_game(self, game_id: str) -> Game:
        """
        Gets the game from the firestore document collection for the given game id
        Args:
            game_id: ID of the game.

        Returns:
            Game: Game object retrieved from the database
        """
        game_ref = self.client.collection(EntityNames.GAMES).document(game_id).get()
        if game_ref.exists:
            return Game(**game_ref.to_dict())
        else:
            raise GameNotFoundError(f"Game with id: {game_id} was not found in the database!")

    def upsert_game(self, game: Game) -> Game:
        """
        Upserts the game object with merge enabled
        Args:
            game: Game object which is to be upserted

        Returns:
            Game: Upserted Game object
        """
        self.client.collection(EntityNames.GAMES).document(game.id).set(game.dict(), merge=True)
        return game
