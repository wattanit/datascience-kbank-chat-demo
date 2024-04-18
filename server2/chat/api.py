import os
import time
import logging
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from server2.db import CHAT_DB, Chat

logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter()

client = OpenAI(
  organization=os.getenv("OPENAI_ORGANIZATION"),
  project=os.getenv("OPENAI_PROJECT"),
)

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
    response = client.beta.threads.delete(thread_id)
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