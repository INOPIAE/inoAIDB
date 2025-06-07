from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import schemas, models, auth
from app.database import SessionLocal
from app.api import deps

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=schemas.UserOut)
def login_user(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not auth.verify_totp(credentials.otp, user.totp_secret):
        raise HTTPException(status_code=401, detail="Invalid OTP code")
    return user  # OTP wird im nächsten Schritt geprüft


def login_userO(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return user


@router.post("/verify", response_model=schemas.Token)
def verify_otp(otp_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == otp_data.email).first()
    if not user or not user.totp_secret:
        raise HTTPException(status_code=400, detail="OTP not set up")
    
    if not auth.verify_totp(otp_data.otp_code, user.totp_secret):
        raise HTTPException(status_code=401, detail="Invalid OTP code")

    token_data = {"user_id": user.id, "email": user.email}
    access_token = auth.create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
