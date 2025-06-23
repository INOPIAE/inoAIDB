import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, AuthInvite, ModelChoice
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

    ensure_default_invite_exists(test_db)

    invites = test_db.query(AuthInvite).all()
    assert len(invites) == 1

    model_choices = test_db.query(ModelChoice).all()
    assert len(model_choices) == 4
