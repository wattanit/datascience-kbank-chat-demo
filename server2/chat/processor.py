import time
import logging
import json
import asyncio
import requests
import os
from fastapi import WebSocket
from openai import AssistantEventHandler, OpenAI
from dotenv import load_dotenv
from typing_extensions import override
from server2.chat.utils import send_activity, send_chat, send_error, get_elapsed_time, send_chat_delta, TimeLog
from server2.db import CHAT_DB, Chat, USER_DB, CREDIT_CARD_DB

logging.basicConfig(level=logging.INFO)

load_dotenv()

client = OpenAI()

async def add_assistant_log(chat, title, body, response_time, websocket: WebSocket):
    chat.add_assistant_log(title, body, response_time)
    CHAT_DB.update_chat(chat)
    logging.info("Updated chat: {}".format(chat.id))
    await send_activity(websocket, title, body, response_time)

def get_context_agent_id(chat: Chat)->str|None:
    if chat.chat_context == 1 or chat.chat_context == "1":
        return os.getenv("OPENAI_SPECIALIST_PRODUCT_AGENT_ID")
    elif chat.chat_context == 2 or chat.chat_context == "2":
        return os.getenv("OPENAI_SPECIALIST_OCCASION_AGENT_ID")
    elif chat.chat_context == 3 or chat.chat_context == "3":
        return os.getenv("OPENAI_SPECIALIST_PLACE_AGENT_ID")
    else:
        return None

async def add_user_message(chat, message, websocket: WebSocket):
    start_time = time.time()
    
    # save user message
    chat.add_message("user", message)
    await add_assistant_log(chat, 
        "user_message", 
        f"User message added: {message}", 
        get_elapsed_time(start_time),
        websocket)

async def wait_run_to_complete(chat):
    run_id = chat.get_last_run_id()
    thread_id = chat.openai_thread_id
    if run_id is None:
        logging.warning("Run ID not found")
        return

    # call OpenAI API to get run status
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )

    # wait until run is completed
    while run.status != "completed":
        logging.info(f"Waiting for run to complete: {run_id}")
        await asyncio.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

    return run

async def get_context(chat, user, websocket: WebSocket):
    # Add message to a thread
    start_time = time.time()

    thread_id = chat.openai_thread_id
    message = chat.get_last_user_message()
    customer_segment = user.segment
    credit_cards = user.credit_cards

    data_content = f'{message} [customer_segment: "{customer_segment}", credit_cards: "{credit_cards}"'

    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=data_content,
    )
    logging.info(f"Calling OpenAI to add message: {data_content}")
    await add_assistant_log(chat, 
        "Add message", 
        f"Giving your message to AI to think. Message: {data_content}", 
        get_elapsed_time(start_time), 
        websocket
    )

    # call OpenAI to create a new run to get context
    start_time = time.time()

    assistant_id = os.getenv("OPENAI_CONTEXT_AGENT_ID")
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # save run information
    run_id = run.id
    chat.add_run_id(run_id)
    chat.set_status("running")
    log_title = "run_created"
    log_body = f"Interpreting of a relevant context. New run created: id={run_id}"
    elapsed_time = get_elapsed_time(start_time)
    await add_assistant_log(chat, log_title, log_body, elapsed_time, websocket)

    # wait for run to complete
    run = await wait_run_to_complete(chat)
    chat.set_status("ready")
    log_title = "run_completed"
    log_body = f"Interpreting of a relevant context. Run completed: id={run_id}"
    elapsed_time = get_elapsed_time(start_time)
    await add_assistant_log(chat, log_title, log_body, elapsed_time, websocket)

    # retrieve the run response from the last message of the thread
    start_time = time.time()

    logging.info(f"Calling OpenAI to get messages: chat_id={chat.id} thread_id={thread_id}")
    thread_messages = client.beta.threads.messages.list(thread_id)
    response_message = thread_messages.data[0]
    if response_message.role != "assistant":
        logging.warning(f"No AI response backed from context agent: {response_message}")
        await add_assistant_log(chat, "No response", "No AI response backed from context agent", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "No response", chat.chat_context)
        return

    response_content = response_message.content[0]
    if response_content.type != "text":
        logging.warning(f"Failed to parse OpenAI response: {response_content}")
        chat.set_status("error")
        await add_assistant_log(chat, "Failed to parse response", "Failed to parse OpenAI response", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "AI is confused", chat.chat_context)
        return

    response_text = response_content.text
    try:
        response_body = json.loads(response_text.value)

        # if assistant asks for a follow up question
        if "follow_up_question" in response_body:
            # add follow up question to chat
            follow_up_question = response_body["follow_up_question"]
            chat.add_message("assistant", follow_up_question)
            await add_assistant_log(chat, "follow_up_question", follow_up_question, get_elapsed_time(start_time), websocket)
            logging.info(f"Follow up question added: {follow_up_question}")
            await send_chat(websocket, "assistant", follow_up_question, chat.chat_context)
            return
        # if assistant found a context
        elif "context" in response_body:
            context = response_body["context"]
            chat.chat_context = context
            await add_assistant_log(chat, "context_found", context, get_elapsed_time(start_time), websocket)
            logging.info(f"Context found: {context}")
            await send_chat(websocket, "system", "AI ของเราเข้าใจคำถามของคุณแล้ว กรุณารอสักครู่", chat.chat_context)
            return
        else:
            chat.set_status("error")
            logging.warning(f"Unexpected chat context response format: {response_text}")
            await add_assistant_log(chat, "error", f"AI is confused: {response_text}", get_elapsed_time(start_time), websocket)
            await send_chat(websocket, "system", "AI is confused", chat.chat_context)
            return
    except json.JSONDecodeError as e:
        chat.set_status("error")
        logging.warning(f"Failed to parse OpenAI response: {response_text}")
        await add_assistant_log(chat, "Failed to parse response", "Failed to parse OpenAI response", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "AI is confused", chat.chat_context)
        return

