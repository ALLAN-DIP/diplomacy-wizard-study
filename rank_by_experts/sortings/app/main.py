import asyncio
import threading
import random
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from .database import engine, get_db, SessionLocal
from .models import Base, User
from .auth import register, login, logout, get_current_user
from .models import Base, User, RankingRequest

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
Base.metadata.create_all(bind=engine)

# --- Sorting and Ranking Logic ---
sorting_state = {
    "array": [18, 46, 49, 23, 5],  # Example array; replace with dynamic input
    "sorted_array": [],
    "processing": False
}



ranking_event = asyncio.Event()
current_ranking_task = None
ranking_result = None
event_loop = None  # Will store the event loop for cross-thread signaling


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(username: str = Form(...), db: Session = Depends(get_db)):
    register(username, db)
    result = login(username, db)
    response = RedirectResponse(url="/", status_code=303)
    for cookie in result.headers.getlist("set-cookie"):
        response.headers.append("set-cookie", cookie)
    return response


@app.post("/logout")
def logout_user():
    return logout()


# --- Ranking API ---
@app.get("/ranking/task")
async def get_ranking_task():
    """Returns the current ranking task."""
    if sorting_state["processing"] is False:
        return {"status": "Sorting complete!", "to_rank": None, "sorted_array": sorting_state["sorted_array"]}
    return {"to_rank": current_ranking_task}


@app.post("/ranking/response")
async def receive_ranking_response(request: RankingRequest):
    """Receives a ranked response and signals sorting to continue."""
    global ranking_result
    ranking_result = request.elements

    future = asyncio.run_coroutine_threadsafe(set_ranking_event(), event_loop)
    future.result()

    return {"status": "Response received"}


async def set_ranking_event():
    """Sets the ranking event in the correct asyncio loop."""
    ranking_event.set()


async def wait_for_ranking(elements: list[int]):
    """Sends a ranking request and waits for a response."""
    global current_ranking_task, ranking_result
    current_ranking_task = elements
    ranking_result = None

    ranking_event.clear()
    await ranking_event.wait()

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
