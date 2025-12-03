from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    """
    Checks if the system is initialized (has at least one user).
    """
    user_count = db.query(User).count()
    return {
        "initialized": user_count > 0,
        "version": "1.0.0"
    }
