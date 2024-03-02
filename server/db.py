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

CHAT_DATA_PATH = 'data/chats.json'

class ChatDB {
    def __init__(self):
        self.data : Chat[] = []

    def load_from_file(self, db_path):
        with open(db_path, 'r') as f:
            chat_json = json.load(f)

            for item in chat_json:
                chat = Chat.from_dict(item)
                self.data.append(chat)

    def save_to_file(self, db_path):
        chat_json = []
        for chat in self.data:
            item = chat.get_as_dict()
            chat_json.append(item)

            with open(db_path, 'w') as f:
                json.dump(chat_json, f, indent=4)

    def get_last_chat(self): 
        if len(self.data)>0:
            return self.data[-1]

    def get_chat_by_id(self, )



class Chat {
    def __init__(self, chat_id, user_id, thread_id):
        self.id = chat_id
        self.user_id = user_id
        self.openai_thread_id = thread_id
        self.chat_messages = []
        self.assistant_logs = []
        self.status = "ready"
        self.last_context = ""
        self.openai_run_id = []

    def get_as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "openai_thread_id": self.openai_thread_id,
            "chat_messages": self.chat_messages,
            "assistant_logs": self.assistant_logs,
            "status": self.status,
            "last_context": self.last_context,
            "openai_run_id": self.openai_run_id
        }

    @staticmethod
    def from_dict(data) -> Chat:
        new_chat = Chat(
            data["id"],
            data["user_id"],
            data["openai_thread_id"],
        )
        new_chat.chat_messages = data["chat_messages"]
        new_chat.assistant_logs = data["assistant_logs"]
        new_chat.status = data["status"]
        new_chat.last_context = data["last_context"]
        new_chat.openai_run_id = data["openai_run_id"]
        return new_chat
}

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
        "status": "done",
        "last_context": "",
        "openai_run_id": []
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