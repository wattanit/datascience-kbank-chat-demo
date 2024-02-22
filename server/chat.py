from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel
from server.db import load_chats, save_chats, find_chat, create_chat, update_chat

router = APIRouter()

class NewChatPayload(BaseModel):
    user_id: int

@router.post("/api/chat")
async def post_chat(body: NewChatPayload):
    new_chat = await create_chat(body.user_id)
    return new_chat

@router.get("/api/chat/:id")
async def get_chat(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat

@router.get("/api/chat/:id/message")
async def get_chat_messages(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["chat_messages"]

class NewChatMessagePayload(BaseModel):
    user_id: int
    message: str

@router.post("/api/chat/:id/message")
async def create_chat_message(id: int, body: NewChatMessagePayload):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        new_chat_message = {
            "type": "user",
            "message": body.message
        }
        chat["chat_messages"].append(new_chat_message)
        await update_chat(chat)
        return new_chat_message

async def append_chat_message(chat_id: int, message_type: str, message: str):
    chat = await find_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat

@router.get("/api/chat/:id/assistant")
async def get_chat_assistant(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["assistant_logs"]
