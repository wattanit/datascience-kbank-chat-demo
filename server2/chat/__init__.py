from fastapi import APIRouter, WebSocket
import logging
from chat.processor import process_message, create_new_chat

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

def get_elapsed_time(start_time: float) -> str:
    now = time.time()
    elapsed_time = now - start_time
    return "{:.3f} seconds".format(elapsed_time)

async def send_activity(websocket: WebSocket, header: str, message: str, elasped_time: str):
    await websocket.send_json({
            "type": "activity", 
            "data": {
                "message_id": "",
                "message_header": header,
                "message_body": message,
                "elasped_time": elasped_time
            }
        })

async def send_chat(websocket: WebSocket, message_type: str, message: str, context: str = "", context_details: str = ""):
    await websocket.send_json({
            "type": "chat",
            "data": {
                "message_id": "",
                "message": message,
                "message_type": message_type,
                "context": context,
                "context_details": context_details
            }
        })

async def send_error(websocket: WebSocket, error_code: str, error_message: str):
    await websocket.send_json({
            "type": "error",
            "data": {
                "error_code": error_code,
                "error_message": error_message
            }
        })

@router.websocket("/api/chat-socket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        request_raw = await websocket.receive_text()
        logging.info(f"Received socket message. (raw data : {request_raw})")

        try:
            req = json.loads(request_raw)
            logging.info("Received data: {}".format(req))````````````  

            if "action" in data:
                if not "data" in req:
                    logging.warning(f"Received data contains no required payload: {req}")
                    continue

                # switch action
                if req["action"] == "new_user_message":
                    await process_message(req["data"], websocket)
                elif req["action"] == "create_new_chat":
                    create_new_chat(req["data"], websocket)
                    
            else:
                logging.warning(f"Received data contains no action: {req}")
                continue

        except json.JSONDecodeError:
            logging.warning(f"Received invalid JSON: {request_raw}")
            continue


@router.post("/api/chat")
async def create_chat():
    return {"message": "Create chat not supported"}