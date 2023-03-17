import uuid

from pydantic import BaseModel, validator, Field
from datetime import timedelta, datetime


class Player(BaseModel):
    """
    A class representing a player in the game.

    Attributes:
    -----------
    id : str
        A unique identifier for the player.
    handle : str
        The player's name or handle.
    avatar : str
        A base64 encoded string representing the player's avatar image.
    score : int
        The player's current score.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    handle: str
    avatar: str
    score: int


class Round(BaseModel):
    """
    A class representing a round in the game.

    Attributes:
    -----------
    id : str
        A unique identifier for the round.
    emoji : str
        A string representation of the emoji associated with this round.
    movie_name : str
        The name of the movie associated with this round.
    start_time : datetime
        The start time of the round.
    results: dict[str:str]
        The dictionary of player id and whether they submitted right or wrong answer.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    emoji: str
    movie_name: str
    start_time: datetime | None
    end_time: datetime | None
    results: dict[str:str]


class Game(BaseModel):
    """
    A class representing a game.

    Attributes:
    -----------
    id : str
        A unique identifier for the game.
    users_count : int
        The maximum number of players allowed in the game.
    round_count : int
        The number of rounds in the game.
    round_duration : timedelta
        The duration of each round.
    created_by : str
        The ID of the player who created the game.
    players : list[Player]
        A list of players in the game.
    rounds : list[Round]
        A list of rounds in the game.
    results : list[dict[str:str]]
        A list of dictionary which contains ID of the players as keys and scores as values.
    Raises:
    -------
    ValueError
        If `users_count` or `round_count` is not a positive integer, or if `players` or `rounds` is empty.

    Notes:
    ------
    `created_by` should be the `id` of one of the players in `players`.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    users_count: int = 10
    round_count: int = 10
    round_duration: timedelta = timedelta(minutes=1)
    created_by: str  # Player.id
    players: list[Player]
    rounds: list[Round]
    results: list[dict[str:str]]

    @validator('users_count', 'round_count')
    def must_be_positive(self, value):
        if value <= 0:
            raise ValueError('must be a positive integer')
        return value

    @validator('players', 'rounds')
    def must_not_be_empty(self, value):
        if not value:
            raise ValueError('must not be empty')
        return value
