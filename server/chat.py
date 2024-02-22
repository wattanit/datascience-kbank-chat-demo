from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from server.db import load_chats, save_chats, find_chat, create_chat, update_chat
from server.db import delete_chat as delete_chat_from_db
from server.agent import process_chat

load_dotenv()
print("LOADED API KEYS: {}".format(os.getenv("OPENAI_API_KEY")))
print("UNDERSTANDING AGENT ID: {}".format(os.getenv("OPENAI_UNDERSTANDING_AGENT_ID")))
print("RESPONSE AGENT ID: {}".format(os.getenv("OPENAI_RESPONSE_AGENT_ID")))

router = APIRouter()

class NewChatPayload(BaseModel):
    user_id: int

@router.post("/api/chat")
async def post_chat(body: NewChatPayload):
    print("Creating new chat for user: {}".format(body.user_id))

    # call OpenAI to create a new thread
    response = requests.post('https://api.openai.com/v1/threads', data={}, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
        })

    if response.status_code != 200:
        print(response.status_code)
        raise HTTPException(status_code=500, detail="OpenAI thread creation failed")

    response = response.json()
    thread_id = response["id"]
    print("Created OpenAI thread: {}".format(thread_id))

    new_chat = await create_chat(body.user_id, thread_id)
    print("Created new chat: {}".format(new_chat))
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
        run_context_agent = 
        process_chat(body.message, chat)

        # new_chat_message = {
        #     "type": "user",
        #     "message": body.message
        # }
        # chat["chat_messages"].append(new_chat_message)

        # # call OpenAI to add the message
        # data = {
        #     "role": "user",
        #     "content": body.message
        # }
        # response = requests.post(f'https://api.openai.com/v1/threads/{chat["openai_thread_id"]}/messages', data=json.dumps(data), headers={
        #     'Content-Type': 'application/json',
        #     'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        #     'OpenAI-Beta': 'assistants=v1'
        #     })

        # if response.status_code != 200:
        #     raise HTTPException(status_code=500, detail="OpenAI message creation failed")
        
        # response = response.json()

        # if chat["status"] == "done":
        #     chat["status"] = "running"

        #     # call OpenAI to create a new run

        # await update_chat(chat)
        # return new_chat_message

@router.get("/api/chat/:id/assistant")
async def get_chat_assistant(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["assistant_logs"]

@router.delete("/api/chat/:id")
async def delete_chat(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # call OpenAI delete thread
        thread_id = chat["openai_thread_id"]
        response = requests.delete(f'https://api.openai.com/v1/threads/{thread_id}', headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'OpenAI-Beta': 'assistants=v1'
            })

        if response.status_code != 200:
            print(response.status_code)
            return {}
        
        response = response.json()
        if response["deleted"]:
            print("Deleted OpenAI thread: {}".format(thread_id))

        # delete chat from database
        await delete_chat_from_db(id)
        print("Deleted chat: {}".format(id))

        return chat