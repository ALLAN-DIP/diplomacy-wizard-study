import asyncio
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Global state
sorting_state = {
    "array": [18, 46, 49, 23, 5],
    "sorted_array": [],
    "processing": False
}

ranking_event = asyncio.Event()  # Event to signal ranking completion
current_ranking_task = None
ranking_result = None

# This will store the event loop for cross-thread signaling
event_loop = None  


class RankingRequest(BaseModel):
    elements: List[int]


@app.get("/ranking/task")
async def get_ranking_task():
    """Returns the current ranking task."""
    if current_ranking_task is None:
        return {"task": None}
    return {"to_rank": current_ranking_task}


@app.post("/ranking/response")
async def receive_ranking_response(request: RankingRequest):
    """Receives a ranked response and signals sorting to continue."""
    global ranking_result
    ranking_result = request.elements

    # Ensure the event is set in the correct event loop
    future = asyncio.run_coroutine_threadsafe(set_ranking_event(), event_loop)
    future.result()  # Ensure it executes correctly

    return {"status": "Response received"}


async def set_ranking_event():
    """Sets the ranking event in the correct asyncio loop."""
    ranking_event.set()


async def wait_for_ranking(elements: List[int]):
    """Sends a ranking request and waits for a response."""
    global current_ranking_task, ranking_result
    current_ranking_task = elements
    ranking_result = None

    ranking_event.clear()  # Reset event
    await ranking_event.wait()  # Wait until event is set

    return ranking_result


async def modified_quicksort(arr):
    """Recursive modified quicksort with ranking-based pivot selection."""
    if len(arr) <= 1:
        return arr

    if len(arr) <= 3:
        return await wait_for_ranking(arr)

    pivot_indices = [0, len(arr) // 2, len(arr) - 1]
    pivots = [arr[i] for i in pivot_indices]

    pivots_sorted = await wait_for_ranking(pivots)

    less_than_pivot1 = []
    between_pivot1_and_pivot2 = []
    between_pivot2_and_pivot3 = []
    greater_than_pivot3 = []

    for element in [arr[i] for i in range(len(arr)) if i not in pivot_indices]:
        sorted_elements = await wait_for_ranking([element] + pivots_sorted)
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

    return (
        sorted_less +
        [pivots_sorted[0]] +
        sorted_between1_2 +
        [pivots_sorted[1]] +
        sorted_between2_3 +
        [pivots_sorted[2]] +
        sorted_greater
    )


def run_sorting():
    """Runs the sorting process in a separate thread."""
    global sorting_state, event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    sorting_state["processing"] = True
    sorting_state["sorted_array"] = event_loop.run_until_complete(modified_quicksort(sorting_state["array"]))
    sorting_state["processing"] = False
    print(f"Sorting complete: {sorting_state['sorted_array']}")


@app.on_event("startup")
async def start_sorting():
    """Starts sorting in a background thread."""
    thread = threading.Thread(target=run_sorting, daemon=True)
    thread.start()


@app.get("/sorted_result")
async def get_sorted_result():
    """Returns the final sorted array once sorting is complete."""
    if sorting_state["processing"]:
        return {"status": "Sorting in progress"}
    return {"sorted_array": sorting_state["sorted_array"]}
