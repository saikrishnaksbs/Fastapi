"""
WEBSOCKET BASICS
================
This script demonstrates how to configure a simple WebSocket endpoint.
To make this script fully runnable and testable, the index route "/" returns
an HTML page containing Javascript that connects to our websocket.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSocket Basics")

html_client = """
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI WebSocket Demo</title>
    </head>
    <body>
        <h1>WebSocket Echo Room</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            // Connect to the WebSocket endpoint
            var ws = new WebSocket("ws://localhost:8000/ws");
            
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

# Serve the HTML client interface
@app.get("/")
async def get_client():
    return HTMLResponse(html_client)

# Register the WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the connection
    await websocket.accept()
    try:
        while True:
            # Wait for data sent from the client
            data = await websocket.receive_text()
            # Echo the message back to the client
            await websocket.send_text(f"Server received: {data}")
    except WebSocketDisconnect:
        # Handle client connection termination cleanly
        print("[WEBSOCKET] Client disconnected.")

# To run this file:
# uvicorn 10_websockets.01_websocket_basics:app --reload
