import asyncio
import websockets
import cv2
from datetime import datetime

# Словарь для хранения подключенных клиентов
clients = set()

# Функция для отправки видео всем подключенным клиентам


async def send_video(video):
    # Проходимся по всем подключенным клиентам и отправляем видео
    for client in clients:
        await client.send(video)

# Обработчик нового подключения клиента


async def handle_client(websocket, path):
    # Добавляем клиента в список подключенных
    clients.add(websocket)
    try:
        while True:
            # Получаем видео от клиента
            video = await websocket.recv()
            current_dateTime = datetime.now()
            print("recv:")
            print(current_dateTime)
            # Отправляем видео всем остальным клиентам
            await send_video(video)
            current_dateTime = datetime.now()
            print("send:")
            print(current_dateTime)
    finally:
        # Удаляем клиента из списка подключенных при разрыве соединения
        clients.remove(websocket)

# Функция запуска сервера


async def start_server():
    server = await websockets.serve(handle_client, "0.0.0.0", 8000)

    # Бесконечный цикл для ожидания подключений
    await server.wait_closed()

# Запуск сервера
asyncio.get_event_loop().run_until_complete(start_server())
