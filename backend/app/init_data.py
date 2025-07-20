from sqlalchemy.orm import Session
from app.models import AuthInvite, ModelChoice, Risk, ApplicationArea

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
        "irrelevant": 2,
        "minimal": 3,
        "low": 4,
        "medium": 5,
        "high": 6,
        "deferred": 7
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

    required_areas = {
        "Text Generation",
        "Translation and Transcription",
        "Image Generation and Manipulation",
        "Design, Marketing, Content Creation, SEO",
        "Audio and Music Processing, Transcription",
        "Audio and Music Generation",
        "Videos",
        "Programming and Code Generation",
        "Learning and Teaching",
        "Mathematics",
        "Productivity applications",
    }

    existing_areas = {
        a.area: a for a in db.query(ApplicationArea).filter(ApplicationArea.area.in_(required_areas)).all()
    }

    for area in required_areas:
        if area not in existing_areas:
            db.add(ApplicationArea(area=area))
            db.commit()
            print(f"Area created: {area} ")
        else:
            print(f"Area already exists: {area} ")
