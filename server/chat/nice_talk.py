import os
import time
import json
import logging
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from server.db import CHAT_DB

logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter()


def further_assistant(chat) -> str | None:
    last_user_message = chat.get_last_user_message()

    if "s24 ultra" in last_user_message.lower():
        chat.add_assistant_log(
            "further assist",
            "Checking for special recommendations",
            response_time=time.time() - time.time(),
        )
        CHAT_DB.update_chat(chat)

        return """
Special instruction: If and only if the conversation is about Samsung S24 Ultra mobile phone,  in addition the promotion recommendation, please also suggest where to buy it from the following links:
Powerbuy : https://www.powerbuy.co.th/th/product/samsung-galaxy-s24-ultra-ram-12gb-256gb-titanium-gray-295650
Banana IT: https://www.bnn.in.th/th/p/smartphone-and-accessories/smartphone/samsung-smartphone/samsung-smartphone-galaxy-s24-ultra-12512-titanium-5g-8806095373393_zvje4w
"""
    else:
        return None

    chat.add_message("assistant", response)
    chat.set_status("ready")
    CHAT_DB.update_chat(chat)
    return {
        "status": "ready",
        "action": "response_added",
        "context": chat.last_context,
        "promotions": chat.last_promotions,
        "message": chat.chat_messages,
        "assistant_logs": chat.assistant_logs,
    }

@router.post("/api/chat/{id}/create_promotions_text")
async def create_promotions_text(id: int):
    start_time = time.time()
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    thread_id = chat.openai_thread_id

    last_user_message = chat.get_last_user_message()

    promotions = chat.get_last_promotions()
    promotion_text = ""
    for item in promotions:
        if (
            last_user_message in item["summary_text"]
            or last_user_message in item["promotion_title"]
        ):
            promotion_text = json.dumps(item)

    if promotion_text == "":
        promotion_text = json.dumps(promotions)
    # promotion_text = json.dumps(promotions[0])
    logging.info(
        "Adding promotions to OpenAI thread: chat_id={}, thread_id={}".format(
            chat.id, thread_id
        )
    )
    data = {"role": "user", "content": last_user_message + "\n" + promotion_text}

    response = requests.post(
        f"https://api.openai.com/v1/threads/{thread_id}/messages",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
            "OpenAI-Beta": "assistants=v1",
        },
    )

    if response.status_code != 200:
        logging.warning(
            "OpenAI message creation failed: code{}, {}".format(
                response.status_code, response.json()
            )
        )
        raise HTTPException(status_code=500, detail="OpenAI message creation failed")

    chat.add_assistant_log(
        "ask_for_promotion_text",
        "AI is asked to describe the promotion",
        response_time=time.time() - start_time,
    )
    CHAT_DB.update_chat(chat)

    # create a new run using Response Agent
    start_time = time.time()
    data = {
        "assistant_id": os.getenv("OPENAI_RESPONSE_AGENT_ID"),
        "additional_instructions": further_assistant(chat),
    }

    response = requests.post(
        f"https://api.openai.com/v1/threads/{thread_id}/runs",
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
            "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
            "OpenAI-Beta": "assistants=v1",
        },
    )

    if response.status_code != 200:
        logging.warning(
            "OpenAI run creation failed: code{}, {}".format(
                response.status_code, response.json()
            )
        )
        raise HTTPException(status_code=500, detail="OpenAI run creation failed")

    response = response.json()
    chat.add_run_id(response["id"])
    chat.set_status("running")
    chat.add_assistant_log(
        "run_created",
        "Thinking of a nice response text. New run created: id={}".format(
            response["id"]
        ),
        response_time=time.time() - start_time,
    )
    logging.info(
        "Run created with id={}. Updated chat: {}".format(response["id"], chat.id)
    )
    CHAT_DB.update_chat(chat)

    return {
        "status": "running",
        "action": "wait_for_promotion_text",
        "promotions": promotions,
    }


