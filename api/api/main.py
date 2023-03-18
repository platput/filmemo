from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to filmemo's API"}


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
