from fastapi import APIRouter
import json
from server.db import load_users, find_user
from server.db import UserDB, User

router = APIRouter()

USER_DATA_PATH = 'data/users.json'
user_db = UserDB(USER_DATA_PATH)

@router.get("/api/users")
def get_users():
    users = user_db.get_all_users_as_dict()
    return {
        "users": users
    }

@router.get("/api/users/:id")
async def get_user(id: int):
    user = user_db.get_user_by_id(id)
    return user

@router.post("/api/users")
async def create_user():
    return {"message": "Create user not supported"}