async def get_context_details(chat, user, websocket: WebSocket):
    # create context details
    start_time = time.time()

    thread_id = chat.openai_thread_id
    context_agent_id = get_context_agent_id(chat)

    if context_agent_id is None:
        logging.warning("Context agent not found for chat: id = {}".format(chat.id))
        await send_error(websocket, "404", "Context agent not found")
        return

    # call OpenAI to create a new run to get context details
    # create a run and start to stream the run's response
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=context_agent_id,
    ) as stream:
        chat.set_status("running")
        await add_assistant_log(chat,
            "context_details_query",
            "Querying context details",
            get_elapsed_time(start_time),
            websocket
        )
        logging.info(f"Calling OpenAI to get context details: chat_id={chat.id} thread_id={thread_id}")

        for text in stream.text_deltas:
            logging.info(f"Run Streaming: Received text: {text}")
            await send_chat_delta(websocket, "system", text, False)

        await send_chat_delta(websocket, "system", "", True)

    # save run information
    run = client.beta.threads.runs.list(thread_id, limit=1).data[0]
    run_id = run.id
    chat.add_run_id(run_id)
    CHAT_DB.update_chat(chat)

    # retrieve the run response from the last message of the thread
    start_time = time.time()
    logging.info(f"Calling OpenAI to get messages: chat_id={chat.id} thread_id={thread_id}")
    thread_messages = client.beta.threads.messages.list(thread_id)
    response_message = thread_messages.data[0]
    if response_message.role != "assistant":
        logging.warning(f"No AI response backed from context agent: {response_message}")
        await add_assistant_log(chat, "No response", "No AI response backed from context agent", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "No response", chat.chat_context, chat.last_context)
        return

    response_content = response_message.content[0]
    if response_content.type != "text":
        logging.warning(f"Failed to parse OpenAI response: {response_content}")
        chat.set_status("error")
        await add_assistant_log(chat, "Failed to parse response", "Failed to parse OpenAI response", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "AI is confused", chat.chat_context, chat.last_context)
        return

    response_text = response_content.text
    try:
        response_body = json.loads(response_text.value)

        # if assistant found context details
        if "follow_up_question" in response_body:
            follow_up_question = response_body["follow_up_question"]
            chat.add_message("assistant", follow_up_question)
            await add_assistant_log(chat, "follow_up_question", follow_up_question, get_elapsed_time(start_time), websocket)
            logging.info(f"Follow up question added: {follow_up_question}")
            await send_chat(websocket, "follow_up_question", follow_up_question, chat.chat_context, chat.last_context)
            return
        # if assistant found context details with "meaning"
        elif "meaning" in response_body:
            meaning = response_body["meaning"]
            await add_assistant_log(chat, "context_details_found", meaning, get_elapsed_time(start_time), websocket)
            if "top_5_things" in response_body:
                add_assistant_log(chat, "context_activity_found", json.dumps(response_body["top_5_things"]), get_elapsed_time(start_time), websocket)

            logging.info(f"Context details found: chat_id={chat.id} context: {meaning}")
            chat.set_last_context(response_body)
            CHAT_DB.update_chat(chat)

            if chat.chat_context == 2 or chat.chat_context == "2":
                top_things = response_body["top_5_things"]
            elif chat.chat_context == 3 or chat.chat_context == "3":
                top_things = response_body["top_5_things"]
            else:
                top_things = []

            meaning_text = f"สำหรับสิ่งที่คุณถามมา เราเข้าใจว่าคุณหมายถึงสิ่งนี้\n\n{meaning}"
            if len(top_things) > 0:
                meaning_text+="\n\nเรากำลังหาโปรโมชั่นที่เกี่ยวข้องกับกิจกรรมต่อไปนี้ที่เหมาะสมกับคุณ\n\n"
                meaning_text+=", ".join(top_things)

            await send_chat(websocket, "system", meaning_text, chat.chat_context, chat.last_context)
            return
        # if assistant found context details with "product_type"
        elif "product_type" in response_body:
            product_type = response_body["product_type"]
            await add_assistant_log(chat, "context_product_type_found", product_type, get_elapsed_time(start_time), websocket)
            logging.info(f"Context product type found: chat_id={chat.id} product_type: {product_type}")
            chat.set_last_context(response_body)
            CHAT_DB.update_chat(chat)
            await send_chat(websocket, "system", f"AI ของเราเข้าใจว่าคุณกำลังหมายถึงสิ่งเหล่านี้\n{product_type}", chat.chat_context, chat.last_context)
        else:
            chat.set_status("error")
            logging.warning(f"Unexpected chat context details response format: {response_text}")
            await add_assistant_log(chat, "error", f"AI is confused: {response_text}", get_elapsed_time(start_time), websocket)
            await send_chat(websocket, "system", "AI is confused", chat.last_context, chat.last_context)
            return

    except json.JSONDecodeError as e:
        chat.set_status("error")
        logging.warning(f"Failed to parse OpenAI response: {response_text}")
        await add_assistant_log(chat, "Failed to parse response", "Failed to parse OpenAI response", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "AI is confused", chat.last_context, chat.last_context)
        return

