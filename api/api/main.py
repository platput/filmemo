from datetime import timedelta

from fastapi import FastAPI, WebSocket, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware

from api.bal.game_manager import GameManager
from api.errors.database import GameNotFoundError
from api.models.game import CreateGameResponse, AddPlayerResponse, APIResponse, VerifyGameResponse

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_mgr = GameManager()


@app.get("/")
async def root():
    return {"message": "Welcome to filmemo's API"}


@app.post("/game/create")
async def create_game(request: Request):
    data = await request.json()
    game = game_mgr.create_game(
        handle=data.get("handle"),
        avatar=data.get("avatar"),
        user_count=int(data.get("user_count")),
        round_count=int(data.get("round_count")),
        round_duration=timedelta(minutes=int(data.get("round_duration")))
    )
    return CreateGameResponse(
        status="OK",
        game_id=game.id,
        created_by_player=game.created_by
    )


@app.post("/player/add")
async def add_player(request: Request):
    data = await request.json()
    player = game_mgr.add_player(
        game_id=data.get("game_id"),
        handle=data.get("handle"),
        avatar=data.get("avatar"),
    )
    return AddPlayerResponse(
        status="OK",
        player_id=player.id
    )


@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await game_mgr.join_game(
        game_id=game_id,
        player_id=player_id,
        websocket=websocket
    )
    await game_mgr.start_round_if_everyone_joined(game_id=game_id)


@app.post("/game/submit")
async def submit_answer(request: Request):
    data = await request.json()
    game_mgr.submit_guess(
        game_id=data.get("game_id"),
        round_id=data.get("round_id"),
        player_id=data.get("player_id"),
        movie_name=data.get("movie_name"),
    )
    return APIResponse(status="OK")


@app.post("/game/verify")
async def check_if_game_id_is_valid(request: Request):
    data = await request.json()
    game_id = data.get("game_id")
    game = None
    try:
        is_valid, game = game_mgr.is_game_valid(game_id)
    except GameNotFoundError:
        is_valid = False
    if is_valid:
        return VerifyGameResponse(
            status="OK",
            game_id=game_id,
            user_count=game.user_count,
            round_count=game.round_count,
            round_duration=game.round_duration,
            created_by=game.created_by
        )
    else:
        raise HTTPException(status_code=404, detail="Invalid Game")
