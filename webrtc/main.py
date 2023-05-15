from fastapi import FastAPI, WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription
from av import VideoFrame
import threading
import json

app = FastAPI()


class WebRTCClient:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.peer_connection = RTCPeerConnection()
        self.video_track = None
        self.audio_track = None
        self.candidate_queue = []
        self.is_offer_set = False
        self.lock = threading.Lock()

    async def start(self):
        self.peer_connection.on("track", self.on_track)
        self.peer_connection.on(
            "iceconnectionstatechange", self.on_ice_connection_state_change)

    async def on_track(self, track):
        if track.kind == "video":
            self.video_track = track
        elif track.kind == "audio":
            self.audio_track = track

    async def on_ice_connection_state_change(self):
        if self.peer_connection.iceConnectionState == "disconnected":
            await self.websocket.close()

    async def handle_offer(self, offer: RTCSessionDescription):
        self.lock.acquire()
        await self.peer_connection.setRemoteDescription(offer)
        answer = await self.peer_connection.createAnswer()
        await self.peer_connection.setLocalDescription(answer)
        await self.websocket.send_json({"type": "answer", "sdp": self.peer_connection.localDescription.sdp})
        self.is_offer_set = True
        while len(self.candidate_queue) > 0:
            candidate = self.candidate_queue.pop(0)
            await self.websocket.send_json({"type": "candidate", "candidate": candidate})
        self.lock.release()

    async def handle_candidate(self, candidate: dict):
        self.lock.acquire()
        if self.is_offer_set:
            await self.peer_connection.addIceCandidate(candidate)
        else:
            self.candidate_queue.append(candidate)
        self.lock.release()


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    client = WebRTCClient(websocket)
    await websocket.accept()
    await client.start()
    while True:
        try:
            print("json")
            data = await websocket.receive_json()
            data["data"] = bytes(data["data"])
            print("1")
            if data["type"] == "offer":
                await client.handle_offer(RTCSessionDescription(sdp=data["sdp"], type="offer"))
                print("2")
            elif data["type"] == "candidate":
                await client.handle_candidate(data["candidate"])
                print("3")
            elif data["type"] == "frame":
                print("4")
                frame = VideoFrame.from_ndarray(data["data"], format="bgr24")
                client.video_track.frame = frame
                print("5")
        except:
            await websocket.close()
            break
