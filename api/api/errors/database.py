class GameNotFoundError(Exception):
    """Raise when game is not found in the database"""


class PlayerNotFoundInGameError(Exception):
    """Raise when player is not found in the game"""


class NoPlayersFoundInGameError(Exception):
    """Raise when players are not found in the game"""
