from fastapi import APIRouter

router = APIRouter()

@router.post("/api/chat")
async def create_chat():
    return {"id": 1}

@router.get("/api/chat/:id")
async def get_chat(id: int):
    example_chat = [
        {type: "user", message: "สวัสดีครับ"},
        {type: "system", message: "สวัสดีครับ มีอะไรให้ช่วยครับ"},
        {type: "user", message: "ฉันอยากทราบราคาสินค้า"},
        {type: "system", message: "ราคาสินค้าคือ 100 บาทครับ"},
        {type: "user", message: "ขอบคุณครับ"},
        {type: "system", message: "ยินดีครับ"},
    ]

    chat = example_chat
    return chat

@router.post("/api/chat/:id/message")
async def create_chat_message():
    return {"message": "Create chat message not supported"}


@router.get("/api/chat/:id/assistant")
async def get_chat_assistant(id: int):
    example_assistant = [
        {type: "system", message: "User logged in"},
        {type: "system", message: "AI started"},
    ]

    assistant = example_assistant
    return assistant