import uuid
from typing import Dict, DefaultDict

from pydantic import BaseModel, validator, Field
from datetime import timedelta, datetime


class Player(BaseModel):
    """
    Player model.

    Attributes:
        id (str): Unique identifier for the player.
        handle (str): Handle of the player.
        avatar (str): Avatar of the player.
        score (int): Score of the player.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    handle: str
    avatar: str
    score: int


class Round(BaseModel):
    """
    Round model.

    Attributes:
        id (str): Unique identifier for the round.
        emoji (str): Emoji for the round.
        movie_name (str): Name of the movie.
        start_time (datetime | None): Start time of the round.
        end_time (datetime | None): End time of the round.
        results (dict[str:bool]): Results of the round.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    emoji: str
    movie_name: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    results: Dict[str:bool] = {}


class Game(BaseModel):
    """
    Game model.

    Attributes:
        id (str): Unique identifier for the game.
        user_count (int): Number of users.
        round_count (int): Number of rounds.
        round_duration (timedelta): Duration of each round.
        created_by (str | None): Creator of the game.
        players (list[Player]): Players in the game.
        rounds (list[Round]): Rounds in the game.
        results (dict[str:str]): Results of the game.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    user_count: int = 10
    round_count: int = 10
    round_duration: timedelta = timedelta(minutes=1)
    created_by: str | None  # Player.id
    players: list[Player] = []
    rounds: list[Round] = []
    results: Dict = {}

    @validator('user_count', 'round_count')
    def must_be_positive(cls, value: int):
        if value <= 0:
            raise ValueError('must be a positive integer')
        return value

    @validator('players', 'rounds')
    def must_not_be_empty(cls, value: list[Player] | list[Round]):
        if not value:
            raise ValueError('must not be empty')
        return value


class APIResponse(BaseModel):
    """
    Base response model for all api endpoints
    Attributes:
        status: Response status to indicate success or failure
    """
    status: str


class CreateGame(APIResponse):
    """
    Response model for the create-game api endpoint
    Attributes:
        status: Response status to indicate success or failure
        game_id: ID of the created game
        created_by_player: ID of the player who created the game
    """
    game_id: str
    created_by_player: str


class AddPlayer(APIResponse):
    """
    Response model for the add-player api endpoint
    Attributes:
        status: Response status to indicate success or failure
        player_id: ID of the created game
    """
    player_id: str
