from fastapi import FastAPI, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import schemas, crud
from .events.publisher import publish_user_created
from .auth import create_access_token, get_current_user

from fastapi.security import OAuth2PasswordRequestForm 

app = FastAPI(
    title="User Service (FastAPI + JWT)",
    description="Mikroservis za registraciju, login i autorizaciju korisnika",
    version="0.1.0")
Base.metadata.create_all(bind=engine)
@app.get("/healthz", tags=["Meta"], summary="Health check")
def healthz():
    return {"status": "ok"}

def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        publish_user_created({"id": user.id, "email": user.email})
    except Exception as e:
        print(f"[warn] RabbitMQ publish failed: {e}")

    return user


@app.post("/login", tags=["Auth"], summary="User login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.email)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):

        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/{user_id}", response_model=schemas.UserRead, tags=["Users"], summary="Get user by id (owner only)")
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) 
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/me", response_model=schemas.UserRead, tags=["Auth"], summary="Get current logged-in user")
def read_me(current_user = Depends(get_current_user)):
    return current_user
