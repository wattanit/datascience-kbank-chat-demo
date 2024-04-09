import os
import logging
import uvicorn
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv

from server2.user import router as user_router
from server2.chat import router as chat_router
from server2.chat.api import router as chat_api_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(chat_api_router)

@app.get("/")
async def root():
    return {"message": "K-Bank Credit Chat DEMO API v0.3"}

def start():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)