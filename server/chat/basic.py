from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import logging
from server.db import CHAT_DB, Chat

logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter()

class NewChatPayload(BaseModel):
    user_id: int

@router.post("/api/chat")
async def post_chat(body: NewChatPayload):
    logging.info("Creating new chat for user: {}".format(body.user_id))

    # call OpenAI to create a new thread
    response = requests.post('https://api.openai.com/v1/threads', data={}, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
        })

    if response.status_code != 200:
        logging.warning("OpenAI thread creation failed: {}".format(response.status_code))
        raise HTTPException(status_code=500, detail="OpenAI thread creation failed")

    response = response.json()
    thread_id = response["id"]
    logging.info("Created OpenAI thread: {}".format(thread_id))

    new_chat = Chat(0, body.user_id, thread_id)
    new_chat.add_assistant_log("new_chat", "New chat created")
    new_chat = CHAT_DB.add_chat(new_chat)
    logging.info("Created new chat: {}".format(new_chat))

    return new_chat

@router.get("/api/chat/{id}")
async def get_chat(id: int):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return chat

@router.delete("/api/chat/{id}")
async def delete_chat(id: int):
    chat = CHAT_DB.get_chat_by_id(id)

    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # call OpenAI delete thread
    thread_id = chat.openai_thread_id
    response = requests.delete(f'https://api.openai.com/v1/threads/{thread_id}', headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
        })

    if response.status_code != 200:
        logging.warning("OpenAI thread deletion failed: {}".format(response.status_code))
        return {}
    
    response = response.json()
    if response["deleted"]:
        logging.info("Deleted OpenAI thread: {}".format(thread_id))

    # delete chat from database
    CHAT_DB.delete_chat(id)
    logging.info("Deleted chat: {}".format(id))
    
    return chat

@router.get("/api/chat/{id}/message")
async def get_chat_messages(id: int):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat.chat_messages

@router.get("/api/chat/{id}/assistant")
async def get_chat_assistant(id: int):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat.assistant_logs