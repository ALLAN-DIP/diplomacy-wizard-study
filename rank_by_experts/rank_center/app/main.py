import random
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from .database import engine, get_db
from .models import Base, User, ResponseSimple, ResponseMulti, PairwiseComparisonSimple, PairwiseComparisonMulti
from .auth import register, login, logout, get_current_user
from .functions import get_user_annotations, get_response_obj_simple, get_response_obj_multi
from .database import SessionLocal

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
    result = login(username, db)
    response = RedirectResponse(url="/", status_code=303)
    for cookie in result.headers.getlist("set-cookie"):
        response.headers.append("set-cookie", cookie)
    return response


@app.post("/logout")
def logout_user():
    return logout()


@app.get("/rank/users", response_class=JSONResponse)
def rank_users():
    """Rank users based on the number of annotations"""
    with SessionLocal() as db:
        users = db.query(User).all()
        user_annotations = {user.username: get_user_annotations(user, db) for user in users}
    return user_annotations

@app.get("/rank/responses", response_class=JSONResponse)
def rank_responses():
    """Rank responses based on the number of annotations"""
    with SessionLocal() as db:
        simple_responses = db.query(ResponseSimple).all()
        simple_annotations = {response.id: response.number_of_annotations for response in simple_responses}
        multi_responses = db.query(ResponseMulti).all()
        multi_annotations = {response.id: response.number_of_annotations for response in multi_responses}
    return {"simple": simple_annotations, "multi": multi_annotations}

@app.get("/show/pairwise/simple", response_class=JSONResponse)
def show_pairwise_simple():
    """Show pairwise annotations for simple responses"""
    with SessionLocal() as db:
        annotations = db.query(PairwiseComparisonSimple).all()
    return [{"user_id": annotation.user_id, "preferred_response_id": annotation.preferred_response_id, "other_response_id": annotation.other_response_id} for annotation in annotations]

@app.get("/show/pairwise/multi", response_class=JSONResponse)
def show_pairwise_multi():
    """Show pairwise annotations for multi responses"""
    with SessionLocal() as db:
        annotations = db.query(PairwiseComparisonMulti).all()
    return [{"user_id": annotation.user_id, "preferred_response_id": annotation.preferred_response_id, "other_response_id": annotation.other_response_id} for annotation in annotations]

@app.get("/graph/simple", response_class=JSONResponse)
def graph_simple(qid: int):
    with SessionLocal() as db:
        responses = db.query(ResponseSimple).filter(ResponseSimple.qid == qid).all()
        annotations = db.query(PairwiseComparisonSimple).all()
    graph = {response.id: [] for response in responses}
    for annotation in annotations:
        if annotation.other_response_id in graph:
            graph[annotation.other_response_id].append(annotation.preferred_response_id)
    return graph

@app.get("/graph/multi", response_class=JSONResponse)
def graph_multi(qid: int):
    with SessionLocal() as db:
        responses = db.query(ResponseMulti).filter(ResponseMulti.qid == qid).all()
        annotations = db.query(PairwiseComparisonMulti)
    graph = {response.id: [] for response in responses}
    for annotation in annotations:
        if annotation.other_response_id in graph:
            graph[annotation.other_response_id].append(annotation.preferred_response_id)
    return graph


@app.get("/annotate/simple", response_class=HTMLResponse)
def annotate_simple(request: Request, user: User = Depends(get_current_user)):
    with SessionLocal() as db:
        qid = random.randint(1, 9)
        responses = db.query(ResponseSimple).filter(ResponseSimple.qid == qid).all()
    weights = [1 / (response.number_of_annotations + 1) for response in responses]
    r1, r2 = random.choices(responses, weights=weights, k=2)
    return templates.TemplateResponse("annotate_simple.html", {
        "request": request,
        "user": user,
        "response1": get_response_obj_simple(r1),
        "response2": get_response_obj_simple(r2)})


@app.post("/annotate/simple")
def annotate_simple_post(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 > 2)"""
    with SessionLocal() as db:
        response1 = db.query(ResponseSimple).filter(ResponseSimple.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseSimple).filter(ResponseSimple.id == response2_id).first()
        response2.number_of_annotations += 1
        annotation = PairwiseComparisonSimple(user_id=user.id, preferred_response_id=response1_id, other_response_id=response2_id)
        user = db.merge(user)
        user.score += 1
        db.add(annotation)
        db.commit()
    return RedirectResponse(url="/annotate/simple", status_code=303)


@app.post("/annotate/simple/equals")
def annotate_simple_equals(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 = 2)"""
    with SessionLocal() as db:
        response1 = db.query(ResponseSimple).filter(ResponseSimple.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseSimple).filter(ResponseSimple.id == response2_id).first()
        response2.number_of_annotations += 1
        annotation1 = PairwiseComparisonSimple(user_id=user.id, preferred_response_id=response1_id, other_response_id=response2_id)
        annotation2 = PairwiseComparisonSimple(user_id=user.id, preferred_response_id=response2_id, other_response_id=response1_id)
        user = db.merge(user)
        user.score += 1
        db.add(annotation1)
        db.add(annotation2)
        db.commit()
    return RedirectResponse(url="/annotate/simple", status_code=303)


@app.get("/annotate/multi", response_class=HTMLResponse)
def annotate_multi(request: Request, user: User = Depends(get_current_user)):
    with SessionLocal() as db:
        qid = random.randint(1, 9)
        responses = db.query(ResponseMulti).filter(ResponseMulti.qid == qid).all()
    weights = [1 / (response.number_of_annotations + 1) for response in responses]
    r1, r2 = random.choices(responses, weights=weights, k=2)
    return templates.TemplateResponse("annotate_multi.html", {
        "request": request,
        "user": user,
        "response1": get_response_obj_multi(r1),
        "response2": get_response_obj_multi(r2)})


@app.post("/annotate/multi")
def annotate_multi_post(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 > 2)"""
    with SessionLocal() as db:
        response1 = db.query(ResponseMulti).filter(ResponseMulti.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseMulti).filter(ResponseMulti.id == response2_id).first()
        response2.number_of_annotations += 1
        annotation = PairwiseComparisonMulti(user_id=user.id, preferred_response_id=response1_id, other_response_id=response2_id)
        user = db.merge(user)
        user.score += 1
        db.add(annotation)
        db.commit()
    return RedirectResponse(url="/annotate/multi", status_code=303)


@app.post("/annotate/multi/equals")
def annotate_multi_equals(response1_id: int = Form(...), response2_id: int = Form(...), user: User = Depends(get_current_user)):
    """Annotate a pair of responses (1 = 2)"""
    with SessionLocal() as db:
        response1 = db.query(ResponseMulti).filter(ResponseMulti.id == response1_id).first()
        response1.number_of_annotations += 1
        response2 = db.query(ResponseMulti).filter(ResponseMulti.id == response2_id).first()
        response2.number_of_annotations += 1
        annotation1 = PairwiseComparisonMulti(user_id=user.id, preferred_response_id=response1_id, other_response_id=response2_id)
        annotation2 = PairwiseComparisonMulti(user_id=user.id, preferred_response_id=response2_id, other_response_id=response1_id)
        user = db.merge(user)
        user.score += 1
        db.add(annotation1)
        db.add(annotation2)
        db.commit()
    return RedirectResponse(url="/annotate/multi", status_code=303)
