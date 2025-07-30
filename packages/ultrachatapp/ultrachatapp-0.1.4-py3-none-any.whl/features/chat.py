
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# import json
# from datetime import datetime
# from threading import Thread, Lock
# from ultrachatapp.database_client import DatabaseClient
# import random
# import string

# router = APIRouter()
# ACTIVE_USERS = {}
# CHAT_HISTORY = {}
# chat_lock = Lock()

# class ChatHandler:
#     def __init__(self, websocket: WebSocket, username: str):
#         self.websocket = websocket
#         self.username = username
#         self.database_client = DatabaseClient()

#     def generate_encryption_key(self):
#         """Generate a random encryption key and ID"""
#         key_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
#         encrypted_message = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))  # Placeholder for encryption logic
#         return {
#             "algorithm": "AES-256",
#             "key_id": key_id,
#             "encrypted_message": encrypted_message
#         }

#     async def connect(self):
#         """Handle WebSocket connection"""
#         await self.websocket.accept()
#         ACTIVE_USERS[self.username] = self.websocket

#     async def disconnect(self):
#         """Handle WebSocket disconnection"""
#         del ACTIVE_USERS[self.username]

#     def handle_message(self, sender: str, receiver: str, message: str):
#         """Handle and log message, including encryption"""
#         chat_id = f"{sender}_{receiver}"
        
#         # Encryption logic (automatically handled)
#         encryption_details = self.generate_encryption_key()

#         with chat_lock:
#             if chat_id not in CHAT_HISTORY:
#                 CHAT_HISTORY[chat_id] = []
#             CHAT_HISTORY[chat_id].append({
#                 "sender_id": sender,
#                 "receiver_id": receiver,
#                 "message": message,
#                 "timestamp": datetime.now().isoformat(),
#                 "encryption": encryption_details
#             })

#         # Send the message to the receiver (if they are connected)
#         recipient_socket = ACTIVE_USERS.get(receiver)
#         if recipient_socket:
#             recipient_socket.send_text(json.dumps({
#                 "sender_id": sender,
#                 "receiver_id": receiver,
#                 "message": message,
#                 "timestamp": datetime.now().isoformat(),
#                 "encryption": encryption_details
#             }))
    
#     async def listen(self):
#         """Listen for incoming messages"""
#         try:
#             while True:
#                 data = await self.websocket.receive_text()
#                 message = json.loads(data)
#                 # Using sender_id, receiver_id, and message from the received data
#                 Thread(target=self.handle_message, args=(
#                     message["sender_id"], message["receiver_id"], message["message"]
#                 )).start()
#         except WebSocketDisconnect:
#             await self.disconnect()
