import asyncio
import logging
from datetime import timedelta

from fastapi import FastAPI, WebSocket, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedError

from api.bal.game_manager import GameManager
from api.constants import LogConstants
from api.errors.database import GameNotFoundError
from api.errors.game import RoundNotExistsError, RoundAlreadyEndedError, ActionNotPermittedError
from api.models.game import CreateGameResponse, AddPlayerResponse, APIResponse, VerifyGameResponse, \
    GetGameWithResultsResponse


logger = logging.getLogger(LogConstants.APP_NAME)
logger.setLevel(logging.INFO)


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
    return {"message": "Welcome to filmemo's API", "version": "1.0.2"}


@app.post("/game/create")
async def create_game(request: Request):
    data = await request.json()
    game = await game_mgr.create_game(
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


@app.post("/game/start")
async def start_game(request: Request):
    data = await request.json()
    try:
        await game_mgr.start_round_if_everyone_joined(
            game_id=data.get("game_id"),
            player_id=data.get("player_id"),
            force_start=True
        )
        return APIResponse(
            status="OK",
        )
    except ActionNotPermittedError as e:
        raise HTTPException(status_code=404, detail=e)


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

    while True:
        try:
            await asyncio.sleep(1)
            message_to_send = {
                "status": "success",
                "message": "heartbeat",
                "message_type": "heartbeat"
            }
            await websocket.send_json(message_to_send)
        except ConnectionClosedError:
            break


@app.post("/game/submit")
async def submit_answer(request: Request):
    data = await request.json()
    try:
        await game_mgr.submit_guess(
            game_id=data.get("game_id"),
            round_id=data.get("round_id"),
            player_id=data.get("player_id"),
            movie_name=data.get("movie_name"),
        )
        return APIResponse(status="OK")
    except RoundNotExistsError:
        raise HTTPException(status_code=404, detail="Invalid Round")
    except RoundAlreadyEndedError:
        raise HTTPException(status_code=404, detail="Round Ended")


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


@app.post("/game/results")
async def get_game(request: Request):
    data = await request.json()
    game_id = data.get("game_id")
    game = game_mgr.get_game_with_results(game_id)
    if game.results:
        return GetGameWithResultsResponse(
            status="OK",
            game=game
        )
    else:
        raise HTTPException(status_code=404, detail="Invalid Game")
