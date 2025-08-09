from fastapi import FastAPI, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import schemas, crud
from .events.publisher import publish_user_created
from .auth import create_access_token, get_current_user

app = FastAPI(title="user-service", version="0.1.0")

Base.metadata.create_all(bind=engine)

@app.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
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

@app.post("/login")
def login(email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or not crud.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/{user_id}", response_model=schemas.UserRead)
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