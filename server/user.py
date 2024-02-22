from fastapi import APIRouter

router = APIRouter()

@router.get("/api/users")
async def get_users():
    example_users = [
        {"id": 1, "name": "JohnDoe", "password": "password1", "description": "คนธรรมดา"},
        {"id": 2, "name": "สาริกา ลิ้นวัว", "password": "password2", "description": "คุณนายเจ้าของตลาด"},
        {"id": 3, "name": "ทาย หนูน้ำ", "password": "password3", "description": "วัยรุ่นสร้างตัว"},
    ]

    users = example_users
    return users

@router.post("/api/users")
async def create_user():
    return {"message": "Create user not supported"}