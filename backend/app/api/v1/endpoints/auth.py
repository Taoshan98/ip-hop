from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import User
from app.schemas import auth as schemas
from app.core import security
import re
from typing import Optional

router = APIRouter()

# Keep this for Swagger UI support, but make it optional
oauth2_scheme_header = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token(request: Request, token_header: Optional[str] = Depends(oauth2_scheme_header)):
    # 1. Try Cookie
    token = request.cookies.get("access_token")
    if token:
        return token
    # 2. Try Header
    if token_header:
        return token_header
    # 3. Fail
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Alias for other modules to use
oauth2_scheme = get_token

def validate_password(password: str) -> bool:
    """
    Validates password complexity:
    - At least 8 characters
    - At least 1 uppercase
    - At least 1 special char
    - At least 2 numbers
    """
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
    if len(re.findall(r"\d", password)) < 2: return False
    return True

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(subject=user.username)
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800, # 30 min
        samesite="lax",
        secure=False, # Set to True in production with HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/setup", response_model=schemas.User)
def setup_admin(setup_data: schemas.SetupRequest, db: Session = Depends(get_db)):
    """
    Creates the first admin user. Fails if any user already exists.
    """
    if db.query(User).count() > 0:
        raise HTTPException(status_code=400, detail="Setup already completed.")

    if not validate_password(setup_data.password):
        raise HTTPException(status_code=400, detail="Password does not meet complexity requirements.")

    hashed_password = security.get_password_hash(setup_data.password)
    new_user = User(
        username=setup_data.username,
        password_hash=hashed_password,
        role="admin"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.refresh(new_user)
    return new_user

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.get("/me", response_model=schemas.User)
def read_users_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Decode token to get username
    # This logic should ideally be in a dependency "get_current_user" but for now:
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except security.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
