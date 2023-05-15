import asyncio
import cv2
import websockets
import numpy as np

# Функция для отправки видео с веб-камеры на сервер


async def send_video_to_server():
    # Открытие видео-захвата с помощью OpenCV
    cap = cv2.VideoCapture(0)

    # Проверка успешного открытия камеры
    if not cap.isOpened():
        print("Не удалось открыть камеру")
        return

    # Цикл для чтения и отправки кадров видео
    while True:
        # Чтение кадра с веб-камеры
        ret, frame = cap.read()

        # Кодирование кадра в формат JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Преобразование кадра в байты для отправки
        video_bytes = jpeg.tobytes()

        # Отправка кадра на сервер
        async with websockets.connect('ws://localhost:8765') as websocket:
            await websocket.send(video_bytes)

    # Освобождение ресурсов после завершения
    cap.release()

# Функция для получения потокового видео с сервера


async def receive_video_from_server():
    async with websockets.connect('ws://localhost:8765') as websocket:
        while True:
            # Получение потокового видео от сервера
            video_bytes = await websocket.recv()

            # Декодирование видео из байтов в кадр
            frame = cv2.imdecode(np.frombuffer(
                video_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

            # Отображение видео в окне
            cv2.imshow('Received Video', frame)
            cv2.waitKey(1)

# Запуск клиентского приложения
if __name__ == "__main__":
    # Создание задач для отправки и получения видео
    send_task = asyncio.ensure_future(send_video_to_server())
    receive_task = asyncio.ensure_future(receive_video_from_server())

    # Запуск цикла обработки событий asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(send_task, receive_task))

    # Освобождение ресурсов после завершения
    cv2.destroyAllWindows()
