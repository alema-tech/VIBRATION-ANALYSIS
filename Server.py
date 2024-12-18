import asyncio
import websockets
import json

# Store vibration data
vibration_data = []

# WebSocket handler
async def handler(websocket, path):
    global vibration_data
    async for message in websocket:
        try:
            # Parse JSON message
            data = json.loads(message)
            vibration_data.append(data)
            print(f"Received: {data}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# Start WebSocket server
async def main():
    async with websockets.serve(handler, "0.0.0.0", 9090):
        print("WebSocket server started at ws://0.0.0.0:9090")
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
