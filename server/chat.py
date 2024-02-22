from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
from pydantic import BaseModel
from server.db import load_chats, save_chats, find_chat, create_chat, update_chat
from dotenv import load_dotenv
import os
from server.agent import process_chat
import concurrent.futures

load_dotenv()
print("LOADED API KEYS: {}".format(os.getenv("OPENAI_API_KEY")))
print("UNDERSTANDING AGENT ID: {}".format(os.getenv("OPENAI_UNDERSTANDING_AGENT_ID")))
print("RESPONSE AGENT ID: {}".format(os.getenv("OPENAI_RESPONSE_AGENT_ID")))

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
async def create_chat_message(id: int, body: NewChatMessagePayload, background_tasks: BackgroundTasks):
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

        background_tasks.add_task(process_chat,chat)
        return new_chat_message

@router.get("/api/chat/:id/assistant")
async def get_chat_assistant(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["assistant_logs"]
