import pyotp

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional

from app import auth
from app.database import SessionLocal
from app.models import User
from app.schemas import UserOut, UserCreate, UserUpdate, ChangePasswordRequest
from app.api.deps import get_current_user


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pw = pwd_context.hash(user.password)
    totp_seed = pyotp.random_base32()
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        totp_secret=totp_seed,
        is_active=user.is_active,
        is_admin=user.is_admin,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Inactive user")
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()

    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()

    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def verify_credentials(user: Optional[User], password: str, totp: str) -> bool:
    if not user:
        return False

    if not auth.verify_password(password, user.hashed_password):
        return False

    check_totp = pyotp.TOTP(user.totp_secret)
    if not check_totp.verify(totp):
        return False

    return True


@router.post("/creds/passwd")
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.id == current_user.id
    ).first()
    if not verify_credentials(user, request.old_password, request.totp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.hashed_password= pwd_context.hash(request.new_password)
    db.commit()

    return {"detail": "Password changed successfully"}
