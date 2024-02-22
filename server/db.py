import json

#### DATABASE SIMULATION ####
# load user data from data/users.json, simulating a database
def load_users():
    with open('data/users.json') as f:
        users = json.load(f)
    return users

async def find_user(id: int):
    users = load_users()
    user = next((user for user in users if user["id"] == id), None)
    return user

# load chat sessions from data/chats.json, simulating a database
def load_chats():
    with open('data/chats.json') as f:
        chats = json.load(f)
    return chats

def save_chats(chats):
    with open('data/chats.json', 'w') as f:
        json.dump(chats, f, indent=4)

async def find_chat(id: int) -> dict|None:
    chats = load_chats()
    chat = next((chat for chat in chats if chat["id"] == id), None)
    return chat

async def create_chat(user_id: int, thread_id: str) -> dict:
    # find the last chat id
    chats = load_chats()
    if len(chats)>0:
        last_chat = chats[-1]
        last_chat_id = last_chat["id"]
        new_chat_id = last_chat_id + 1
    else:
        new_chat_id = 1

    new_chat = {
        "id": new_chat_id,
        "user_id": user_id,
        "openai_thread_id": thread_id,
        "chat_messages": [],
        "assistant_logs": [],
        "status": "done"
        }

    chats.append(new_chat)
    save_chats(chats)
    return new_chat

async def update_chat(chat: dict):
    chats = load_chats()
    chat_index = next((index for (index, c) in enumerate(chats) if c["id"] == chat["id"]), None)
    chats[chat_index] = chat
    save_chats(chats)

async def delete_chat(id: int):
    chats = load_chats()
    chat_index = next((index for (index, c) in enumerate(chats) if c["id"] == id), None)
    del chats[chat_index]
    save_chats(chats)