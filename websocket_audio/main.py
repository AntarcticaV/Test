from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio

# Список активных подключений
connections = set()

# Создаем экземпляр FastAPI
app = FastAPI()

# HTML-страница с формой для тестирования
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Audio Streaming Server</title>
    </head>
    <body>
        <h1>Audio Streaming Server</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" placeholder="Enter message" required>
            <button type="submit">Send</button>
        </form>
        <script>
            var socket = new WebSocket("ws://localhost:8000/ws");

            function sendMessage(event) {
                event.preventDefault();
                var messageInput = document.getElementById("messageText");
                var message = messageInput.value;
                socket.send(message);
                messageInput.value = '';
            }
        </script>
    </body>
</html>
"""

# WebSocket обработчик


async def websocket_handler(websocket: WebSocket):
    await websocket.accept()

    # Добавляем новое подключение в список активных подключений
    connections.add(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            # Отправляем сообщение всем подключенным пользователям, кроме отправителя
            for connection in connections:
                if connection != websocket:
                    await connection.send_text(message)
    except WebSocketDisconnect:
        # Удаляем закрытое подключение из списка активных подключений
        connections.remove(websocket)

# Маршрут для WebSocket соединения


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)

# Маршрут для HTML-страницы


@app.get("/")
async def get():
    return HTMLResponse(html)

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
