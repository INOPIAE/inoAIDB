from sqlalchemy.orm import Session
from app.models import AuthInvite

def ensure_default_invite_exists(db: Session):
    existing = db.query(AuthInvite).first()
    if not existing:
        invite = AuthInvite(code="SpecialInvite", use_max=1)
        db.add(invite)
        db.commit()
        print(f"Invite created: {invite.code}")
    else:
        print(f"Invite existing {existing.code}")