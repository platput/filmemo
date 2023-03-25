from typing import Dict

from google.cloud import firestore

from api.constants import EntityNames
from api.dal.database import Database
from api.models.game import Game


class Firestore(Database):
    """
    Firestore Database store which is the implementation of the interface Database

    """
    def __init__(self):
        self.client = firestore.Client()

    def get_game(self, game_id: str) -> Dict:
        """
        Gets the game from the firestore document collection for the given game id
        Args:
            game_id: ID of the game.

        Returns:
            Game: Game object retrieved from the database
        """
        game_ref = self.client.collection(EntityNames.GAMES).document(game_id).get()
        if game_ref.exists:
            return game_ref.to_dict()
        else:
            return {}

    def upsert_game(self, game: Dict) -> Dict:
        """
        Upserts the game object with merge enabled
        Args:
            game: Game object which is to be upserted

        Returns:
            Game: Upserted Game object
        """
        self.client.collection(EntityNames.GAMES).document(game.get("id")).set(game, merge=True)
        return game
