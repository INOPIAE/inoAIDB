from sqlalchemy.orm import Session
from app.models import AuthInvite, ModelChoice

def ensure_default_invite_exists(db: Session):
    existing = db.query(AuthInvite).first()
    if not existing:
        invite = AuthInvite(code="SpecialInvite", use_max=1)
        db.add(invite)
        db.commit()
        print(f"Invite created: {invite.code}")
    else:
        print(f"Invite existing {existing.code}")
    existing = db.query(ModelChoice).first()
    if not existing:
        mc = ModelChoice(name="unknown")
        db.add(mc)
        db.commit()
        print(f"Model choice created: {mc.name}")
        mc = ModelChoice(name="web")
        db.add(mc)
        db.commit()
        print(f"Model choice created: {mc.name}")
        mc = ModelChoice(name="company")
        db.add(mc)
        db.commit()
        print(f"Model choice created: {mc.name}")
        mc = ModelChoice(name="web_company")
        db.add(mc)
        db.commit()
        print(f"Model choice created: {mc.name}")
    else:
        print(f"Model choice existing {existing.name}")