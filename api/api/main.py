from datetime import timedelta

from fastapi import FastAPI, WebSocket, Request

from api.bal.game_manager import GameManager
from api.models.game import CreateGame, AddPlayer, APIResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to filmemo's API"}


@app.post("/game/create")
async def create_game(request: Request):
    data = await request.json()
    game_mgr = GameManager()
    game = game_mgr.create_game(
        handle=data.get("handle"),
        avatar=data.get("avatar"),
        user_count=int(data.get("user_count")),
        round_count=int(data.get("round_count")),
        round_duration=timedelta(seconds=int(data.get("round_duration")))
    )
    return CreateGame(
        status="OK",
        game_id=game.id,
        created_player_id=game.created_by
    )


@app.post("/player/add")
async def add_player(request: Request):
    data = await request.json()
    game_mgr = GameManager()
    player = game_mgr.add_player(
        game_id=data.get("game_id"),
        handle=data.get("handle"),
        avatar=data.get("avatar"),
    )
    return AddPlayer(
        status="OK",
        player_id=player.id
    )


@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    game_mgr = GameManager()
    await game_mgr.join_game(
        game_id=game_id,
        player_id=player_id,
        websocket=websocket
    )
    await game_mgr.start_round_if_everyone_joined(game_id=game_id)


@app.post("/game/submit")
async def submit_answer(request: Request):
    data = await request.json()
    game_mgr = GameManager()
    game_mgr.submit_guess(
        game_id=data.get("game_id"),
        round_id=data.get("round_id"),
        player_id=data.get("player_id"),
        movie_name=data.get("movie_name"),
    )
    return APIResponse(status="OK")
