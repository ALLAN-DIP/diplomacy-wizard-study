import httpx
import asyncio
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Global variables for tracking the sorting state
sorting_state = {
    "array": [18, 46, 49, 23, 5],  # Initial array
    "sorted_array": [],
    "current_subtasks": [],
    "processing": False
}

# Use an asyncio.Queue to enable communication between event loops
ranking_queue = asyncio.Queue()

class RankingRequest(BaseModel):
    elements: List[int]

async def send_ranking_task(elements: List[int]):
    """Sends a ranking request to the annotation server."""
    async with httpx.AsyncClient() as client:
        await client.post("http://127.0.0.1:8000/ranking/task", json={"elements": elements})

async def wait_for_ranking():
    """Waits for user input using asyncio.Queue instead of asyncio.Event."""
    return await ranking_queue.get()  # Blocks until an item is added

async def modified_quicksort(arr):
    """Recursive modified quicksort that integrates user ranking."""
    if len(arr) <= 1:
        return arr

    if len(arr) <= 3:
        await send_ranking_task(arr)
        return await wait_for_ranking()

    # Pick three pivots and ask the user to rank them
    pivot_indices = [0, len(arr) // 2, len(arr) - 1]
    pivots = [arr[i] for i in pivot_indices]

    await send_ranking_task(pivots)
    pivots_sorted = await wait_for_ranking()

    less_than_pivot1 = []
    between_pivot1_and_pivot2 = []
    between_pivot2_and_pivot3 = []
    greater_than_pivot3 = []

    for element in [arr[i] for i in range(len(arr)) if i not in pivot_indices]:
        await send_ranking_task([element] + pivots_sorted)
        sorted_elements = await wait_for_ranking()
        element_index = sorted_elements.index(element)

        if element_index == 0:
            less_than_pivot1.append(element)
        elif element_index == 1:
            between_pivot1_and_pivot2.append(element)
        elif element_index == 2:
            between_pivot2_and_pivot3.append(element)
        else:
            greater_than_pivot3.append(element)

    sorted_less = await modified_quicksort(less_than_pivot1)
    sorted_between1_2 = await modified_quicksort(between_pivot1_and_pivot2)
    sorted_between2_3 = await modified_quicksort(between_pivot2_and_pivot3)
    sorted_greater = await modified_quicksort(greater_than_pivot3)

    return sorted_less + [pivots_sorted[0]] + sorted_between1_2 + [pivots_sorted[1]] + sorted_between2_3 + [pivots_sorted[2]] + sorted_greater

@app.post("/ranking/response")
async def receive_ranking_response(request: RankingRequest):
    """Handles the ranked response from the annotation server."""
    global sorting_state
    sorting_state["current_subtasks"].append(request.elements)
    await ranking_queue.put(request.elements)  # Store user response and unblock `wait_for_ranking`
    return {"status": "Ranking received"}

def run_sorting():
    """Runs the sorting process in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    global sorting_state
    sorting_state["processing"] = True
    sorting_state["sorted_array"] = loop.run_until_complete(modified_quicksort(sorting_state["array"]))
    sorting_state["processing"] = False
    print(f"Sorting complete: {sorting_state['sorted_array']}")

@app.on_event("startup")
async def start_sorting():
    """Starts sorting in a separate thread so the server remains responsive."""
    thread = threading.Thread(target=run_sorting, daemon=True)
    thread.start()

@app.get("/sorted_result")
async def get_sorted_result():
    """Returns the final sorted array once sorting is complete."""
    if sorting_state["processing"]:
        return {"status": "Sorting in progress"}
    return {"sorted_array": sorting_state["sorted_array"]}
