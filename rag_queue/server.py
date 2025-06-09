from fastapi import FastAPI, Query
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()


@app.get('/')
def root():
    return {"status": "Server is running"}


@app.post('/chat')
def chat(
    query: str = Query(..., description="Chat Message")
):
    print("Enqueuing job:", query)
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}


# Folder - rag_queue
# server file - 2 routes - root and chat(expects a query)
# to run app , main file made
# in main uvicorn will run app

# 65f0fac1-e345-4552-90b8-d8dd1df1d1ab
# fadac015-0576-4222-817d-4ef2bccb6537
