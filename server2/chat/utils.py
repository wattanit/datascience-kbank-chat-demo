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

async def send_chat_delta(websocket: WebSocket, message_type: str, message: str, is_completed: bool):
    await websocket.send_json({
            "type": "chat_delta",
            "data": {
                "message_id": "",
                "message": message,
                "message_type": message_type,
                "is_completed": is_completed
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

class TimeLog:
    def __init__(self):
        self.start_datetime = time.time()
        self.last_log_time = self.start_datetime
        self.context_time = 0
        self.context_details_time = 0
        self.promotion_time = 0
        self.promotion_details_time = 0
        self.total_time = 0

    def log_time(self, state: str):
        current_time = time.time()
        elapsed_time = current_time - self.last_log_time
        if state == "context":
            self.context_time = elapsed_time
        elif state == "context_details":
            self.context_details_time = elapsed_time
        elif state == "promotion":
            self.promotion_time = elapsed_time
        elif state == "promotion_details":
            self.promotion_details_time = elapsed_time
        self.last_log_time = current_time
        
        self.total_time = time.time() - self.start_datetime

    