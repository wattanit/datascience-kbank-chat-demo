import os
import time
from fastapi import FastAPI, Query
from utils.searcher import NeuralSearcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
COLLECTION_NAME = os.environ.get('COLLECTION_NAME')

app = FastAPI()

# Create a neural searcher instance
searcher = NeuralSearcher(collection_name=COLLECTION_NAME)

vector_columns = ['vector_promotion_title','vector_promotion_description','vector_shop','vector_special_day']

@app.get("/api/search")
def search(queries: list[str] = Query(..., description="List of query strings"),
            vector_name: list[str] = Query(vector_columns, description="List of vector name")):
    start_time = time.time()
    response = {"result" : searcher.get_context_reranked(queries, vector_name, limit=5, threshold=0.0, limit_per_vec=3)}
    print("Response time is {} sec".format(time.time() - start_time))
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=8001, reload=True)