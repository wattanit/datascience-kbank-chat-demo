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
    q1 = last_user_message

    def get_contexts(chat):
        if chat.chat_context == 1 or chat.chat_context == "1":
            return last_context["product_type"]
        elif chat.chat_context == 2 or chat.chat_context == "2":
            return last_context["top_5_things"]
        elif chat.chat_context == 3 or chat.chat_context == "3":
            return last_context["top_5_things"]
        else:
            return []

    q2 = get_contexts(chat)

    q = [q1] + q2

    logging.info("Querying promotions: q={}".format(q))
    chat.add_assistant_log("promotions_query", "Querying promotions: q={}".format(q))

    # query for promotions
    response = requests.get("http://localhost:8001/api/search", params={"q": q})

    if response.status_code != 200:
        logging.warning(
            "Promotion search engine failed: code{}, {}".format(
                response.status_code, response.json()
            )
        )
        raise HTTPException(status_code=500, detail="Promotion search engine failed")

    response = response.json()

    if len(response["result"]) == 0:
        return {"status": "ready", "action": "promotions not found", "promotions": ""}

    logging.info("Promotions found: {}".format(response["result"]))
    chat.add_assistant_log("promotions_found", json.dumps(response["result"]))
    chat.set_last_promotions(response["result"])
    CHAT_DB.update_chat(chat)
    return {
        "status": "ready",
        "action": "promotions found",
        "promotions": response["result"],
    }
