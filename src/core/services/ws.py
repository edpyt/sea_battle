from fastapi import WebSocket


async def sea_ws(websocket: WebSocket, username: str, room_name: str) -> None:
    """Main logic with sea battle websockets"""
    ...
