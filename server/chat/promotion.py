from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import logging
from server.db import CHAT_DB

logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter()

@router.get("/api/chat/{id}/get_promotions")
async def get_chat_promotions(id: int):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    last_user_message = chat.get_last_user_message()
    if last_user_message is None:
        return {
            "status": "ready",
            "action": "promotions not found",
            "promotions": "",
        }

    last_context = chat.get_last_context()
    first_thing = last_context["top_5_things"][0]

    q1 = last_user_message.message
    q2 = first_thing

    logging.info("Querying promotions: q1={}, q2={}".format(q1, q2))
    chat.add_assistant_log("promotions_query", "Querying promotions: q1={}, q2={}".format(q1, q2))
    
    # query for promotions
    response = requests.get("http://localhost:8001/api/search", params={"q1": q1, "q2": q2})

    if response.status_code != 200:
        logging.warning("Promotion search engine failed: {}".format(response))
        raise HTTPException(status_code=500, detail="Promotion search engine failed")

    response = response.json()
    
    if len(response["result"]) == 0:
        return {
            "status": "ready",
            "action": "promotions not found",
            "promotions": ""
        }
        
    logging.info("Promotions found: {}".format(response["result"]))
    chat.add_assistant_log("promotions_found", json.dumps(response["result"]))
    chat.set_last_promotions(response["result"])
    CHAT_DB.update_chat(chat)
    return {
        "status": "ready",
        "action": "promotions found",
        "promotions": response["result"]
    }

