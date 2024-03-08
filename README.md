# KBANK Credit Card Assistant DEMO
This project is a demonstration of a credit card assistant for KBANK. It includes a promotion search engine, backend server, and frontend development server. Follow the steps below to run the development servers.

## Development Setup

### Prerequisites

Make sure you have Poetry and NPM installed for development.

### 1. Start promotion search engine
**Install Dependencies**
```bash
pip install qdrant-client openai git+https://github.com/openai/whisper.git python-dotenv
```

**Configure Environment Variables**

Create a `.env` file in the `promotion_search` directory with the following content:
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

**Start Database**

Pull the Qdrant Docker image and run it:
```bash
docker pull qdrant/qdrant

docker run --rm -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

**Start Services**

Navigate to the `promotion_search` directory and run the following commands:
```bash
poetry run python promotion_search/src/embedding.py
poetry run python promotion_search/src/uploading.py
poetry run python promotion_search/src/service.py
```

### 2. Start Backend Server

**Configure Environment Variables**

Create a `.env` file in the root directory with the following content:
```bash
OPENAI_CONTEXT_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_PRODUCT_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_OCCASION_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_PLACE_AGENT_ID=your-agent-id
OPENAI_RESPONSE_AGENT_ID=your-agent-id
OPENAI_API_KEY=your-api-key
```

**Start Server**
```bsah
poetry run uvicorn server.main:app --reload --port 8000
```

### 3. Start Frontend Server
Navigate to the `www` directory and run the following commands:
```bash
cd www
npm install
npm start
```

---

Now you should have the promotion search engine, backend server, and frontend development server running. 
- Access the frontend of KBANK Credit Card Assistant DEMO at http://localhost:3000.
- Access the Qdrant dashboard UI at http://localhost:6333/dashboard.