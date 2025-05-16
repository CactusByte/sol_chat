from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Add CORS middleware with more permissive settings for Heroku
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = []

async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"New client connected. Total clients: {len(connected_clients)}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            for client in connected_clients:
                if client != websocket:
                    await client.send_text(data)
                    print(f"Message forwarded to another client")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"Client disconnected. Remaining clients: {len(connected_clients)}")

@app.websocket("/")
async def root_websocket(websocket: WebSocket):
    await handle_websocket(websocket)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Hello World"}
