from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets
from datetime import datetime, timedelta, UTC, timezone
from fastapi.security import OAuth2PasswordRequestForm
from app import schemas, models, auth
from app.database import SessionLocal
from app.api import deps
import uuid
from app.models import AuthInvite, User, PasswordResetToken
from app.api.deps import get_current_user
from app.utils.email import send_email
from app.config import settings

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_model=schemas.UserOut)
def login_user(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not auth.verify_totp(credentials.otp, user.totp_secret):
        raise HTTPException(status_code=401, detail="Invalid OTP code")
    if user.expire is not None and user.expire <= datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="User account expired")
    return user  # OTP wird im nächsten Schritt geprüft


def login_userO(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return user


@router.post("/verify", response_model=schemas.Token)
def verify_otp(otp_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == otp_data.email).first()
    if not user or not user.totp_secret:
        raise HTTPException(status_code=400, detail="OTP not set up")
    
    if not auth.verify_totp(otp_data.otp_code, user.totp_secret):
        raise HTTPException(status_code=401, detail="Invalid OTP code")

    token_data = {"user_id": user.id, "email": user.email}
    access_token = auth.create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/invite", response_model=schemas.InviteListResponse)
def get_invites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")

    invites = db.query(
        AuthInvite.code,
        (AuthInvite.use_max - AuthInvite.use_count).label("use_left")
    ).filter(
        AuthInvite.use_max - AuthInvite.use_count > 0
    ).all()

    return {"invites": invites}


@router.post("/invite", response_model=schemas.AuthInviteCreateResponse)
def create_invite(
    invite: schemas.AuthInviteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")

    code = invite.code or str(uuid.uuid4())

    db_invite = AuthInvite(
        code=code,
        use_max=invite.use_max,
        duration_month=invite.duration_month or 0,
    )

    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    return schemas.AuthInviteCreateResponse(
        code=db_invite.code,
        use_max=db_invite.use_max
    )


@router.get("/invite/{code}", response_model=schemas.AuthInviteStatusResponse)
def get_invite_uses_left(
    code: str,
    auth: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not auth.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")

    db_invite = db.query(AuthInvite).filter(
        AuthInvite.code == code
    ).first()

    use_left = db_invite.use_max - db_invite.use_count if db_invite is not None else 0

    return schemas.AuthInviteStatusResponse(
        use_left=use_left
    )

@router.post("/forgot-password")
def forgot_password(email: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.email).first()
    if not user:
        return {"message": "If the email exists, a reset link has been sent."}

    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(hours=1)

    db_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
    db.add(db_token)
    db.commit()


    if settings.nginx_enabled:
        reset_url = f"https://{settings.public_url}/reset-password?token={token}"
    else:
        reset_url = f"http://{settings.public_url}:{settings.port_frontend}/reset-password?token={token}"

    linebreak = "\n"
    body = (
        "Hi," + linebreak +
        "You requested to reset your password. Click the link below to reset it:" + linebreak + linebreak +
        reset_url + linebreak + linebreak +
        "Your Support Team"
    )

    send_email(to=email.email, subject="Password Reset for inoAIDB", body=body)

    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    token_entry = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == request.token, PasswordResetToken.used == False)
        .first()
    )

    if not token_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    expires_at = token_entry.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_entry.user_id).first()

    user.hashed_password = pwd_context.hash(request.new_password)
    token_entry.used = True

    db.commit()

    user1 = db.query(User).filter(User.id == token_entry.user_id).first()

    return {"message": "Password has been reset successfully."}
