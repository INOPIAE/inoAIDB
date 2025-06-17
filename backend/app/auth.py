from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import pyotp
from sqlalchemy.orm import Session
from app.models import AuthInvite


from app.config import settings

# Passwort-Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT-Einstellungen
SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes

# Passwort-Hash erstellen/prüfen
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT-Token erstellen
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# JWT-Token prüfen und Nutzdaten extrahieren
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# TOTP-Secret generieren
def generate_totp_secret() -> str:
    return pyotp.random_base32()

# QR-Code URL für Google Authenticator
def get_totp_uri(user_email: str, secret: str, issuer: str = "inoAIDB") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name=issuer)

# OTP validieren
def verify_totp(token: str, secret: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

def get_current_totp(secret):
    return pyotp.TOTP(secret).now()

def validate_invite(db: Session, code: str) -> AuthInvite:
    invite = db.query(AuthInvite).filter(
        AuthInvite.code == code
    ).first()

    if not invite:
        return None

    if invite.use_count >= invite.use_max:
        return None

    return invite
