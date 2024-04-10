import time
from fastapi import WebSocket

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