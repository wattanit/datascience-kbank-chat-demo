import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from server.user import router as user_router
from server.chat.basic import router as chat_router
from server.chat.context import router as context_router
from server.chat.promotion import router as promotion_router
from server.chat.nice_talk import router as nice_talk_router

logging.basicConfig(level=logging.INFO)

load_dotenv()
logging.info("LOADED API KEYS: {}".format(os.getenv("OPENAI_API_KEY")))
logging.info("UNDERSTANDING AGENT ID: {}".format(os.getenv("OPENAI_UNDERSTANDING_AGENT_ID")))
logging.info("RESPONSE AGENT ID: {}".format(os.getenv("OPENAI_RESPONSE_AGENT_ID")))

app = FastAPI()
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(context_router)
app.include_router(promotion_router)
app.include_router(nice_talk_router)

@app.get("/")
async def root():
    return {"message": "K-Bank Credit Chat DEMO API"}

def start():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)