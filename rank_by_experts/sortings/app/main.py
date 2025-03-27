import asyncio
import threading
import json
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Form, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .database import engine, get_db, SessionLocal
from .models import Base, User, Order, RankingRequest, Comparison, CompleteRanking
from .auth import register, login, logout, get_current_user
import logging

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
Base.metadata.create_all(bind=engine)
logging.basicConfig(filename='app.log', level=logging.DEBUG)


# --- Sorting and Ranking Logic ---
sorting_states = None
event_loops = None


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    logging.info("Register page accessed")
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(username: str = Form(...), db: Session = Depends(get_db)):
    register(username, db)
    result = login(username, db)
    response = RedirectResponse(url="/", status_code=303)
    for cookie in result.headers.getlist("set-cookie"):
        response.headers.append("set-cookie", cookie)
        logging.info(f"User {username} registered with session id {result.headers['set-cookie']}")
    return response

@app.post("/logout")
def logout_user():
    return logout()


def assign_qid(db: Session, user: User):
    """Assigns a new qid to a user if they need one."""
    available_qids = set(order.qid for order in db.query(Order).all()) - set(
        user.last_qid_working_on for user in db.query(User).all()
    ) - set(ranking.qid for ranking in db.query(CompleteRanking).all())

    if not available_qids:
        return None  # No new qids available

    new_qid = min(available_qids)  # Assign the smallest available qid
    user.last_qid_working_on = new_qid
    db.commit()
    logging.info(f"User {user.username} assigned qid {new_qid}")
    return new_qid


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Serves the ranking UI for the assigned qid."""
    
    if user.last_qid_working_on == 0 or user.last_qid_working_on not in sorting_states:
        new_qid = assign_qid(db, user)
        if new_qid is None:
            return templates.TemplateResponse("done.html", {"request": request})

    qid = user.last_qid_working_on
    orders = db.query(Order).filter(Order.qid == qid).all()
    state = sorting_states[qid]
    if state["processing"] is False:
        return templates.TemplateResponse("done.html", {"request": request})

    orders_filtered = [order for order in orders if order.orders_id in sorting_states[qid]["current_ranking_task"]]

    last_ranking = request.cookies.get(f"last_ranking")
    if last_ranking:
        last_ranking_ids = [int(order_id) for order_id in json.loads(last_ranking)]
        logging.info(f"User {user.username} fetched last ranking for qid {qid}: {last_ranking_ids} vs {[o.orders_id for o in orders_filtered]}")
        try:
            temp = [None] * len(orders_filtered)
            for i, order in enumerate(orders_filtered):
                if order.orders_id in last_ranking_ids:
                    temp[last_ranking_ids.index(order.orders_id)] = order
            for i, order in enumerate(orders_filtered):
                if order.orders_id not in last_ranking_ids:
                    temp[temp.index(None)] = order
            logging.info(f"User {user.username} reordered orders for qid {qid} as {[o.orders_id for o in temp]}")
            orders_filtered = temp
        except (ValueError, IndexError):
            logging.info(f"User {user.username} fetched last ranking for qid {qid} with missing orders")

    
    logging.info(f"Fetched orders for qid {qid} for user {user.username} when orders {[o.orders_id for o in orders]}: {[o.orders_id for o in orders_filtered]}")
    logging.info(f"User {user.username} working on qid {qid} with orders {sorting_states[qid]['current_ranking_task']}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "orders": orders_filtered,
        "qid": qid,
        "stance_friends": [k for k,v in dict(eval(orders[0].stance)).items() if v > 0],
        "stance_foes": [k for k,v in dict(eval(orders[0].stance)).items() if v < 0],
        "stance_neutral": [k for k,v in dict(eval(orders[0].stance)).items() if v == 0]
    })


@app.post("/")
async def submit_ranking(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Receives a ranking response and stores it."""
    form_data = await request.form()
    ranking_json = form_data.get("ranking")
    if not ranking_json:
        return RedirectResponse(url="/", status_code=303)

    ranking_list = [int(order_id) for order_id in json.loads(ranking_json)]
    qid = user.last_qid_working_on
    db.add(Comparison(qid=qid, user_id=user.id, comparison=ranking_json))
    db.commit()

    # Signal sorting to continue
    sorting_states[qid]["ranking_result"] = ranking_list
    future = asyncio.run_coroutine_threadsafe(set_ranking_event(qid), event_loops[qid])
    future.result()

    logging.info(f"User {user.username} submitted ranking for qid {qid} as {ranking_list}")

    # If sorting is complete, assign a new qid
    if not sorting_states[qid]["processing"]:
        new_qid = assign_qid(db, user)
        if new_qid is None:
            return RedirectResponse(url="/", status_code=303)

    # Store the ranking in a cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="last_ranking", value=ranking_list, max_age=86400)

    return response


@app.get("/sorted_result", response_class=HTMLResponse)
def get_sorted_result(request: Request, qid: int = Query(...), db: Session = Depends(get_db)):
    """Returns the final sorted array as an HTML page."""
    if qid not in sorting_states:
        return templates.TemplateResponse("sorted_results.html", {"request": request, "qid": qid, "orders": []})

    state = sorting_states[qid]
    
    if state["processing"]:
        return HTMLResponse(content="<h2>Sorting is still in progress...</h2>", status_code=200)

    sorted_order_ids = state["sorted_array"]
    if not sorted_order_ids:
        return templates.TemplateResponse("sorted_results.html", {"request": request, "qid": qid, "orders": []})

    # Fetch order details from DB
    orders = db.query(Order).filter(Order.qid == qid, Order.orders_id.in_(sorted_order_ids)).all()

    # Sort them based on stored order
    order_dict = {order.orders_id: order for order in orders}
    sorted_orders = [order_dict[oid] for oid in sorted_order_ids if oid in order_dict]

    return templates.TemplateResponse("sorted_results.html", {"request": request, "qid": qid, "orders": sorted_orders})


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
    logging.info(f"Sorting complete for qid {qid}: {sorting_states[qid]['sorted_array']}")
    event_loops[qid].close()
    with SessionLocal() as db:
        db.query(CompleteRanking).filter(CompleteRanking.qid == qid).delete()
        db.add(CompleteRanking(qid=qid, ranking=json.dumps(sorting_states[qid]["sorted_array"])))
        db.commit()


@app.on_event("startup")
async def start_sorting():
    """Starts sorting in background threads for all qids."""
    global sorting_states, event_loops
    with SessionLocal() as db:
        orders = db.query(Order).all()
        qids = set(order.qid for order in orders)
        
        sorting_states = {
            qid: {
                "array": [order.orders_id for order in orders if order.qid == qid],
                "processing": False,
                "sorted_array": [],
                "current_ranking_task": None,
                "ranking_event": asyncio.Event()
            } for qid in qids
        }
        event_loops = {qid: None for qid in qids}

    for qid in qids:
        thread = threading.Thread(target=run_sorting, args=(qid,), daemon=True)
        thread.start()

