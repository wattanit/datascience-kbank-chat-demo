from fastapi import APIRouter
import json
from server2.db import USER_DB

router = APIRouter()


@router.get("/api/users")
def get_users():
    users = USER_DB.get_all_users_as_dict()
    return {"users": users}


@router.get("/api/users/{id}")
async def get_user(id: int):
    user = USER_DB.get_user_by_id(id)
    return user


@router.post("/api/users")
async def create_user():
    return {"message": "Create user not supported"}
