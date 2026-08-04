# Topic 10: WebSockets

This module covers creating real-time duplex communication endpoints using WebSockets in FastAPI.

---

## Code Walkthrough

1. **[01_websocket_basics.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/10_websockets/01_websocket_basics.py)**
   * Shows how to establish a WebSocket endpoint, receive messages from a client, and send messages back using the `WebSocket` object.
2. **[02_websocket_chat.py](file:///Users/saikrishnakuchimanchi/Downloads/Test/Fastapi/10_websockets/02_websocket_chat.py)**
   * Builds an interactive multi-client WebSocket chatroom using a connection manager to keep track of active connections and broadcast messages.

---

## WebSockets vs HTTP

Unlike standard HTTP request/response loops, WebSockets allow persistent connections:
* **HTTP**: Client requests -> Server replies (connection closes).
* **WebSocket**: Client requests upgrade -> Connection stays open -> Both can push data anytime (ideal for chat apps, stock tickers, or live collaboration tools).
