from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi import Form
import argparse
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
    return login(username, db)

@app.post("/logout")
def logout_user():
    return logout()

@app.get("/annotate/simple", response_class=HTMLResponse)
def annotate_simple(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("annotate_simple.html", {"request": request, "user": user})

@app.get("/annotate/multi", response_class=HTMLResponse)
def annotate_multi(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("annotate_multi.html", {"request": request, "user": user})
