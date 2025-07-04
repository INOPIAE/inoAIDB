from sqlalchemy.orm import Session
from app.models import AuthInvite, ModelChoice, Risk

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
    
    required_risks = {
        "unknown": 1,
        "minimal": 2,
        "low": 3,
        "medium": 4,
        "high": 5,
        "deferred": 6
    }

    existing_risks = {
        r.name: r for r in db.query(Risk).filter(Risk.name.in_(required_risks.keys())).all()
    }

    for name, sort in required_risks.items():
        existing = existing_risks.get(name)
        if existing is None:
            rk = Risk(name=name, sort=sort)
            db.add(rk)
            db.commit()
            print(f"Risk created: {name} (sort={sort})")
        else:
            if existing.sort != sort:
                existing.sort = sort
                db.commit()
                print(f"Risk updated: {name} (sort={sort})")
            else:
                print(f"Risk already exists: {name} (sort={sort})")

