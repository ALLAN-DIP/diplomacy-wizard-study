import asyncio
import threading
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Form, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .database import engine, get_db, SessionLocal
from .models import Base, User, Order, RankingRequest
from .auth import register, login, logout, get_current_user

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
Base.metadata.create_all(bind=engine)

# --- Sorting and Ranking Logic ---
sorting_states = None
event_loops = None


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.post("/logout")
def logout_user():
    return logout()


# --- Ranking API ---
@app.get("/ranking/task")
async def get_ranking_task(qid: int = Query(...)):
    """Returns the ranking task for a specific qid."""
    if qid not in sorting_states:
        return {"error": "Invalid qid"}

    state = sorting_states[qid]
    if state["processing"] is False:
        return {"status": "Sorting complete!", "to_rank": None, "sorted_array": state["sorted_array"]}
    return {"to_rank": state["current_ranking_task"]}


@app.post("/ranking/response")
async def receive_ranking_response(qid: int = Query(...), request: RankingRequest = None):
    """Receives a ranked response for a specific qid and signals sorting to continue."""
    if qid not in sorting_states:
        return {"error": "Invalid qid"}

    state = sorting_states[qid]
    state["ranking_result"] = request.elements

    future = asyncio.run_coroutine_threadsafe(set_ranking_event(qid), event_loops[qid])
    future.result()

    return {"status": "Response received"}


async def set_ranking_event(qid: int):
    """Sets the ranking event for a specific qid."""
    sorting_states[qid]["ranking_event"].set()


async def wait_for_ranking(qid: int, elements: list[int]):
    """Sends a ranking request and waits for a response for a specific qid."""
    state = sorting_states[qid]
    state["current_ranking_task"] = elements
    state["ranking_result"] = None

    state["ranking_event"].clear()
    await state["ranking_event"].wait()

    return state["ranking_result"]


async def modified_quicksort(qid: int, arr):
    """Recursive modified quicksort with ranking-based pivot selection."""
    if len(arr) <= 1:
        return arr

    if len(arr) <= 3:
        return await wait_for_ranking(qid, arr)

    pivot_indices = [0, len(arr) // 2, len(arr) - 1]
    pivots = [arr[i] for i in pivot_indices]

    pivots_sorted = await wait_for_ranking(qid, pivots)

    less_than_pivot1 = []
    between_pivot1_and_pivot2 = []
    between_pivot2_and_pivot3 = []
    greater_than_pivot3 = []

    for element in [arr[i] for i in range(len(arr)) if i not in pivot_indices]:
        sorted_elements = await wait_for_ranking(qid, [element] + pivots_sorted)
        element_index = sorted_elements.index(element)

        if element_index == 0:
            less_than_pivot1.append(element)
        elif element_index == 1:
            between_pivot1_and_pivot2.append(element)
        elif element_index == 2:
            between_pivot2_and_pivot3.append(element)
        else:
            greater_than_pivot3.append(element)

    sorted_less = await modified_quicksort(qid, less_than_pivot1)
    sorted_between1_2 = await modified_quicksort(qid, between_pivot1_and_pivot2)
    sorted_between2_3 = await modified_quicksort(qid, between_pivot2_and_pivot3)
    sorted_greater = await modified_quicksort(qid, greater_than_pivot3)

    return (
        sorted_less +
        [pivots_sorted[0]] +
        sorted_between1_2 +
        [pivots_sorted[1]] +
        sorted_between2_3 +
        [pivots_sorted[2]] +
        sorted_greater
    )


def run_sorting(qid: int):
    """Runs the sorting process for a specific qid in a separate thread."""
    global event_loops
    event_loops[qid] = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loops[qid])

    sorting_states[qid]["processing"] = True
    sorting_states[qid]["sorted_array"] = event_loops[qid].run_until_complete(
        modified_quicksort(qid, sorting_states[qid]["array"])
    )
    sorting_states[qid]["processing"] = False
    print(f"Sorting complete for qid {qid}: {sorting_states[qid]['sorted_array']}")


@app.on_event("startup")
async def start_sorting():
    """Starts sorting in background threads for all qids."""
    global sorting_states, event_loops
    with SessionLocal() as db:
        orders = db.query(Order).all()
        qids = set(order.qid for order in orders)
        
        sorting_states = {
            qid: {
                "array": [order.id for order in orders if order.qid == qid],
                "processing": False,
                "sorted_array": [],
                "current_ranking_task": None,
                "ranking_event": asyncio.Event()
            } for qid in qids
        }
        event_loops = {qid: None for qid in qids}  # Store separate event loops per qid

    for qid in range(1, 10):
        thread = threading.Thread(target=run_sorting, args=(qid,), daemon=True)
        thread.start()


@app.get("/sorted_result")
async def get_sorted_result(qid: int = Query(...)):
    """Returns the final sorted array for a specific qid."""
    if qid not in sorting_states:
        return {"error": "Invalid qid"}
    
    state = sorting_states[qid]
    if state["processing"]:
        return {"status": "Sorting in progress"}
    
    return {"sorted_array": state["sorted_array"]}
