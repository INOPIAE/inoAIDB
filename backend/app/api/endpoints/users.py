import pyotp
from datetime import datetime, UTC, timezone
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional

from app import auth
from app.database import SessionLocal
from app.models import PaymentToken, User
from app.schemas import PaymentTokenCreate, PaymentTokenCreateOut, PaymentTokenOut, PaymentUsage, UserOut, UserCreate, UserUpdate, ChangePasswordRequest, RegisterRequest, RegisterResponse, UserResponse
from app.api.deps import get_current_user
from app.auth import generate_totp_secret, validate_invite, get_totp_uri
from app.utils.token import generate_unique_token


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/payments", response_model=list[PaymentTokenOut])
def list_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this function")
    # return db.query(PaymentToken).filter(PaymentToken.used_at.is_(None)).all()
    tokens = db.query(PaymentToken).filter(PaymentToken.used_at.is_(None)).all()
    return [PaymentTokenOut.model_validate(t) for t in tokens]

@router.post("/payments", response_model=PaymentTokenCreateOut)
def create_payment(payment: PaymentTokenCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this function")
    
    token = generate_unique_token(db, PaymentToken, field_name="token")
    db_token = PaymentToken(token=token, duration=payment.duration)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

@router.put("/payments")
def update_payment(payment: PaymentUsage, db: Session = Depends(get_db)):

    db_token = db.query(PaymentToken).filter(PaymentToken.token == payment.token).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Payment token not found")

    if db_token.used_at is not None:
        raise HTTPException(status_code=400, detail="Payment token already used")
    
    user =db.query(User).filter(User.email == payment.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found or invalid OTP code")
    
    if not auth.verify_totp(payment.otp, user.totp_secret):
        raise HTTPException(status_code=401, detail="User not found or invalid OTP code")

    db_token.used_at = datetime.now(timezone.utc)
    db_token.user_id = user.id
    db.commit()
    db.refresh(db_token)

    user.expire = user.expire + relativedelta(months=db_token.duration)
    db.commit()
    db.refresh(user)

    return {"success": True, "new_expiry": user.expire}


@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
        expire = calculate_expire(user.expire) if user.expire else None,
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

    for key, value in updates.model_dump(exclude_unset=True).items():
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

def calculate_expire(duration: int) -> datetime | None:
    if duration == 0:
        return None
    return datetime.now(UTC) + relativedelta(months=duration)

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if not request.accept_terms:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing accepted terms")
    # Validate invite code using the validate_invite function
    invite = validate_invite(db, request.invite)
    if not invite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired invite code")

    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")

    hashed_password = pwd_context.hash(request.password)

    # Generate TOTP seed
    totp_seed = generate_totp_secret()
    
    is_admin = False
    if request.invite == "SpecialInvite":
        is_admin = True

    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        totp_secret=totp_seed,
        is_admin=is_admin,
        expire= calculate_expire(invite.duration_month)
    )
    db.add(new_user)

    # Update invite usage
    invite.use_count += 1
    db.commit()
    db.refresh(new_user)

    # Generate TOTP URI
    #totp_uri = pyotp.totp.TOTP(totp_seed).provisioning_uri(name=request.username, issuer_name=cfg.authprovider)
    totp_uri =get_totp_uri(request.email, totp_seed, issuer="inoAIDB")

    return RegisterResponse(
        user=UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
        ),
        totp_uri=totp_uri
    )

