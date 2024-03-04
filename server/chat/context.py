from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import logging
from server.db import CHAT_DB, USER_DB

logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter()


class NewChatMessagePayload(BaseModel):
    user_id: int
    message: str


@router.post("/api/chat/{id}/message")
async def create_chat_message(id: int, body: NewChatMessagePayload):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    # get user data
    user_id = body.user_id
    user = USER_DB.get_user_by_id(user_id)
    if user is None:
        logging.warning("User not found: id = {}".format(user_id))
        raise HTTPException(status_code=404, detail="User not found")
    customer_segment = user.segment
    credit_cards = user.credit_cards

    # save user message
    chat.add_message("user", body.message)
    chat.add_assistant_log(
        "user_message", "User message added: {}".format(body.message)
    )
    CHAT_DB.update_chat(chat)
    logging.info("Updated chat: {}".format(chat.id))

    # call OpenAI to add the message
    data = {
        "role": "user",
        "content": '{} [customer_segment: "{}", credit_cards: "{}"]'.format(
            body.message, customer_segment, credit_cards
        ),
    }
    logging.info("Calling OpenAI to add message: {}".format(data))
    response = requests.post(
        f"https://api.openai.com/v1/threads/{chat.openai_thread_id}/messages",
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

    # call OpenAI to create a new run
    if chat.is_ready():
        thread_id = chat.openai_thread_id
        data = {"assistant_id": os.getenv("OPENAI_CONTEXT_AGENT_ID")}
        logging.info("Calling OpenAI to create run: {}".format(data))
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
            "Interpreting of a relevant context. New run created: id={}".format(
                response["id"]
            ),
        )
        CHAT_DB.update_chat(chat)
        logging.info(
            "Run created with id={}. Updated chat: {}".format(response["id"], chat.id)
        )

    return chat


@router.get("/api/chat/{id}/get_context")
async def get_chat_context(id: int):
    chat = CHAT_DB.get_chat_by_id(id)
    if chat is None:
        logging.warning("Chat not found: id = {}".format(id))
        raise HTTPException(status_code=404, detail="Chat not found")

    if not chat.is_running():
        return {
            "status": "ready",
            "action": "no_run",
            "context": chat.chat_context,
            "message": "",
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
            "message": "",
        }

    logging.info(
        "Calling OpenAI to get run status: chat_id={} thread_id={}, run_id={}".format(
            chat.id, thread_id, run_id
        )
    )
    response = requests.get(
        f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
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
            "action": "run_in_progress",
            "context": chat.chat_context,
            "message": "",
        }

    # if run is completed

    chat.set_status("ready")
    chat.add_assistant_log("run_complete", "Run complete: id={}".format(run_id))

    # retrieve the run response from the last message of the thread
    logging.info(
        "Calling OpenAI to get messages: chat_id={} thread_id={}".format(
            chat.id, thread_id
        )
    )
    response = requests.get(
        f"https://api.openai.com/v1/threads/{thread_id}/messages",
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

    if response_message["role"] != "assistant":
        chat.set_status("ready")
        chat.add_assistant_log(
            "No response", "No AI response backed from context agent"
        )
        logging.warning(
            "No AI response backed from context agent: {}".format(response_message)
        )
        CHAT_DB.update_chat(chat)
        return {
            "status": "ready",
            "action": "no_response",
            "context": chat.chat_context,
            "message": "No response",
        }

    response_content = response_message["content"][0]

    if response_content["type"] != "text":
        chat.set_status("error")
        chat.add_assistant_log(
            "error", "Failed to parse OpenAI response: {}".format(response_content)
        )
        logging.warning("Failed to parse OpenAI response: {}".format(response_content))
        CHAT_DB.update_chat(chat)
        return {
            "status": "error",
            "action": "unexpected_response",
            "context": chat.chat_context,
            "message": "AI is confused",
        }

    response_text = response_content["text"]
    try:
        response_body = json.loads(response_text["value"])

        # if assistant asks for a follow up question
        if "follow_up_question" in response_body:
            # add follow up question to chat
            chat.add_message("assistant", response_body["follow_up_question"])
            chat.add_assistant_log(
                "follow_up_question", response_body["follow_up_question"]
            )
            logging.info(
                "Follow up question added: {}".format(
                    response_body["follow_up_question"]
                )
            )
            CHAT_DB.update_chat(chat)
            return {
                "status": "ready",
                "action": "follow_up_question",
                "context": chat.last_context,
                "message": response_body["follow_up_question"],
            }
        # if assistant found a context
        elif "context" in response_body:
            chat.add_assistant_log("context_found", response_body["context"])
            chat.chat_context = response_body["context"]
            CHAT_DB.update_chat(chat)
            return {
                "status": "ready",
                "action": "context_found",
                "context": chat.chat_context,
                "message": response_body,
            }
        else:
            chat.set_status("error")
            chat.add_assistant_log("error", "AI is confused: {}".format(response_text))
            logging.warning(
                "Unexpected chat context response format: {}".format(response_text)
            )
            CHAT_DB.update_chat(chat)
            return {
                "status": "error",
                "action": "unexpected_response",
                "context": chat.chat_context,
                "message": "AI is confused",
            }

    except:
        chat.set_status("error")
        chat.add_assistant_log(
            "error", "Failed to parse OpenAI response: {}".format(response_text)
        )
        logging.warning("Failed to parse OpenAI response: {}".format(response_text))
        CHAT_DB.update_chat(chat)
        return {
            "status": "error",
            "action": "unexpected_response",
            "context": chat.chat_context,
            "message": "AI is confused",
        }
