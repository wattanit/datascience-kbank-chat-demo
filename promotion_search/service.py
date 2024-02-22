from fastapi import FastAPI
from openai import OpenAI

from dotenv import load_dotenv
import json
from promotion_search.search_promotions import search_related_promotions, get_unique_promotions
import uvicorn

load_dotenv()

app = FastAPI()
GPT_MODEL = "text-embedding-3-large"
openai_client = OpenAI()

TOP_N = 3

promotions = json.load(

    open("promotion_search/data/promotions.json")
)

embed_promotions = json.load(
    open(
        "promotion_search/data/embed_promotions.json"
    )
)


@app.get("/")
def root_api():
    print("INFO: root_apt called")
    return {"message": "Welcome to KBank Special Days API"}


@app.get("/api/search")
def search_promotion(q1: str, q2: str):
    print("INFO: search_promotion called")
    result_1 = search_related_promotions(
        q1,
        promotions,
        embed_promotions,
        openai_client,
    )
    result_2 = search_related_promotions(
        q2,
        promotions,
        embed_promotions,
        openai_client,
    )
    return {"result": get_unique_promotions(result_1 + result_2, TOP_N)}


if __name__ == "__main__":
    print("Starting server at port 8000")
    uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)

# python qdrant/service.py
