# KBANK Credit Card Assistant DEMO

## Run devepment server

_requires Poetry and NPM for development_

1. start promotion search engine
- add `.env` file
```bash
OPENAI_API_KEY=your-openai-api-key

OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSION=1536
OPENAI_EMBEDDING_ENCODING=cl100k_base
OPENAI_MAX_TOKENS_ENCODING=8000

QDRANT_API_KEY=
QDRANT_URL=http://localhost:6333/
COLLECTION_NAME=kbank_promotions
```
- database
```bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```
- service
```bash
cd promotion_search
python src/embedding.py
python src/uploading.py
python src/service.py
```

2. start backend server
- add .env file
```bash
OPENAI_CONTEXT_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_PRODUCT_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_OCCASION_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_PLACE_AGENT_ID=your-agent-id
OPENAI_RESPONSE_AGENT_ID=your-agent-id
OPENAI_API_KEY=your-api-key
```
- service
```bsah
poetry run uvicorn server.main:app --reload --port 8000
```

3. start frontend development server
```bash
cd www
npm install
npm start
```