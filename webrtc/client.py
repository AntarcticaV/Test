import asyncio
import cv2
import websockets
import json
import asyncio
import base64


async def receive_video(websocket):
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if data["type"] == "video":
                frame_data = data["data"]
                frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                cv2.imshow("Received Video", frame)
                cv2.waitKey(1)
        except websockets.exceptions.ConnectionClosed:
            break


async def send_video(websocket):
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        if not ret:
            break

        # Преобразование видео-кадра в байты
        _, frame_data = cv2.imencode('.jpg', frame)
        frame_bytes = base64.b64encode(frame_data).decode('utf-8')

        # Отправка видео-кадра на сервер
        await websocket.send(json.dumps({"type": "video", "data": frame_bytes}))
        await asyncio.sleep(0.06)

    capture.release()


async def main():
    uri = "ws://localhost:8000/"
    async with websockets.connect(uri) as websocket:
        receive_task = asyncio.ensure_future(receive_video(websocket))
        send_task = asyncio.ensure_future(send_video(websocket))
        await asyncio.wait([receive_task, send_task], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())
