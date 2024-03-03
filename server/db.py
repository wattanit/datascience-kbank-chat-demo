import json

#### DATABASE SIMULATION ####
# load user data from data/users.json, simulating a database
USER_DATA_PATH = 'data/users.json'

Class UserDB:
    def __init__(self, db_path):
        self.data: User[] = []
        self.db_path = db_path
        self.load_from_file(db_path)

    def load_from_file(self, db_path) -> None:
        with open(db_path, 'r') as f:
            user_json = json.load(f)

            for item in user_json:
                user = User.from_dict(item)
                self.data.append(user)

    def save_to_file(self, db_path) -> None:
        user_json = []
        for user in self.data:
            item = user.get_as_dict()
            user_json.append(item)

            with open(db_path, 'w') as f:
                json.dump(user_json, f, indent=4)

    def get_user_by_id(self, id: int) -> User|None:
        for user in self.data:
            if user.id == id:
                return user

    def get_all_users_as_dict(self) -> dict[]:
        users: dict[] = []
        for user in self.data:
            users.append(user.get_as_dict())
        return users

Class User:
    def __init__(self, name, password, description, segment, npl_status):
        self.id = 0
        self.name = name
        self.password = password
        self.description = description
        self.segment = segment
        self.npl_status = npl_status

    def get_as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
            "description": self.description,
            "customer_segment": self.segment,
            "NPL_status": self.npl_status
        }

    @staticmethod
    def from_dict(data) -> User:
        new_user = User(
            data["name"],
            data["password"],
            data["description"],
            data["customer_segment"],
            data["NPL_status"]
        )
        new_user.id = data["id"]
        return new_user

# load chat sessions from data/chats.json, simulating a database
CHAT_DATA_PATH = 'data/chats.json'

class ChatDB:
    def __init__(self, db_path):
        self.data : Chat[] = []
        self.db_path = db_path
        self.load_from_file(db_path)

    def load_from_file(self, db_path) -> None:
        with open(db_path, 'r') as f:
            chat_json = json.load(f)

            for item in chat_json:
                chat = Chat.from_dict(item)
                self.data.append(chat)

    def save_to_file(self, db_path) -> None:
        chat_json = []
        for chat in self.data:
            item = chat.get_as_dict()
            chat_json.append(item)

            with open(db_path, 'w') as f:
                json.dump(chat_json, f, indent=4)

    def get_last_chat(self) -> Chat|None: 
        if len(self.data)>0:
            return self.data[-1]

    def get_chat_by_id(self, id: int) -> Chat|None:
        for chat in self.data:
            if chat.id == id:
                return chat

    def update_chat(self, chat: Chat, persist=True) -> None:
        for (index, c) in enumerate(self.data):
            if c.id == chat.id:
                self.data[index] = chat

                if persist:
                    self.save_to_file(self.db_path)

                return

    def add_chat(self, chat: Chat, persist=True) -> None:
        last_chat = self.get_last_chat()
        if last_chat:
            chat.id = last_chat.id + 1
        else:
            chat.id = 1

        self.data.append(chat)

        if persist:
            self.save_to_file(self.db_path)

    def delete_chat(self, id: int|None = None, chat: Chat|None = None, persist=True) -> None:
        if id:
            for (index, c) in enumerate(self.data):
                if c.id == id:
                    del self.data[index]
                    if persist:
                        self.save_to_file(self.db_path)
                    return
        elif chat:
            for (index, c) in enumerate(self.data):
                if c.id == chat.id:
                    del self.data[index]
                    if persist:
                        self.save_to_file(self.db_path)
                    return

class Chat:
    def __init__(self, chat_id, user_id, thread_id):
        self.id: int = chat_id
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

user_db = UserDB(USER_DATA_PATH)
chat_db = ChatDB(CHAT_DATA_PATH)

async def create_chat(user_id: int, thread_id: str) -> dict:
    new_chat = new Chat(0, user_id, thread_id)
    chat_db.add_chat(new_chat)
    return new_chat

async def update_chat(chat: Chat):
    chat_db.update_chat(chat)

async def delete_chat(id: int):
    chat_db.delete_chat(id=id)
