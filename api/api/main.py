from fastapi import FastAPI, WebSocket, Request

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to filmemo's API"}


@app.post("/game/create")
async def create_game(request: Request):
    data = request.json()


@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
