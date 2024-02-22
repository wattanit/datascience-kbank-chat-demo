from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from server.db import load_chats, save_chats, find_chat, create_chat, update_chat, find_user
from server.db import delete_chat as delete_chat_from_db
from server.agent import process_chat

load_dotenv()
print("LOADED API KEYS: {}".format(os.getenv("OPENAI_API_KEY")))
print("UNDERSTANDING AGENT ID: {}".format(os.getenv("OPENAI_UNDERSTANDING_AGENT_ID")))
print("RESPONSE AGENT ID: {}".format(os.getenv("OPENAI_RESPONSE_AGENT_ID")))

router = APIRouter()

class NewChatPayload(BaseModel):
    user_id: int

@router.post("/api/chat")
async def post_chat(body: NewChatPayload):
    print("Creating new chat for user: {}".format(body.user_id))

    # call OpenAI to create a new thread
    response = requests.post('https://api.openai.com/v1/threads', data={}, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Beta': 'assistants=v1'
        })

    if response.status_code != 200:
        print(response.status_code)
        raise HTTPException(status_code=500, detail="OpenAI thread creation failed")

    response = response.json()
    thread_id = response["id"]
    print("Created OpenAI thread: {}".format(thread_id))

    new_chat = await create_chat(body.user_id, thread_id)
    print("Created new chat: {}".format(new_chat))
    return new_chat

@router.get("/api/chat/:id")
async def get_chat(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat

@router.delete("/api/chat/:id")
async def delete_chat(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # call OpenAI delete thread
        thread_id = chat["openai_thread_id"]
        response = requests.delete(f'https://api.openai.com/v1/threads/{thread_id}', headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'OpenAI-Beta': 'assistants=v1'
            })

        if response.status_code != 200:
            print(response.status_code)
            return {}
        
        response = response.json()
        if response["deleted"]:
            print("Deleted OpenAI thread: {}".format(thread_id))

        # delete chat from database
        await delete_chat_from_db(id)
        print("Deleted chat: {}".format(id))

        return chat

class NewChatMessagePayload(BaseModel):
    user_id: int
    message: str

@router.post("/api/chat/:id/message")
async def create_chat_message(id: int, body: NewChatMessagePayload, background_tasks: BackgroundTasks):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # get user data
        user_id = body.user_id
        user = await find_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # save user message
        new_chat_message = {
            "type": "user",
            "message": body.message
        }
        chat["chat_messages"].append(new_chat_message)

        # call OpenAI to add the message
        data = {
            "role": "user",
            "content": body.message
        }
        response = requests.post(f'https://api.openai.com/v1/threads/{chat["openai_thread_id"]}/messages', data=json.dumps(data), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'OpenAI-Beta': 'assistants=v1'
            })

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="OpenAI message creation failed")

        # call OpenAI to create a new run
        if chat["status"] == "done":
            thread_id = chat["openai_thread_id"]
            C = {
                "assistant_id": os.getenv("OPENAI_UNDERSTANDING_AGENT_ID")
            }
            response = requests.post(f'https://api.openai.com/v1/threads/{thread_id}/runs', data=json.dumps(data), headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                'OpenAI-Beta': 'assistants=v1'
                })

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="OpenAI run creation failed")

            response = response.json()

            chat["openai_run_id"].append(response["id"])
            chat["status"] = "running"
            await update_chat(chat)

        return new_chat_message

