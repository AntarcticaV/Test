from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import asyncio

app = FastAPI()

# Список подключенных клиентов
connected_clients = []

# Модель данных для получения потокового видео и аудио от клиента


class StreamData(BaseModel):
    type: str
    data: bytes

# Обработчик вебсокет-подключения клиента


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Добавление клиента в список подключенных
    connected_clients.append(websocket)

    try:
        while True:
            # Получение потоковых данных от клиента
            data = await websocket.receive_json()

            # Проверка типа данных (видео или аудио)
            if data['type'] == 'video':
                # Отправка видео другим подключенным клиентам
                await send_video_to_clients(websocket, data['data'])
            elif data['type'] == 'audio':
                # Отправка аудио другим подключенным клиентам
                await send_audio_to_clients(websocket, data['data'])
    except:
        # Удаление клиента из списка подключенных при обрыве соединения
        connected_clients.remove(websocket)

# Функция для отправки видео другим подключенным клиентам


async def send_video_to_clients(sender: WebSocket, video_data: bytes):
    for client in connected_clients:
        if client != sender:
            # Отправка видео клиенту
            await client.send_json({'type': 'video', 'data': video_data})

# Функция для отправки аудио другим подключенным клиентам


async def send_audio_to_clients(sender: WebSocket, audio_data: bytes):
    for client in connected_clients:
        if client != sender:
            # Отправка аудио клиенту
            await client.send_json({'type': 'audio', 'data': audio_data})
