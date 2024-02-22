# KBANK Credit Card Assistant DEMO

## Run devepment server

1. start promotion search engine
```
uvicorn promotion_search.service:app --reload --port 8001
```

2. start backend server
```
uvicorn server.main:app --reload --port 8000
```

3. start frontend development server
```
cd www
npm start
```