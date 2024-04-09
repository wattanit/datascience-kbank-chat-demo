from fastapi import APIRouter, WebSocket
import logging
import json
from server2.chat.processor import process_message, create_new_chat

logging.basicConfig(level=logging.INFO)

router = APIRouter()

# websocket received message schema:
# action: ["new_user_message", "create_new_chat"]
# data: 
#     action.new_user_message: 
#         chat_id: number
#         user_id: number
#         message: str
#     action.create_new_chat:
#         user_id: number

# websocket response message schema:
# type: ["chat", "activity", "error"]
# data:
#     type.chat:
#         message_id: str
#         message: str
#         message_type: ["user", "assistant", "system"]
#         context: str
#         context_details: str
#     type.activity:
#         message_id: str
#         message_header: str
#         message_body: str
#         elasped_time: str     
#     type.error:
#         error_code: str
#         error_message: str

@router.websocket("/api/chat-socket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        request_raw = await websocket.receive_text()
        logging.info(f"Received socket message. (raw data : {request_raw})")

        try:
            req = json.loads(request_raw)
            logging.info("Received data: {}".format(req))

            if "action" in req:
                if not "data" in req:
                    logging.warning(f"Received data contains no required payload: {req}")
                    continue

                # switch action
                if req["action"] == "new_user_message":
                    await process_message(req["data"], websocket)
                elif req["action"] == "create_new_chat":
                    await create_new_chat(req["data"], websocket)
                    
            else:
                logging.warning(f"Received data contains no action: {req}")
                continue

        except json.JSONDecodeError:
            logging.warning(f"Received invalid JSON: {request_raw}")
            continue
