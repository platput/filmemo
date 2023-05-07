class PlayerLimitMetError(Exception):
    """Raise when more players can't be added to the game."""


class RoundNotExistsError(Exception):
    """Raise when answer submission is invalid"""


class InvalidPlayerError(Exception):
    """Raise when a player tries to do something before getting added to the players list"""


class RoundNotStartedError(Exception):
    """Raise when answer is submitted to a round which is not started yet"""


class RoundAlreadyEndedError(Exception):
    """Raise when answer is submitted to a round which is already ended"""


class GameNotFinishedError(Exception):
    """Raise when game is not yet finished"""


class ActionNotPermittedError(Exception):
    """Raise when players try to do something not allowed"""
