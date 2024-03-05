import os
import time
import json
import logging
import requests
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
from server.db import CHAT_DB, USER_DB, Chat

logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter()

def get_context_agent_id(chat: Chat)->str|None:
    if chat.chat_context == 1 or chat.chat_context == "1":
        return os.getenv("OPENAI_SPECIALIST_PRODUCT_AGENT_ID")
    elif chat.chat_context == 2 or chat.chat_context == "2":
        return os.getenv("OPENAI_SPECIALIST_OCCASION_AGENT_ID")
    elif chat.chat_context == 3 or chat.chat_context == "3":
        return os.getenv("OPENAI_SPECIALIST_PLACE_AGENT_ID")
    else:
        return None

@router.post("/api/chat/{id}/create_context_details")
def create_context_details(id: int):
    start_time = time.time()
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    user_id = chat.user_id
    user = USER_DB.get_user_by_id(user_id)
    if user is None:
        logging.warning("User not found: id = {}".format(user_id))
        raise HTTPException(status_code=404, detail="User not found")
    customer_segment = user.segment

    # call OpenAI to create context details
    if chat.is_ready():
        thread_id = chat.openai_thread_id

        context_agent_id = get_context_agent_id(chat)

        if context_agent_id is None:
            logging.warning("Context agent not found for chat: id = {}".format(id))
            raise HTTPException(status_code=404, detail="Context agent not found")

        data = {
            "assistant_id": context_agent_id
        }
        logging.info("Calling OpenAI to create run: context={} agent_id={}".format(chat.chat_context, context_agent_id))   
        response = requests.post(f'https://api.openai.com/v1/threads/{thread_id}/runs', data=json.dumps(data), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'OpenAI-Beta': 'assistants=v1'
        })

        if response.status_code != 200:
            logging.warning("OpenAI run creation failed: code{}, {}".format(response.status_code, response.json()))
            raise HTTPException(status_code=500, detail="OpenAI run creation failed")

        response = response.json()
        chat.add_run_id(response["id"])
        chat.set_status("running")
        chat.add_assistant_log(
            "run_created", 
            "Thinking of context details. Run created: {}".format(response["id"]),
            response_time = time.time() - start_time
            )
        CHAT_DB.update_chat(chat)
        logging.info("Run created with id={}. Updated chat: {}".format(response["id"],chat.id))

    return chat

