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
OPENAI_PROMOTION_SELECTOR_ID=your-agent-id
OPENAI_ORGANIZATION=your-organization-id
OPENAI_PROJECT=your-project-id
OPENAI_API_KEY=your-api-key
```

**Start Server**
```bsah
poetry run uvicorn server2.main:app --reload --port 8000
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


## Deployment

### Prerequisite

For manual deployment on standard linux server, the following packages are required:
- docker
- nginx
- certbot (optional Let's Encrypt SSL)
- git

### Build steps
#### 1. Clone the project repository
   
#### 2. Build promotion_search service

Run command
```bash
cd promotion_search
docker build -t promotion-search:latest .
```

#### 3. Build Frontend app
```bash
cd ../www
npm run build
docker build -t credit-demo-frontend:latest .
```

#### 4. Build backend service
```bash
cd ../server2
docker build -t credit-demo-backend:lastest .
```

#### 5. Configure ENV 

The ```.env``` file should contains the following items
```
OPENAI_CONTEXT_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_PRODUCT_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_OCCASION_AGENT_ID=your-agent-id
OPENAI_SPECIALIST_PLACE_AGENT_ID=your-agent-id
OPENAI_PROMOTION_SELECTOR_ID=your-agent-id
OPENAI_ORGANIZATION=your-organization-id
OPENAI_PROJECT=your-project-id
OPENAI_API_KEY=your-api-key
```

#### 6. Start services
```
cd ..
docker-compose up -d
```

#### 7. Migrate data (optional)
```
docker exec -it <promotion_search's app id> bash
python3 src/embedding.py
python3 src/uploading.py
```

#### 8. Configure Nginx


