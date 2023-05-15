from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        print("fggf")
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_video(self, video_frame: str, sender: WebSocket):
        for connection in self.active_connections:
            if connection != sender:
                await connection.send_text(video_frame)
                current_dateTime = datetime.now()
                with open("otus.txt", "a+") as file:
                    file.write(f"send:{current_dateTime}\n")


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            current_dateTime = datetime.now()
            with open("otus.txt", "a+") as file:
                file.write(f"recv:{current_dateTime}\n")
            await manager.broadcast_video(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
