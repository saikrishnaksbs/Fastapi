"""
WEBSOCKET MULTI-CLIENT CHATROOM
===============================
This script demonstrates managing multiple WebSocket connections using a ConnectionManager.
It allows broadcasting messages to all connected clients (e.g. standard Chatroom logic).
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSocket Broadcast Chat")

# HTML page allowing multiple users to connect with a custom nickname/user ID
html_chat_client = """
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI Chatroom</title>
        <style>
            body { font-family: sans-serif; margin: 30px; }
            #messages { list-style-type: none; padding: 0; }
            #messages li { padding: 8px; margin-bottom: 5px; background: #eee; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>FastAPI Chatroom</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" placeholder="Type a message..."/>
            <button>Send</button>
        </form>
        <ul id='messages'></ul>
        <script>
            // Generate a random client ID
            var client_id = Math.floor(Math.random() * 1000);
            document.getElementById("ws-id").innerText = client_id;
            
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
            
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

# Connection Manager to track active websocket sockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        # Sends a message to every active connection in the pool
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(html_chat_client)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    await manager.broadcast(f"Client #{client_id} joined the room")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the room")

# To run this file:
# uvicorn 10_websockets.02_websocket_chat:app --reload
