import requests
import websocket
import asyncio


with requests.Session() as session:
    data = {"username": "КЭШ", "password": "wasd123!"}
    url = "https://bigeny.ru/api/auth/login"
    r = session.post(url, json=data)

    print(r.content)
    print(r.json())
    token = r.json()
    while True:
        ws = websocket.WebSocket()
        ws.connect("wss://bigeny.ru/api/messages/ws/7")

        # Добавление заголовков (например, токена авторизации) к запросу
        ws.send()

        # Запуск WebSocket соединения
