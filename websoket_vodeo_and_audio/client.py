import asyncio
import cv2
import numpy as np
import websockets
import pyaudio
import wave

# Установка параметров видео и аудио
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

# Функция для чтения видео с веб-камеры и отправки на сервер


async def send_video(stream):
    # Создание объекта видео-захвата
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # Цикл чтения и отправки кадров видео
    while True:
        # Чтение кадра с веб-камеры
        ret, frame = cap.read()

        # Кодирование кадра в формат JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        video_bytes = jpeg.tobytes()

        # Отправка кадра на сервер
        await stream.send(video_bytes)

    # Освобождение ресурсов
    cap.release()

# Функция для чтения аудио с микрофона и отправки на сервер


async def send_audio(stream):
    # Создание объекта аудио-захвата
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    # Цикл чтения и отправки аудио
    while True:
        # Чтение аудио-фрейма
        audio_data = stream.read(CHUNK_SIZE)

        # Отправка аудио-фрейма на сервер
        await stream.send(audio_data)

    # Остановка аудио-захвата
    stream.stop_stream()
    stream.close()
    audio.terminate()

# Функция для приема видео и аудио от сервера и вывода на экран


async def receive_video_and_audio(stream):
    # Создание окна для отображения видео
    cv2.namedWindow('Received Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Received Video', FRAME_WIDTH, FRAME_HEIGHT)

    # Цикл приема и отображения видео и аудио
    while True:
        # Получение данных от сервера
        data = await stream.recv()

        # Проверка типа данных
        if isinstance(data, bytes):
            # Декодирование видео-кадра из байтов в изображение
            frame = cv2.imdecode(np.frombuffer(
                data, np.uint8), cv2.IMREAD_COLOR)

            # Отображение видео-кадра
            cv2.imshow('Received Video', frame)
            cv2.waitKey(1)
        elif isinstance(data, str):
            # Воспроизведение аудио-данных
            audio_data = np.frombuffer(data, dtype=np.int16)
            play_audio(audio_data)

# Функция для воспроизведения аудио


def play_audio(audio_data):
    # Создание объекта воспроизведения аудио
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=SAMPLE_RATE, output=True)

    # Воспроизведение аудио-данных
    stream.write(audio_data.tobytes())

    # Остановка воспроизведения
    stream.stop_stream()
    stream.close()
    audio.terminate()

# Функция для запуска клиентского приложения


async def run_client():
    # Подключение к серверу
    async with websockets.connect('ws://5.128.148.231:11000') as websocket:
        # Отправка видео и аудио на сервер
        video_task = asyncio.create_task(send_video(websocket))
        audio_task = asyncio.create_task(send_audio(websocket))

        # Прием и обработка видео и аудио от сервера
        await receive_video_and_audio(websocket)

        # Ожидание завершения задач отправки видео и аудио
        await video_task
        await audio_task

# Запуск клиентского приложения
if __name__ == "__main__":
    asyncio.run(run_client())
