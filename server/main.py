import uvicorn
from fastapi import FastAPI
from server.user import router as user_router
from server.chat import router as chat_router

app = FastAPI()
app.include_router(user_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "K-Bank Credit Chat DEMO API"}

def start():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)