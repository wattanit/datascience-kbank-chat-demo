# Neural Search Service

This project aims to create a neural search service using Qdrant as the database and FastAPI for the search service.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install qdrant-client
pip install openai
pip install git+https://github.com/openai/whisper.git
pip install python-dotenv
```

Create a .env file in the project root directory and add the following environment variables:

> Note: QDRANT_API_KEY can be empthy
> Note: Recommended to use the text-embedding-3-large model over the text-embedding-3-small model for better results in Thai languages.

```bash
OPENAI_API_KEY=your-openai-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSION=1536
OPENAI_EMBEDDING_ENCODING=cl100k_base
OPENAI_MAX_TOKENS_ENCODING=8000

QDRANT_API_KEY=
QDRANT_URL=http://localhost:6333/
COLLECTION_NAME=kbank_promotions
```
For more information about OpenAI Embeddings, refer to the [documentation](https://platform.openai.com/docs/guides/embeddings).

## Setting up Qdrant Database

1. Download the latest Qdrant image from Dockerhub:
```bash
docker pull qdrant/qdrant
```

2. Run the Qdrant service:
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```
All data will be stored in the `./qdrant_storage` directory.

3. Qdrant is now accessible:
- REST API: [localhost:6333](http://localhost:6333)
- Web UI: [localhost:6333/dashboard](http://localhost:6333/dashboard)
- GRPC API: [localhost:6334](http://localhost:6334)

For more information about Qdrant, refer to the [documentation](https://qdrant.tech/documentation/overview/).

## Embedding data using OpenAI

Run the program:

```bash
python src/embedding.py
```

The program will prompt you to enter the name of the file you want to embed. Type the file name when prompted (e.g., my_file.csv).

> Note: Before running the program, ensure you edit the embedding.py file to specify which column you want to embed.

## Uploading embed data to Qdrant

Run the program:

```bash
python src/uploading.py
```

The program will prompt you to enter the name of the file you want to embed. Type the file name when prompted (e.g., my_file.csv).

## Running the Search Service
Run the FastAPI search service:
```bash
python src/service.py
```

The search service is now accessible at [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) for interactive API documentation.


---
# Neural Search Service (Docker)
## Environment
```bash
OPENAI_API_KEY=your-openai-key

OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSION=3072
OPENAI_EMBEDDING_ENCODING=cl100k_base
OPENAI_MAX_TOKENS_ENCODING=8000

QDRANT_API_KEY=
QDRANT_URL=http://db:6334/
COLLECTION_NAME=kbank_promotions
```

## Build API image
```bash
docker build -t kbank-search-engine:latest .
```

## Start system
```bash
docker-compose up
```

## Initnitial database
- Run container in background:
``` bash
docker run -d kbank-search-engine
```
- Run bash shell in existing container:
> tofind `container_id` use `docker ps -a` for list all container in Docker system 
```bash
docker exec -it <container_id> bash
```

- embedding data
```bash
python3 src/embedding.py 
```

- uploading data
```bash
python3 src/uploading.py
```