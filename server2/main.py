import os
import logging
import uvicorn
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv

from server.user import router as user_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "K-Bank Credit Chat DEMO API v0.3"}

def start():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)