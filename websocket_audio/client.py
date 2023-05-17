import asyncio
import websockets
import pyaudio

# WebSocket URL сервера
server_url = "ws://5.128.148.231:11000/ws"

# Параметры захвата и воспроизведения аудио
sample_rate = 44100
frames_per_buffer = 1024
channels = 2
audio = pyaudio.PyAudio()
stream = audio.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        output=True,
        frames_per_buffer=frames_per_buffer
    )

# Функция обратного вызова для отправки аудио фрагмента через WebSocket
async def send_audio_fragment(fragment, websocket):
    print(fragment)
    await websocket.send(fragment)

# Функция обратного вызова для воспроизведения полученного аудио фрагмента
def play_audio_fragment(fragment):
    # Воспроизводим аудио фрагмент с помощью PyAudio
    
    
    stream.write(fragment)
    stream.close()

async def receive_audio_stream(websocket):
    # Цикл для получения аудио фрагментов от сервера
    try:
        async for fragment in websocket:
            # Воспроизведение полученного аудио фрагмента
            play_audio_fragment(fragment)
    except websockets.exceptions.ConnectionClosedError:
        print("WebSocket connection closed unexpectedly.")

async def capture_and_send_audio(websocket):
    # Инициализация PyAudio


    # Захват аудио с микрофона
    

    # Отправка аудио фрагментов в цикле
    # while True:
        # Чтение аудио фрагмента с микрофона
    fragment = stream.read(frames_per_buffer)
    await send_audio_fragment(fragment, websocket)

async def connect_and_receive_audio_stream():
    async with websockets.connect(server_url) as websocket:
        # Создание задачи для получения аудио потока
        receive_task = asyncio.create_task(receive_audio_stream(websocket))

        # Захват и отправка аудио с микрофона
        await capture_and_send_audio(websocket)

        # Ожидание завершения задачи получения аудио потока
        await receive_task

# Запуск программы
asyncio.run(connect_and_receive_audio_stream())
