from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.api.services.event_broker import get_event_broker
from app.api.dtos.events import BaseEvent
import json

router = APIRouter(tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.broker = get_event_broker()
        self.broker.subscribe(self.handle_broker_event)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def handle_broker_event(self, event: BaseEvent):
        message = event.model_dump_json()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection might have dropped mid-send
                pass

manager = ConnectionManager()

@router.websocket("/ws/v1/runtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
