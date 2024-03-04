from fastapi import FastAPI, Query
from openai import OpenAI

from dotenv import load_dotenv
import json
from promotion_search.search_promotions import (
    search_related_promotions,
    get_unique_promotions,
)

import uvicorn
from typing import List, Annotated

load_dotenv()

app = FastAPI()
GPT_MODEL = "text-embedding-3-large"
openai_client = OpenAI()

TOP_N = 3

promotions = json.load(open("promotion_search/data/promotions.json"))

embed_promotions = json.load(open("promotion_search/data/embed_promotions.json"))


@app.get("/")
def root_api():
    print("INFO: root_apt called")
    return {"message": "Welcome to KBank Special Days API"}


@app.get("/api/search")
def search_promotion(
    q: Annotated[list[str] | None, Query()] = None,
    cols: Annotated[list[str] | None, Query()] = [
        "special_day",
        "promotion_description",
        "promotion_title",
        "shop",
    ],
):
    promotion_results = []
    for query in q:
        promotion_results.extend(
            search_related_promotions(
                query, promotions, embed_promotions, cols, openai_client
            )
        )
    return {"result": get_unique_promotions(promotion_results, TOP_N)}


if __name__ == "__main__":
    print("Starting server at port 8000")
    uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)

# python qdrant/service.py
