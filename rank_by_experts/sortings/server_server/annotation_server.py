from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import httpx
import asyncio

app = FastAPI()

current_task: Optional[List[int]] = None
sorted_response: Optional[List[int]] = None
order_event = asyncio.Event()

class RankingTask(BaseModel):
    elements: List[int]

@app.post("/ranking/task")
async def set_ranking_task(request: RankingTask):
    """Receives a ranking task from the middle server."""
    global current_task, sorted_response
    current_task = request.elements
    sorted_response = None
    order_event.clear()
    print(f"Received ranking task: {current_task}")
    return {"status": "Task received"}

@app.get("/ranking/task")
async def get_ranking_task():
    """Returns the current ranking task."""
    return {"to_rank": current_task or []}

@app.post("/ranking/response")
async def submit_sorted_response(request: RankingTask):
    """Receives a sorted response from the user and notifies the middle server."""
    global sorted_response
    sorted_response = request.elements
    order_event.set()
    print(f"Received sorted response: {sorted_response}")

    # Notify the middle server
    async with httpx.AsyncClient() as client:
        await client.post("http://127.0.0.1:8001/ranking/response", json={"elements": sorted_response})
    
    return {"status": "Response received"}

@app.get("/ranking/response")
async def get_sorted_response():
    """Waits until the ranking response is available."""
    await order_event.wait()
    return {"sorted_order": sorted_response}
