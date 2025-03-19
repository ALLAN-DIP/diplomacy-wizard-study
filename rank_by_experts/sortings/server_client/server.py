from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import asyncio

app = FastAPI()

# Global storage for current ranking request
current_request: Optional[List[int]] = None
order_event = asyncio.Event()  # Used to signal when an order is received
ordered_response: Optional[List[int]] = None

class RankRequest(BaseModel):
    array: List[int]

@app.get("/current_rank_request")
async def get_current_rank_request():
    """
    Returns the current ranking request that the user needs to sort.
    """
    return {"to_rank": current_request or []}

@app.post("/current_rank_request")
async def set_current_rank_request(request: RankRequest):
    """
    Sets the current ranking request that the user needs to sort.
    """
    global current_request, ordered_response
    current_request = request.array
    ordered_response = None  # Reset the ordered response
    return {"status": "Request received"}

@app.post("/submit_order")
async def submit_order(request: RankRequest):
    """
    Receives the ordered response from the user and notifies the sorting process.
    """
    global ordered_response
    ordered_response = request.array
    order_event.set()  # Notify that an order is received
    return {"status": "Order received"}

@app.get("/get_ordered_response")
async def get_ordered_response():
    """
    Returns the ordered response from the user.
    """
    if ordered_response is None:
        return {}
    return {"ordered_response": ordered_response}