@router.get("/api/chat/{id}/get_context_details")
async def get_context_details(id: int):
    start_time = time.time()
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if not chat.is_running():
        return {
            "status": "ready",
            "action": "no_run",
            "context": chat.chat_context,
            "context_detais": chat.last_context,
            "message": ""
        }

    thread_id = chat.openai_thread_id
    run_id = chat.get_last_run_id()
    if run_id is None:
        logging.warning("Run ID not found. Set chat status to ready")
        chat.set_status("ready")
        CHAT_DB.update_chat(chat)
        logging.info("Updated chat: {}".format(chat.id))
        return {
            "status": "ready",
            "action": "no_run",
            "context": chat.chat_context,
            "context_detais": chat.last_context,
            "message": ""
        }

    logging.info("Calling OpenAI to get run status: chat_id={} thread_id={}, run_id={}".format(chat.id, thread_id, run_id))
    response = requests.get(f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}', headers={
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
        })

    if response.status_code != 200:
        logging.warning("OpenAI run status failed: code{}, {}".format(response.status_code, response.json()))
        raise HTTPException(status_code=500, detail="OpenAI run status failed")

    response = response.json()
    if response["status"] != "completed":
        return {
            "status": "running",
            "action": "run_in_progress",
            "context": chat.chat_context,
            "context_detais": chat.last_context,
            "message": ""
        }

    # if run is completed

    chat.set_status("ready")
    chat.add_assistant_log(
        "run_complete", 
        "Run complete: id={}".format(run_id),
        response_time = time.time() - start_time
        )

    # retrieve the run response from the last message of the thread
    start_time = time.time()
    logging.info("Calling OpenAI to get messages: chat_id={} thread_id={}".format(chat.id, thread_id))  
    response = requests.get(f'https://api.openai.com/v1/threads/{thread_id}/messages', headers={
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
    }) 

    if response.status_code != 200:
        logging.warning("OpenAI message retrieval failed: code{}, {}".format(response.status_code, response.json()))
        raise HTTPException(status_code=500, detail="OpenAI message retrieval failed")

    response = response.json()
    response_message = response["data"][0]

    if response_message["role"] != "assistant":
        chat.set_status("ready")
        chat.add_assistant_log(
            "No response", 
            "No AI response backed from context agent",
            response_time = time.time() - start_time
            )
        logging.warning("No AI response backed from context agent: {}".format(response_message))
        CHAT_DB.update_chat(chat)
        return {
            "status": "ready",
            "action": "no_response",
            "context": chat.chat_context,
            "context_detais": chat.last_context,
            "message": "No response"
        }

    response_content = response_message["content"][0]
    if response_content["type"] != "text":
        chat.set_status("error")
        chat.add_assistant_log(
            "error", 
            "Failed to parse OpenAI response: {}".format(response_content),
            response_time = time.time() - start_time
            )
        logging.warning("Failed to parse OpenAI response: {}".format(response_content))
        CHAT_DB.update_chat(chat)
        return {
            "status": "error",
            "action": "unexpected_response",
            "context": chat.chat_context,
            "context_detais": chat.last_context,
            "message": "AI is confused"
        }

    response_text = response_content["text"]
    try:
        response_body = json.loads(response_text["value"])

        if "follow_up_question" in response_body:
            # add follow up question to chat
            chat.add_message("assistant", response_body["follow_up_question"])
            chat.add_assistant_log(
                "follow_up_question", 
                response_body["follow_up_question"],
                response_time = time.time() - start_time
                )
            logging.info("Follow up question added: {}".format(response_body["follow_up_question"]))
            CHAT_DB.update_chat(chat)
            return {
                "status": "ready",
                "action": "follow_up_question",
                "context": chat.last_context,
                "context_detais": chat.last_context,
                "message": response_body["follow_up_question"]
            }
        # if assistant found context details with "meaning"
        elif "meaning" in response_body:
            chat.add_assistant_log(
                "context_meaning_found", 
                response_body["meaning"],
                response_time = time.time() - start_time
                )
            if "top_5_things" in response_body:
                chat.add_assistant_log(
                    "context_activity_found", 
                    json.dumps(response_body["top_5_things"]),
                    response_time = time.time() - start_time
                    )

            logging.info("Context found: chat_id={} context: {}".format(chat.id, response_body))
            chat.set_last_context(response_body)
            CHAT_DB.update_chat(chat)
            return {
                "status": "ready",
                "action": "context_details_found",
                "context": chat.chat_context,
                "context_detais": chat.last_context,
                "message": response_body
            }
        # if assistant found context details with "product_type"
        elif "product_type" in response_body:
            chat.add_assistant_log(
                "context_product_type_found", 
                response_body["product_type"],
                response_time = time.time() - start_time
                )

            logging.info("Context found: chat_id={} context: {}".format(chat.id, response_body))
            chat.set_last_context(response_body)
            CHAT_DB.update_chat(chat)
            return {
                "status": "ready",
                "action": "context_details_found",
                "context": chat.chat_context,
                "context_detais": chat.last_context,
                "message": response_body
            }
        else:
            chat.set_status("error")
            chat.add_assistant_log(
                "error", 
                "AI is confused: {}".format(response_text),
                response_time = time.time() - start_time
                )
            logging.warning("Unexpected chat context response format: {}".format(response_text))
            CHAT_DB.update_chat(chat)
            return {
                "status": "error",
                "action": "unexpected_response",
                "context": chat.chat_context,
                "context_detais": chat.last_context,
                "message": "AI is confused"
            }
            
    except:
        chat.set_status("error")
        chat.add_assistant_log(
            "error", 
            "Failed to parse OpenAI response: {}".format(response_text),
            response_time = time.time() - start_time
            )
        logging.warning("Failed to parse OpenAI response: {}".format(response_text))
        CHAT_DB.update_chat(chat)
        return {
            "status": "error",
            "action": "unexpected_response",
            "context": chat.chat_context,
            "context_detais": chat.last_context,
            "message": "AI is confused"
        }
