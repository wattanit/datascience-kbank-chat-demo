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

    def add_chat(self, chat: Chat, persist=True) -> Chat:
        last_chat = self.get_last_chat()
        if last_chat:
            chat.id = last_chat.id + 1
        else:
            chat.id = 1

        self.data.append(chat)

        if persist:
            self.save_to_file(self.db_path)

        return chat

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
        self.user_id: str = user_id
        self.openai_thread_id: str = thread_id
        self.chat_messages: ChatMessage[] = []
        self.assistant_logs: AssistantLog[] = []
        self.status = "ready"
        self.last_context = ""
        self.last_promotions = ""
        self.openai_run_id: str[] = []

    def get_as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "openai_thread_id": self.openai_thread_id,
            "chat_messages": [message.get_as_dict() for message in self.chat_messages],
            "assistant_logs": [log.get_as_dict() for log in self.assistant_logs],
            "status": self.status,
            "last_context": self.last_context,
            "last_promotions": self.last_promotions,
            "openai_run_id": self.openai_run_id
        }

    @staticmethod
    def from_dict(data) -> Chat:
        new_chat = Chat(
            data["id"],
            data["user_id"],
            data["openai_thread_id"],
        )
        new_chat.chat_messages = [ChatMessage.from_dict(message) for message in data["chat_messages"]]
        new_chat.assistant_logs = [AssistantLog.from_dict(log) for log in data["assistant_logs"]]
        new_chat.status = data["status"]
        new_chat.last_context = data["last_context"]
        new_chat.last_promotions = data["last_promotions"]
        new_chat.openai_run_id = data["openai_run_id"]
        return new_chat

    def addMessage(self, user_type, message)->None:
        new_message = ChatMessage(user_type, message)
        self.chat_messages.append(new_message)

    def getLastUserMessage(self)->str|None:
        for message in reversed(self.chat_messages):
            if message.type == "user":
                return message.message
        return None

    def addAssistantLog(self, chat_type, message)->None:
        new_log = AssistantLog(chat_type, message)
        self.assistant_logs.append(new_log)

    def addRunId(self, run_id)->None:
        self.openai_run_id.append(run_id)

    def getLastRunId(self)-> str|None:
        if len(self.openai_run_id) > 0:
            return self.openai_run_id[-1]
        else:
            return None

    def setStatus(self, status)->None:
        if status in ["ready", "running", "complete", "error"]:
            self.status = status
        else:
            logging.warning("Invalid status: {}".format(status))
            raise ValueError("Invalid status")

    def isRunning(self)->bool:
        return self.status == "running"

    def isReady(self)->bool:

    def setLastContext(self, context)->None:
        self.last_context = json.dumps(context)

    def getLastContext(self)->dict|None:
        if self.last_context != "":
            return json.loads(self.last_context)
        else:
            return None

    def setLastPromotions(self, promotions)->None:
        self.last_promotions = json.dumps(promotions)

    def getLastPromotions(self)->dict|None:
        if self.last_promotions != "":
            return json.loads(self.last_promotions)
        else:
            return None

class ChatMessage:
    def __init__(self, user_type, message):
        if user_type in ["user", "assistant", "system"]:
            self.type = user_type
            self.message = message
        else:
            logging.warning("Invalid user type: {}".format(user_type))
            raise ValueError("Invalid user type")

    def get_as_dict(self):
        return {
            "user_type": self.type,
            "message": self.message
        }
    @staticmethod
    def from_dict(data) -> ChatMessage:
        return ChatMessage(
            data["user_type"],
            data["message"]
        )

class AssistantLog:
    def __init__(self, chat_type, message):
        self.type = chat_type
        self.message = message

    def get_as_dict(self):
        return {
            "type": self.type,
            "message": self.message
        }

    @staticmethod
    def from_dict(data) -> AssistantLog:
        return AssistantLog(
            data["type"],
            data["message"]
        )

USER_DB = UserDB(USER_DATA_PATH)
CHAT_DB = ChatDB(CHAT_DATA_PATH)

async def create_chat(user_id: int, thread_id: str) -> dict:
    new_chat = new Chat(0, user_id, thread_id)
    chat_db.add_chat(new_chat)
    return new_chat

async def update_chat(chat: Chat):
    chat_db.update_chat(chat)

async def delete_chat(id: int):
    chat_db.delete_chat(id=id)