@router.get("/api/chat/{id}/get_response")
async def get_chat_response(id: int):
    start_time = time.time()
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    if not chat.is_running:
        return {
            "status": "ready",
            "action": "no_run",
            "context": chat.last_context,
            "promotions": chat.last_promotions,
            "message": chat.chat_messages,
            "assistant_logs": chat.assistant_logs,
        }

    run_id = chat.get_last_run_id()
    if run_id is None:
        logging.warning("Run ID not found. Set chat status to ready")
        chat.set_status("ready")
        CHAT_DB.update_chat(chat)
        logging.info("Updated chat: {}".format(chat.id))
        return {
            "status": "ready",
            "action": "no_run",
            "context": chat.last_context,
            "promotions": chat.last_promotions,
            "message": chat.chat_messages,
            "assistant_logs": chat.assistant_logs,
        }

    # get running status
    response = requests.get(
        f"https://api.openai.com/v1/threads/{chat.openai_thread_id}/runs/{run_id}",
        headers={
            "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
            "OpenAI-Beta": "assistants=v1",
        },
    )

    if response.status_code != 200:
        logging.warning(
            "OpenAI run status failed: code{}, {}".format(
                response.status_code, response.json()
            )
        )
        raise HTTPException(status_code=500, detail="OpenAI run status failed")

    response = response.json()
    if response["status"] != "completed":
        return {
            "status": "running",
            "action": "run_not_completed",
            "context": chat.last_context,
            "promotions": chat.last_promotions,
            "message": chat.chat_messages,
            "assistant_logs": chat.assistant_logs,
        }

    chat.add_assistant_log(
        "run_complete",
        "Run complete: id={}".format(run_id),
        response_time=time.time() - start_time,
    )
    chat.set_status("ready")
    CHAT_DB.update_chat(chat)

    # retrieve response messages
    start_time = time.time()
    response = requests.get(
        f"https://api.openai.com/v1/threads/{chat.openai_thread_id}/messages",
        headers={
            "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
            "OpenAI-Beta": "assistants=v1",
        },
    )

    if response.status_code != 200:
        logging.warning(
            "OpenAI message retrieval failed: code{}, {}".format(
                response.status_code, response.json()
            )
        )
        raise HTTPException(status_code=500, detail="OpenAI message retrieval failed")

    response = response.json()
    response_message = response["data"][0]
    response_content = response_message["content"][0]

    if response_content["type"] != "text":
        chat.set_status("error")
        chat.add_assistant_log(
            "invalid_response",
            "Invalid response: {}".format(response_content),
            response_time=time.time() - start_time,
        )
        CHAT_DB.update_chat(chat)
        logging.warning("Invalid response: {}".format(response_content))
        return {
            "status": "error",
            "action": "invalid_response",
            "context": chat.last_context,
            "promotions": chat.last_promotions,
            "message": chat.chat_messages,
            "assistant_logs": chat.assistant_logs,
        }
        

    try:
        promotion_choice = str(json.loads(response_content["text"]["value"])["result"])
        logging.info("Promotion choice: {}".format(promotion_choice))
        if promotion_choice:
            message_string = "Default cerdit card promotion"
            for _promotion in json.loads(chat.last_promotions):
                if promotion_choice == str(_promotion["id"]):
                    message_string = _promotion["summary_text"]
                    break
        else:
            message_string = "Default cerdit card promotion"
    except:
        logging.warning("Cannot parse response: {}".format(response_content))
        message_string = "Default cerdit card promotion"

    chat.add_message("assistant", message_string)

    chat.add_assistant_log(
        "response_message",
        "Response message added: {}".format(message_string),
        response_time=time.time() - start_time,
    )
    chat.set_status("ready")
    CHAT_DB.update_chat(chat)

    return {
        "status": "ready",
        "action": "response_added",
        "context": chat.last_context,
        "promotions": chat.last_promotions,
        "message": chat.chat_messages,
        "assistant_logs": chat.assistant_logs,
    }
