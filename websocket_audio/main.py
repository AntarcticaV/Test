import asyncio
import websockets
from fastapi import FastAPI
from starlette.websockets import WebSocket

app = FastAPI()
connected_clients = set()


@app.websocket("/ws")
async def audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_bytes()
            print(data)
            await broadcast(data, websocket)

    except websockets.exceptions.ConnectionClosedError:
        connected_clients.remove(websocket)


async def broadcast(data: bytes, sender: WebSocket):
    for client in connected_clients:
        if client != sender:
            await client.send_bytes(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
