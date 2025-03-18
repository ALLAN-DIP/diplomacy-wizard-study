import random
import json
import re
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import Form
from .database import SessionLocal
from .models import DiplomacyScenario, Treatment, ContextVSSuggestion, State, Power, GameHardness
from .models import ResponseSimple, ResponseMulti
from .models import PairwiseComparisonSimple, PairwiseComparisonMulti
from .database import engine, get_db, init_db
from .models import Base
from .models import User
from .auth import register, login, logout, get_current_user


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(username: str = Form(...), db: Session = Depends(get_db)):
    register(username, db)
    login(username, db)
    return RedirectResponse(url="/", status_code=303)

@app.post("/logout")
def logout_user():
    return logout()

def get_user_score(user: User, db: Session):
    with SessionLocal() as db:
        simple_annotations = db.query(PairwiseComparisonSimple).filter(PairwiseComparisonSimple.user_id == user.id).count()
        multi_annotations = db.query(PairwiseComparisonMulti).filter(PairwiseComparisonMulti.user_id == user.id).count()
    return {
        "simple": simple_annotations,
        "multi": multi_annotations,
        "total": simple_annotations + multi_annotations,
    }

@app.get("/rank/users", response_class=JSONResponse)
def rank_users():
    """Rank users based on the number of annotations"""
    # loop over users and query simple and multi responses for their user_id
    with SessionLocal() as db:
        users = db.query(User).all()
        user_annotations = {}
        for user in users:
            user_annotations[user.username] = get_user_score(user, db)
    return user_annotations


def get_response_obj_simple(response: ResponseSimple):
    return {
        "id": response.id,
        "participant_name": response.participant_name,
        "map_name": response.map_name,
        "player_name": Power[response.player_name],
        "stance": json.loads(response.stance.replace("'", "\"")),
        "orders": response.orders_str,
        "map": response.map_url,
    }

@app.get("/annotate/simple", response_class=HTMLResponse)
def annotate_simple(request: Request, user: User = Depends(get_current_user)):
    with SessionLocal() as db:
        # select a qid between 1 and 9
        qid = random.randint(1, 9)
        responses = db.query(ResponseSimple).filter(ResponseSimple.qid == qid).all()
    weights = [1 / (response.number_of_annotations + 1) for response in responses]
    r1, r2 = random.choices(responses, weights=weights, k=2)
    return templates.TemplateResponse("annotate_simple.html", {
        "request": request,
        "user": user,
        "response1": get_response_obj_simple(r1),
        "response2": get_response_obj_simple(r2),
        "user_score": get_user_score(user, db)})

@app.post("/annotate/simple")
def annotate_simple_post(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 > 2)"""
    with SessionLocal() as db:
        # Update the number of annotations for each response
        response1 = db.query(ResponseSimple).filter(ResponseSimple.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseSimple).filter(ResponseSimple.id == response2_id).first()
        response2.number_of_annotations += 1
        
        # Save the annotations to PairwiseComparisonSimple
        annotation = PairwiseComparisonSimple(
            user_id=user.id,
            preferred_response_id=response1_id,
            other_response_id=response2_id)
        db.add(annotation)
        db.commit()
    return RedirectResponse(url="/annotate/simple", status_code=303)

@app.post("/annotate/simple/equals")
def annotate_simple_equals(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 = 2)"""
    with SessionLocal() as db:
        # Update the number of annotations for each response
        response1 = db.query(ResponseSimple).filter(ResponseSimple.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseSimple).filter(ResponseSimple.id == response2_id).first()
        response2.number_of_annotations += 1
        
        # Save the annotations to PairwiseComparisonSimple
        annotation = PairwiseComparisonSimple(
            user_id=user.id,
            preferred_response_id=response1_id,
            other_response_id=response2_id)
        db.add(annotation)
        annotation = PairwiseComparisonSimple(
            user_id=user.id,
            preferred_response_id=response2_id,
            other_response_id=response1_id)
        db.commit()
    return RedirectResponse(url="/annotate/simple", status_code=303)


def get_response_obj_multi(response: ResponseMulti):
    return {
        "id": response.id,
        "participant_name": response.participant_name,
        "map_name": response.map_name,
        "player_name": Power[response.player_name],
        "stance": json.loads(response.stance.replace("'", "\"")),
        "orders": {
            0: response.orders0_str,
            1: response.orders1_str,
        },
        "map": {
            0: response.map_url0,
            1: response.map_url1,
        },
    }

@app.get("/annotate/multi", response_class=HTMLResponse)
def annotate_multi(request: Request, user: User = Depends(get_current_user)):
    with SessionLocal() as db:
        # select a qid between 1 and 9
        qid = random.randint(1, 9)
        responses = db.query(ResponseMulti).filter(ResponseMulti.qid == qid).all()
    weights = [1 / (response.number_of_annotations + 1) for response in responses]
    r1, r2 = random.choices(responses, weights=weights, k=2)
    return templates.TemplateResponse("annotate_multi.html", {
        "request": request,
        "user": user,
        "response1": get_response_obj_multi(r1),
        "response2": get_response_obj_multi(r2),
        "user_score": get_user_score(user, db)})

@app.post("/annotate/multi")
def annotate_multi_post(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 > 2)"""
    with SessionLocal() as db:
        # Update the number of annotations for each response
        response1 = db.query(ResponseMulti).filter(ResponseMulti.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseMulti).filter(ResponseMulti.id == response2_id).first()
        response2.number_of_annotations += 1
        
        # Save the annotations to PairwiseComparisonMulti
        annotation = PairwiseComparisonMulti(
            user_id=user.id,
            preferred_response_id=response1_id,
            other_response_id=response2_id)
        db.add(annotation)
        db.commit()
    return RedirectResponse(url="/annotate/multi", status_code=303)

@app.post("/annotate/multi/equals")
def annotate_multi_equals(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 = 2)"""
    with SessionLocal() as db:
        # Update the number of annotations for each response
        response1 = db.query(ResponseMulti).filter(ResponseMulti.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseMulti).filter(ResponseMulti.id == response2_id).first()
        response2.number_of_annotations += 1
        
        # Save the annotations to PairwiseComparisonMulti
        annotation = PairwiseComparisonMulti(
            user_id=user.id,
            preferred_response_id=response1_id,
            other_response_id=response2_id)
        db.add(annotation)
        annotation = PairwiseComparisonMulti(
            user_id=user.id,
            preferred_response_id=response2_id,
            other_response_id=response1_id)
        db.commit()
    return RedirectResponse(url="/annotate/multi", status_code=303)
