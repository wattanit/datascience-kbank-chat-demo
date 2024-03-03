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

@router.post("/api/chat/{id}/create_promotions_text")
async def create_promotions_text(id: int):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    thread_id = chat.openai_thread_id

    promotions = chat.get_last_promotions()
    promotion_text = json.dumps(promotions)

    logging.info("Adding promotions to OpenAI thread: chat_id={}, thread_id={}".format(chat.id, thread_id))
    data = {
        "role": "user",
        "content": promotion_text
    }

    response = requests.post(f'https://api.openai.com/v1/threads/{thread_id}/messages', data=json.dumps(data), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
    })

    if response.status_code != 200:
        logging.warning("OpenAI message creation failed: {}".format(response))
        raise HTTPException(status_code=500, detail="OpenAI message creation failed")

    chat.add_assistant_log("ask_for_promotion_text", "AI is asked to describe the promotion")
    CHAT_DB.update_chat(chat)

    # create a new run using Response Agent
    data = {
        "assistant_id": os.getenv("OPENAI_RESPONSE_AGENT_ID")
    }

    response = requests.post(f'https://api.openai.com/v1/threads/{thread_id}/runs', data=json.dumps(data), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
    })

    if response.status_code != 200:
        logging.warning("OpenAI run creation failed: {}".format(response))
        raise HTTPException(status_code=500, detail="OpenAI run creation failed")

    response = response.json()
    chat.add_run_id(response["id"])
    chat.set_status("running")
    chat.add_assistant_log("run_created", "Thinking of a nice response text. New run created: id={}".format(response["id"]))
    logging.info("Run created with id={}. Updated chat: {}".format(response["id"],chat.id))
    CHAT_DB.update_chat(chat)

    return {
        "status": "running",
        "action": "wait_for_promotion_text",
        "promotions": promotions
    }

@router.get("/api/chat/{id}/get_response")
async def get_chat_response(id: int):
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
            "assistant_logs": chat.assistant_logs
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
            "assistant_logs": chat.assistant_logs
        }

    # get running status
    response = requests.get(f'https://api.openai.com/v1/threads/{chat.openai_thread_id}/runs/{run_id}', headers={
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
    })
    
    if response.status_code != 200:
        logging.warning("OpenAI run status failed: {}".format(response))
        raise HTTPException(status_code=500, detail="OpenAI run status failed")
    
    response = response.json()
    if response["status"] != "completed":
        return {
            "status": "running",
            "action": "run_not_completed",
            "context": chat.last_context,
            "promotions": chat.last_promotions,
            "message": chat.chat_messages,
            "assistant_logs": chat.assistant_logs
        }

    chat.add_assistant_log("run_complete", "Run complete: id={}".format(run_id))
    chat.set_status("ready")
    CHAT_DB.update_chat(chat)

    # retrieve response messages
    response = requests.get(f'https://api.openai.com/v1/threads/{chat.openai_thread_id}/messages', headers={
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
    })

    if response.status_code != 200:
        logging.warning("OpenAI message retrieval failed: {}".format(response))
        raise HTTPException(status_code=500, detail="OpenAI message retrieval failed")

    response = response.json()
    response_message = response["data"][0]
    response_content = response_message["content"][0]

    if response_content["type"] != "text":
        chat.set_status("error")
        chat.add_assistant_log("invalid_response", "Invalid response: {}".format(response_content))
        CHAT_DB.update_chat(chat)
        logging.warning("Invalid response: {}".format(response_content))
        return {
            "status": "error",
            "action": "invalid_response",
            "context": chat.last_context,
            "promotions": chat.last_promotions,
            "message": chat.chat_messages,
            "assistant_logs": chat.assistant_logs
        }

    message = response_content["text"]["value"]
    chat.add_message("assistant", message)
    chat.add_assistant_log("response_message", "Response message added: {}".format(message))
    chat.set_status("ready")
    CHAT_DB.update_chat(chat)

    return {
        "status": "ready",
        "action": "response_added",
        "context": chat.last_context,
        "promotions": chat.last_promotions,
        "message": chat.chat_messages,
        "assistant_logs": chat.assistant_logs
    }
