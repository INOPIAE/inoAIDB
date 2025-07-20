import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, AuthInvite, ModelChoice, Risk, ApplicationArea
from app.init_data import ensure_default_invite_exists

# Testdatenbank (in-memory SQLite)
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_ensure_default_invite_creates_records(test_db):
    ensure_default_invite_exists(test_db)

    invite = test_db.query(AuthInvite).first()
    assert invite is not None
    assert invite.code == "SpecialInvite"
    assert invite.use_max == 1

    model_choices = test_db.query(ModelChoice).all()
    assert len(model_choices) == 4
    names = [mc.name for mc in model_choices]
    assert "unknown" in names
    assert "web" in names
    assert "company" in names
    assert "web_company" in names

    risk = test_db.query(Risk).all()
    assert len(risk) == 7
    names = [rk.name for rk in risk]
    assert "unknown" in names
    assert "minimal" in names
    assert "low" in names
    assert "medium" in names
    assert "high" in names
    assert "deferred" in names

    area = test_db.query(ApplicationArea).all()
    assert len(area) == 11
    areas = [ak.area for ak in area]
    assert "Text Generation" in areas
    assert "Translation and Transcription" in areas
    assert "Image Generation and Manipulation" in areas
    assert "Design, Marketing, Content Creation, SEO" in areas
    assert "Audio and Music Processing, Transcription" in areas
    assert "Audio and Music Generation" in areas
    assert "Videos" in areas
    assert "Programming and Code Generation" in areas
    assert "Learning and Teaching" in areas
    assert "Mathematics" in areas
    assert "Productivity applications" in areas

    ensure_default_invite_exists(test_db)

    invites = test_db.query(AuthInvite).all()
    assert len(invites) == 1

    model_choices = test_db.query(ModelChoice).all()
    assert len(model_choices) == 4

    risk = test_db.query(Risk).all()
    assert len(risk) == 7

def test_ensure_default_invite_update_risks_sort(test_db):
    ensure_default_invite_exists(test_db)

    updates = {
        1: 30,
        2: 35,
    }

    for risk_id, new_sort in updates.items():
        entry = test_db.query(Risk).filter_by(id=risk_id).first()
        if entry:
            entry.sort = new_sort
            print(f"Updated Risk id={risk_id} with sort={new_sort}")
    test_db.commit()


    ensure_default_invite_exists(test_db)

    risk = test_db.query(Risk).all()
    assert len(risk) == 7

    risk1 = test_db.query(Risk).filter_by(id=1).first()
    risk2 = test_db.query(Risk).filter_by(id=2).first()

    
    assert risk1.name == 'unknown'
    assert risk1.sort == 1

    assert risk2.name == 'irrelevant'
    assert risk2.sort == 2
    