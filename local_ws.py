import json
import random
import asyncio
import websockets


async def generate_messages(websocket, path):
    while True:
        msg_type = random.choice(["add_new_item", "deleted_item"])
        number = random.randint(0, 10)
        message = [msg_type, number]

        # Send the message over the WebSocket connection
        await websocket.send(json.dumps(message))

        # Print the message to the console
        print(f"Sent: {message}")

        await asyncio.sleep(1)  # Add some delay between messages


start_server = websockets.serve(generate_messages, "localhost", 8765)


async def main():
    await start_server
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
