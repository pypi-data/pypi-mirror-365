from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
from ultrachatapp.database_client import DatabaseClient
from features.encryption import encrypt_message, decrypt_message

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, str] = {}
        self.database_client = DatabaseClient()

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accepts WebSocket connection and stores session."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.sessions[user_id] = f"session_{user_id}"

    def disconnect(self, user_id: str):
        """Removes WebSocket connection and session."""
        self.active_connections.pop(user_id, None)
        self.sessions.pop(user_id, None)

    async def send_message(self, sender_id: str, receiver_id: str, message: str):
        """Sends message to a connected user and stores it in the database."""
        if receiver_id in self.active_connections:
            await self.active_connections[receiver_id].send_text(message)
            status = "delivered"
        else:
            status = "pending"
        # Encrypt the message before storing it
        encrypted_message = encrypt_message(message)
        self.database_client.add_message(sender_id=sender_id, receiver_id=receiver_id, message=encrypted_message, status=status)

    async def broadcast(self, message: str):
        """Broadcasts a message to all connected clients."""
        for connection in self.active_connections.values():
            await connection.send_text(message)

    def get_session_id(self, user_id: str):
        """Retrieves session ID for a user."""
        return self.sessions.get(user_id)


class MessageHandler:
    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

    def send_message(self, sender_id: str, receiver_id: str, content: str):
        """Stores a sent message in the database."""
        message = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "status": "sent"
        }
        self.database_client.add_message(**message)
        return "Message stored successfully"

    def receive_messages(self, receiver_id: str):
        """Fetches messages for a recipient and updates status."""
        messages = self.database_client.get_messages_by_recipient(receiver_id)
        for msg in messages:
            # Decrypt the message content before returning it
            msg["message"] = decrypt_message(msg["message"])
            msg["status"] = "received"
        return messages

    def get_all_messages(self):
        """Retrieves all messages from the database."""
        return self.database_client.get_all_messages()
