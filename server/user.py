from fastapi import APIRouter
import json
from server.db import load_users, find_user

router = APIRouter()

@router.get("/api/users")
def get_users():
    users = load_users()
    return {
        "users": users
    }

@router.get("/api/users/:id")
async def get_user(id: int):
    user = await find_user(id)
    return user

@router.post("/api/users")
async def create_user():
    return {"message": "Create user not supported"}