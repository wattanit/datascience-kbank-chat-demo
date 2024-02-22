from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel

router = APIRouter()

#### DATABASE SIMULATION ####
# load chat sessions from data/chats.json, simulating a database
def load_chats():
    with open('data/chats.json') as f:
        chats = json.load(f)
    return chats

def save_chats(chats):
    with open('data/chats.json', 'w') as f:
        json.dump(chats, f)

async def find_chat(id: int) -> dict|None:
    chats = load_chats()
    chat = next((chat for chat in chats if chat["id"] == id), None)
    return chat

async def create_chat(user_id: int) -> dict:
    # find the last chat id
    chats = load_chats()
    last_chat = chats[-1]
    last_chat_id = last_chat["id"]
    new_chat_id = last_chat_id + 1

    new_chat = {
        "id": new_chat_id,
        "user_id": user_id,
        "chat_messages": [],
        "assistant_logs": []
        }

    chats.append(new_chat)
    save_chats(chats)
    return new_chat

async def update_chat(chat: dict):
    chats = load_chats()
    chat_index = next((index for (index, c) in enumerate(chats) if c["id"] == chat["id"]), None)
    chats[chat_index] = chat
    save_chats(chats)

#############################

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
    print(id)
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        new_chat_message = {
            "type": "user",
            "message": body.message
        }
        print(new_chat_message)
        chat["chat_messages"].append(new_chat_message)
        await update_chat(chat)
        return new_chat_message
    
    # return {"message": "Create chat message not supported"}


    # return append_chat_message(id, "user", "whattt")

async def append_chat_message(chat_id: int, message_type: str, message: str):
    chat = await find_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat
    

    # chat = await find_chat(id)
    # if chat is None:
    #     raise HTTPException(status_code=404, detail="Chat not found")
    # else:
    #     if message_type == "user":
    #         chat_message = {
    #             "type": "user",
    #             "message": message
    #         }
    #     elif message_type == "bot":
    #         chat_message = {
    #             "type": "bot",
    #             "message": message
    #         }
    #     else: 
    #         raise HTTPException(status_code=400, detail="Invalid message type")
        
    #     chat["chat_messages"].append(chat_message)
    #     await update_chat(chat)
    #     return chat_message


@router.get("/api/chat/:id/assistant")
async def get_chat_assistant(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["assistant_logs"]
