from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []  

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        if websocket not in self.active_connections:
            self.active_connections.append(websocket) 

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)  

    async def send_message(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)  
            except Exception as e:
                print(f"Error sending message to {connection}: {e}")