@router.get("/api/chat/:id/get_context")
async def get_chat_context(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        if chat["status"] == "done":
            return {
                "action": "no action",
                "context": chat["last_context"],
                "message": ""
            }
        elif chat["status"] == "running":
            if len(chat["openai_run_id"]) > 0:
                thread_id = chat["openai_thread_id"]
                run_id = chat["openai_run_id"][-1]

                response = requests.get(f'https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}', headers={
                    'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                    'OpenAI-Beta': 'assistants=v1'
                    })

                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="OpenAI run status failed")

                response = response.json()
                if response["status"] == "complete":
                    # update chat status to done
                    chat["status"] = "done"
                    
                    # retrieve the run response from the last message of the thread
                    response = requests.get(f'https://api.openai.com/v1/threads/{thread_id}/messages', headers={
                        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                        'OpenAI-Beta': 'assistants=v1'
                        })

                    if response.status_code != 200:
                        raise HTTPException(status_code=500, detail="OpenAI message retrieval failed")

                    response = response.json()
                    response_message = response["data"][0]

                    if response_message["role"] == "assistant":
                        response_content = response_message["content"]
                        if response_content["type"] == "text":
                            response_text = response_content["text"]

                            try:
                                response_body = json.loads(response_text)

                                # if assistant asks for a follow up question
                                if "follow_up_question" in response_body:
                                    # add follow up question to chat
                                    new_chat_message = {
                                        "type": "bot",
                                        "message": response_body["follow_up_question"]
                                    }
                                    chat["chat_messages"].append(new_chat_message)

                                    new_assistant_log = {
                                        "type": "follow_up_question",
                                        "message": response_body["follow_up_question"]
                                    }
                                    chat["assistant_logs"].append(new_assistant_log)

                                    await update_chat(chat)
                                    return {
                                        "action": "follow_up_question",
                                        "context": response["context"],
                                        "message": response_body["follow_up_question"]
                                    }

                                # if assistant found a context
                                elif "meaning" in response_body:
                                    new_assistant_log = {
                                        "type": "context_meaning_found",
                                        "message": response_body["meaning"]
                                    }
                                    chat["assistant_logs"].append(new_assistant_log)

                                    if "top_5_things" in response_body:
                                        new_assistant_log = {
                                            "type": "context_activity_found",
                                            "message": json.dumps(response_body["top_5_things"])
                                        }
                                        chat["assistant_logs"].append(new_assistant_log)

                                    chat["last_context"] = json.dumps(response_body)
                                    await update_chat(chat)
                                    return {
                                        "action": "context_found",
                                        "context": json.dumps(response_body),
                                        "message": ""
                                    }

                            except:
                                # report to assistant logs
                                new_assistant_log = {
                                    "type": "error",
                                    "message": "Failed to parse OpenAI response: {}".format(response_text)
                                }
                                chat["assistant_logs"].append(new_assistant_log)
                                await update_chat(chat)
                                return {
                                    "action": "error",
                                    "context": chat["last_context"],
                                    "message": "AI is confused"
                                }
                        else:
                            await update_chat(chat)
                            return {
                                "action": "done",
                                "context": chat["last_context"],
                                "message": ""
                            }
                    else:
                        await update_chat(chat)
                        return {
                            "action": "done",
                            "context": chat["last_context"],
                            "message": ""
                        }
                            
                else:
                    return {
                        "action": "running",
                        "context": chat["last_context"],
                        "message": ""
                    }

        else:
            return {
                "status": "done",
                "context": chat["last_context"],
                "message": ""
            }

@router.get("/api/chat/:id/get_promotions")
async def get_chat_promotions(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # get last user message
        last_user_message = next((message for message in chat["chat_messages"] if message["type"] == "user"), None)
        if last_user_message is None:
            return {
                "action": "promotions not found",
                "promotions": "",
            }
        
        # get last context from chat
        last_context = chat["last_context"]
        if last_context != "":
            try:
                last_context = json.loads(last_context)
                first_thing = last_context["top_5_things"][0]
            except:
                first_thing = None
        else:
            first_thing = None

        q1 = last_user_message
        q2 = first_thing

        # query for promotions
        response = {
            "result": []
        }
        
        if len(response["result"]) == 0:
            return {
                "action": "promotions not found",
                "promotions": ""
            }
        else:
            # add promotions to OpenAI thread
            thread_id = chat["openai_thread_id"]

            promotion_text = json.dumps(response["result"])
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
                raise HTTPException(status_code=500, detail="OpenAI message creation failed")

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
                raise HTTPException(status_code=500, detail="OpenAI run creation failed")

            response = response.json()
            chat["openai_run_id"].append(response["id"])
            chat["status"] = "running"
            await update_chat(chat)

            return {
                "action": "promotions found",
                "promotions": response["result"]
            }
            

@router.get("/api/chat/:id/message")
async def get_chat_messages(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["chat_messages"]


@router.get("/api/chat/:id/assistant")
async def get_chat_assistant(id: int):
    chat = await find_chat(id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    else:
        return chat["assistant_logs"]

