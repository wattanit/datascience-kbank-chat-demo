# KBANK Credit Card Assistant DEMO

## Run devepment server

_requires Poetry and NPM for development_

1. start promotion search engine
```
poetry run uvicorn promotion_search.service:app --reload --port 8001
```

2. start backend server
```
poetry run uvicorn server.main:app --reload --port 8000
```

3. start frontend development server
```
cd www
npm install # if needed
npm start
```