async def get_promotions(chat, user, websocket: WebSocket):
    start_time = time.time()

    last_user_message = chat.get_last_user_message()
    if last_user_message is None:
        logging.warning("User message not found")
        return

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
    await add_assistant_log(chat, 
        "promotions_query", 
        f"Querying promotions: q={q}", 
        get_elapsed_time(start_time),
        websocket
    )

    # query for promotions
    start_time = time.time()

    response = requests.get("http://localhost:8001/api/search", params={"queries": q})

    if response.status_code != 200:
        logging.warning(
            "Promotion search engine failed: code{}, {}".format(
                response.status_code, response.json()
            )
        )
        return

    response = response.json()

    if len(response["result"]) == 0:
        chat.set_last_promotions([])
        await add_assistant_log(chat, 
            "promotions_not_found", 
            "Promotions not found", 
            get_elapsed_time(start_time),
            websocket
        )
        return 

    logging.info("Promotions found: {}".format(response["result"]))
    chat.set_last_promotions(response["result"])
    await add_assistant_log(chat,
        "promotions_found",
        json.dumps(response["result"]),
        get_elapsed_time(start_time),
        websocket
    )
    return

async def get_promotions_details(chat, user, websocket: WebSocket):
    def further_assistant(chat) -> str | None:
        last_user_message = chat.get_last_user_message()

        if "s24 ultra" in last_user_message.lower():
            add_assistant_log(
                chat,
                "further_assist",
                "Checking for special recommendations",
                get_elapsed_time(start_time),
                websocket,
            )
            return """
Special instruction: If and only if the conversation is about Samsung S24 Ultra mobile phone,  in addition the promotion recommendation, please also suggest where to buy it from the following links:
Powerbuy : https://www.powerbuy.co.th/th/product/samsung-galaxy-s24-ultra-ram-12gb-256gb-titanium-gray-295650
Banana IT: https://www.bnn.in.th/th/p/smartphone-and-accessories/smartphone/samsung-smartphone/samsung-smartphone-galaxy-s24-ultra-12512-titanium-5g-8806095373393_zvje4w
"""
        else:
            return None

    # provide promotions list to AI
    start_time = time.time()

    thread_id = chat.openai_thread_id
    last_user_message = chat.get_last_user_message()
    promotions = chat.get_last_promotions()
    promotion_text = ""
    for promotion in promotions:
        if (last_user_message in promotion["summary_text"] 
            or last_user_message in promotion["promotion_title"]):
            promotion_text = json.dumps(promotion, ensure_ascii=False)
            
    if promotion_text == "":
        promotion_text = json.dumps(promotions, ensure_ascii=False)

    logging.info(f"Adding promotions to OpenAI thread: chat_id={chat.id}, thread_id={thread_id}")

    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=last_user_message + "\n" + promotion_text
    )
    await add_assistant_log(chat,
        "ask_for_promotion_text",
        "AI is asked to choose the best promotion",
        get_elapsed_time(start_time),
        websocket
    )

    # call OpenAI to create a new run to choose a promotion
    start_time = time.time()
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=os.getenv("OPENAI_PROMOTION_SELECTOR_ID"),
        additional_instructions=further_assistant(chat)
    )

    # save run information
    run_id = run.id
    chat.add_run_id(run_id)
    chat.set_status("running")
    await add_assistant_log(chat,
        "run_created",
        f"Choosing the best promotion. New run created: id={run_id}",
        get_elapsed_time(start_time),
        websocket
    )
    logging.info(f"New run created: id={run_id}. Updating chat: {chat.id}")

    # wait for run to complete
    start_time = time.time()
    run = await wait_run_to_complete(chat)
    chat.set_status("ready")
    await add_assistant_log(chat,
        "run_completed",
        f"Choosing the best promotion. Run completed: id={run_id}",
        get_elapsed_time(start_time),
        websocket
    )

    # retrieve the run response from the last message of the thread
    start_time = time.time()
    logging.info(f"Calling OpenAI to get messages: chat_id={chat.id} thread_id={thread_id}")
    thread_messages = client.beta.threads.messages.list(thread_id)
    response_message = thread_messages.data[0]
    if response_message.role != "assistant":
        logging.warning(f"No AI response backed from response agent: {response_message}")
        await add_assistant_log(chat, "No response", "No AI response backed from response agent", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "No response", chat.chat_context, chat.last_context)
        return

    response_content = response_message.content[0]
    if response_content.type != "text":
        logging.warning(f"Failed to parse OpenAI response: {response_content}")
        chat.set_status("error")
        await add_assistant_log(chat, "Failed to parse response", "Failed to parse OpenAI response", get_elapsed_time(start_time), websocket)
        await send_chat(websocket, "system", "AI is confused", chat.chat_context, chat.last_context)
        return

    credit_cards = user.credit_cards

    try:
        if len(credit_cards) > 0:
            credit_card_promotion = CREDIT_CARD_DB.get_credit_card_promotion(credit_cards[0])
        else:
            credit_card_promotion = None

        if credit_card_promotion:
            default_apologize_phrase = "ขอโทษค่ะ เราขออภัยที่ไม่สามารถให้บริการโปรโมชั่นที่คุณต้องการในขณะนี้\n\nแต่บัตร {} ของคุณสามารถ{}ได้ค่ะ".format(credit_cards[0], credit_card_promotion)
        else:
            default_apologize_phrase = "ขอโทษค่ะ เราขออภัยที่ไม่สามารถให้บริการโปรโมชั่นที่คุณต้องการในขณะนี้ได้ค่ะ"

        promotion_choice = str(json.loads(response_content.text.value)["result"])
        if promotion_choice:
            message_string = default_apologize_phrase
            for _promotion in json.loads(chat.last_promotions):
                if promotion_choice == str(_promotion["id"]):
                    message_string = _promotion["summary_text"]
                    break
        else:
            message_string = default_apologize_phrase
    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse OpenAI response: {response_text}")
        message_string = default_apologize_phrase

    chat.add_message("assistant", message_string)
    chat.set_status("ready")
    await add_assistant_log(chat, 
        "promotion_selected", 
        message_string, 
        get_elapsed_time(start_time), 
        websocket
    )
    await send_chat(websocket, "assistant", message_string, chat.chat_context, chat.last_context)
    return

