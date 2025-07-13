import secrets
from sqlalchemy.orm import Session
from sqlalchemy import select

def generate_unique_token(db: Session, model, field_name: str = "token", length: int = 32, max_attempts: int = 10) -> str:
    """
    Erzeugt ein eindeutiges Token, das in 'model' in der Spalte 'field_name' noch nicht existiert.
    """
    for _ in range(max_attempts):
        token = secrets.token_urlsafe(length)
        column = getattr(model, field_name)
        exists = db.execute(select(model).where(column == token)).scalar()
        if not exists:
            return token
    raise Exception(f"Failed to generate unique token after {max_attempts} attempts.")
