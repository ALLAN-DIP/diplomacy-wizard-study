from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import asyncio

app = FastAPI()

# Global variables for storing the ranking request and user response
current_ranking_task: Optional[List[int]] = None
order_event = asyncio.Event()  # Event to signal when a user response is received
user_sorted_response: Optional[List[int]] = None

class RankingRequest(BaseModel):
    elements: List[int]

@app.get("/ranking/task")
async def get_ranking_task():
    """
    Retrieves the current ranking task that the user needs to sort.
    """
    return {"task": current_ranking_task or []}

@app.post("/ranking/task")
async def set_ranking_task(request: RankingRequest):
    """
    Sets the ranking task that the user needs to sort.
    """
    global current_ranking_task, user_sorted_response
    current_ranking_task = request.elements
    user_sorted_response = None  # Reset the user response
    return {"status": "Task received"}

@app.post("/ranking/response")
async def submit_ranking_response(request: RankingRequest):
    """
    Receives the sorted ranking from the user and notifies the sorting process.
    """
    global user_sorted_response
    user_sorted_response = request.elements
    order_event.set()  # Signal that a ranking response is received
    return {"status": "Response received"}

@app.get("/ranking/response")
async def get_ranking_response():
    """
    Retrieves the user-submitted ranking response.
    """
    if user_sorted_response is None:
        return {}
    return {"sorted_order": user_sorted_response}