async def get_token_report(chat, websocket: WebSocket):
    start_time = time.time()
    run_list = chat.openai_run_id

    prompt_tokens_total = 0
    completion_tokens = 0

    for run_id in run_list:
        logging.info(f"Calling OpenAI to get run tokens: chat_id={chat.id} run_id={run_id}")
        run = client.beta.threads.runs.retrieve(
            thread_id=chat.openai_thread_id,
            run_id=run_id
        )

        prompt_tokens_total += run.usage.prompt_tokens
        completion_tokens += run.usage.completion_tokens

    await add_assistant_log(chat,
        "Final Report: TOKEN",
        f"Prompt Tokens: {prompt_tokens_total}\n, Completion Tokens: {completion_tokens},\nTotal Tokens: {prompt_tokens_total + completion_tokens}",
        get_elapsed_time(start_time),
        websocket
    )

async def process_message(data, websocket: WebSocket):
    # validate data object
    if "chat_id" not in data or "user_id" not in data or "message" not in data:
        logging.warning("Invalid message data")
        await send_error(websocket, "400", "Bad request")
        return

    # get chat data
    chat_id = data["chat_id"]
    chat = CHAT_DB.get_chat_by_id(chat_id)
    if chat is None:
        logging.warning(f"Chat not found: id = {chat_id}")
        await send_error(websocket, "404", "Chat not found")
        return

    # get user data
    user_id = data["user_id"]
    user = USER_DB.get_user_by_id(user_id)
    if user is None:
        logging.warning(f"User not found: id = {user_id}")
        await send_error(websocket, "404", "User not found")
        return

    # save user message
    await add_user_message(chat, data["message"], websocket)

    time_log = TimeLog()

    # interpret context
    await get_context(chat, user, websocket)
    time_log.log_time("context")

    # compute context details
    if chat.chat_context > 0:
        await get_context_details(chat, user, websocket)
        time_log.log_time("context_details")

        # search for promotions
        await get_promotions(chat, user, websocket)
        time_log.log_time("promotion")

        # send promotions
        await get_promotions_details(chat, user, websocket)
        time_log.log_time("promotion_details")

        await add_assistant_log(chat,
            "Final Report: TIME",
            f"Total time: {time_log.total_time:.2f}s\nContext: {time_log.context_time:.2f}s\nContext Details: {time_log.context_details_time:.2f}s\nPromotion: {time_log.promotion_time:.2f}s\nPromotion Details: {time_log.promotion_details_time:.2f}s",
            f"{time_log.total_time:.4f}",
            websocket
        )

        await get_token_report(chat, websocket)

async def create_new_chat(data, websocket: WebSocket):
    start_time = time.time()

    # Validate data object
    if "user_id" not in data:
        logging.warning("User ID not found")
        return
    user_id = data["user_id"]
    logging.info(f"Creating new chat for user: {user_id}")

    # call OpenAI API to create a new Thread
    new_thread = client.beta.threads.create()
    thread_id = new_thread.id
    logging.info("Created OpenAI thread: {}".format(thread_id))

    # create new Chat in database
    new_chat = Chat(0, user_id, thread_id)
    new_chat.add_assistant_log(
        "new_chat", 
        "New chat created", 
        response_time = time.time() - start_time)

    # record thread's info to database
    new_chat = CHAT_DB.add_chat(new_chat)
    logging.info("Created new chat: {}".format(new_chat))

    # return chat information
    await websocket.send_json({
        "type": "new_chat_info",
        "data": {
            "chat_id": new_chat.id,
            "user_id": new_chat.user_id
        }
    })
    return new_chat
