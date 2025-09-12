from sqlalchemy.orm import Session
from fastapi import Depends, Header, HTTPException, status
from app.db.session import get_db

def db_session(db: Session = Depends(get_db)):
    return db

def get_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Id header")
    return x_user_id