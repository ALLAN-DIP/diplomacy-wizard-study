from fastapi import Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from .database import get_db
from .models import User

def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == session_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session, if you are a new user, please /register.")
    return user

def register(username: str, db: Session = Depends(get_db)):
    user = User(username=username)
    # check if user already exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    db.add(user)
    db.commit()
    db.refresh(user)

def login(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    response = JSONResponse(content={"message": "Login successful. Welcome! " + username + "! Go to / to start annotating."})
    response.set_cookie(key="session_id", value=str(user.id), httponly=True, secure=True, samesite="lax")
    return response

def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_id")
    return response
