import asyncio
import websockets
import sounddevice as sd
import soundfile as sf

# WebSocket URL сервера
server_url = "ws://5.128.148.231:11000/ws"

# Параметры захвата и воспроизведения аудио
sample_rate = 44100
# Длительность каждого фрагмента (в секундах)
duration = 0.1
input_channels = 1
output_channels = 2

# Функция обратного вызова для отправки аудио фрагмента через WebSocket


async def send_audio_fragment(fragment, websocket):
    await websocket.send(fragment)


async def send_audio_stream(websocket):
    # Начинаем захват аудио с микрофона
    with sd.InputStream(callback=lambda indata, frames, time, status: send_audio_fragment(indata.copy(), websocket),
                        channels=input_channels,
                        samplerate=sample_rate):
        # Продолжаем отправку фрагментов в цикле
        while True:
            await asyncio.sleep(duration)

# Функция обратного вызова для воспроизведения полученного аудио фрагмента


def play_audio_fragment(fragment):
    # Сохраняем аудио фрагмент во временный файл
    temp_file = "temp_audio.wav"
    sf.write(temp_file, fragment, sample_rate)

    # Воспроизводим аудио фрагмент с помощью sounddevice
    data, _ = sf.read(temp_file, dtype="float32")
    sd.play(data, samplerate=sample_rate, channels=output_channels)
    sd.wait()


async def receive_audio_stream(websocket):
    # Цикл для получения аудио фрагментов от сервера
    try:
        async for fragment in websocket:
            # Воспроизведение полученного аудио фрагмента
            play_audio_fragment(fragment)
    except websockets.exceptions.ConnectionClosedOK:
        print("Server connection closed.")


async def connect_and_send_receive_audio_stream():
    async with websockets.connect(server_url) as websocket:
        send_task = asyncio.create_task(send_audio_stream(websocket))
        receive_task = asyncio.create_task(receive_audio_stream(websocket))
        await asyncio.gather(send_task, receive_task)

# Запускаем цикл событий для выполнения асинхронной программы
asyncio.run(connect_and_send_receive_audio_stream())
