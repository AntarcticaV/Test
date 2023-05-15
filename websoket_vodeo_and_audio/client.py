import cv2
import numpy as np
import pyaudio
import asyncio
import websockets
import threading

# Параметры видео и аудио
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 30
VIDEO_CODEC = cv2.VideoWriter_fourcc(*'XVID')
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHUNK_SIZE = 1024

# Конфигурация клиента
SERVER_URL = 'ws://localhost:8765'

# Открытие видео-захвата с помощью OpenCV
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
video_capture.set(cv2.CAP_PROP_FPS, VIDEO_FPS)

# Инициализация аудиозахвата
audio_stream = pyaudio.PyAudio().open(
    format=pyaudio.paInt16,
    channels=AUDIO_CHANNELS,
    rate=AUDIO_SAMPLE_RATE,
    input=True,
    frames_per_buffer=AUDIO_CHUNK_SIZE
)

# Функция для чтения и отправки видео с веб-камеры
def send_video():
    # Создание видеопотока для записи видео
    video_writer = cv2.VideoWriter('video_stream.avi', VIDEO_CODEC, VIDEO_FPS, (VIDEO_WIDTH, VIDEO_HEIGHT))

    # Цикл для чтения и отправки кадров видео
    while True:
        # Чтение кадра с веб-камеры
        ret, frame = video_capture.read()

        # Запись кадра в видеопоток
        video_writer.write(frame)

        # Кодирование кадра в формат JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Преобразование кадра в байты для отправки
        video_bytes = jpeg.tobytes()

        # Отправка кадра на сервер
        asyncio.run(send_video_to_server(video_bytes))

    # Освобождение ресурсов после завершения
    video_writer.release()

# Функция для отправки видео на сервер
async def send_video_to_server(video_bytes):
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send(video_bytes)

# Функция для отправки аудио на сервер
async def send_audio_to_server(audio_data):
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send(audio_data)

# Функция для получения потокового видео и аудио с сервера
async def receive_stream_from_server():
    async with websockets.connect(SERVER_URL) as websocket:
        while True:
            # Получение потокового видео и аудио от сервера
            stream_data = await websocket.recv()

            # Обработка полученных данных
            if stream_data.startswith('video'):
                # Получение видео из потока данных
                video_data = stream_data[6:]

                # Декодирование видео из байтов в кадр
                frame = cv2.imdecode(np.frombuffer(video_data, np.uint8), cv2.IMREAD_UNCHANGED)

                # Отображение видео в окне
                cv2.imshow('Received Video', frame)
                cv2.waitKey(1)
            elif stream_data.startswith('audio'):
                # Получение аудио из потока данных
                audio_data = stream_data[6:]

                # Воспроизведение аудио
                audio_stream.write(audio_data)

# Функция для отправки видео и аудио на сервер
async def send_stream():
    async with websockets.connect(SERVER_URL) as websocket:
        while True:
            # Чтение кадра с веб-камеры
            ret, frame = video_capture.read()

            # Кодирование кадра в формат JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)

            # Преобразование кадра в байты для отправки
            video_bytes = jpeg.tobytes()

            # Отправка видео на сервер
            await websocket.send(f'video{video_bytes}')

            # Чтение аудио-данных
            audio_data = audio_stream.read(AUDIO_CHUNK_SIZE)

            # Отправка аудио на сервер
            await websocket.send(f'audio{audio_data}')

# Запуск клиентского приложения
if __name__ == '__main__':
    # Запуск потоков для отправки и получения потокового видео и аудио
    send_thread = threading.Thread(target=asyncio.run, args=(send_stream(),))
    receive_thread = threading.Thread(target=asyncio.run, args=(receive_stream_from_server(),))
    send_thread.start()
    receive_thread.start()

    # Отображение видео с локальной камеры
    while True:
        ret, frame = video_capture.read()
        cv2.imshow('Local Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождение ресурсов после завершения
    video_capture.release()
    audio_stream.stop_stream()
    audio_stream.close()
    pyaudio.PyAudio().terminate()
    cv2.destroyAllWindows()

