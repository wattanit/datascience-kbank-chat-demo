from fastapi import APIRouter
import json

router = APIRouter()

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

#############################

@router.get("/api/users")
async def get_users():
    users = load_users()
    return users

@router.get("/api/users/:id")
async def get_user(id: int):
    user = await find_user(id)
    return user

@router.post("/api/users")
async def create_user():
    return {"message": "Create user not supported"}