import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic import command

from app import auth, models
from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models import Application, AuthInvite, Manufacturer, User, LanguageModel, ModelChoice, PasswordResetToken, ApplicationUser, Risk


@pytest.fixture(scope="session")
def engine():
    settings = get_settings("test")
    engine = create_engine(settings.database_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def alembic_config():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", get_settings("test").database_url)
    return alembic_cfg


# @pytest.fixture(scope="function")
# def run_migrations(engine, alembic_config):
#     command.downgrade(alembic_config, "base")
#     command.upgrade(alembic_config, "head")
#     yield

@pytest.fixture(scope="session", autouse=True)
def run_migrations(alembic_config):
    command.upgrade(alembic_config, "head")

@pytest.fixture(scope="function")
def db(engine, run_migrations):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def setup_test_data(db):
    db.query(AuthInvite).delete()
    db.query(PasswordResetToken).delete()
    db.query(ApplicationUser).delete()
    db.query(User).delete()


    db.query(Application).delete()
    db.query(LanguageModel).delete()
    db.query(ModelChoice).delete()
    db.query(Manufacturer).delete()
    db.commit()

    db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE manufacturers_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE language_models_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE model_choices_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE applications_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE password_reset_tokens_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE application_users_id_seq RESTART WITH 1"))

    user1 = User(username="admin", email="admin@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_admin=True, totp_secret=auth.generate_totp_secret())
    user2 = User(username="user", email="user@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_admin=False, totp_secret=auth.generate_totp_secret())
    user3 = User(username="missingotp", email="missingotp@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_admin=False)
    user4 = User(username="inactive", email="inactive@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_active=False, is_admin=False, totp_secret=auth.generate_totp_secret())

    man1 = Manufacturer(name="Microsoft", description="Tech", is_active=True)
    man2 = Manufacturer(name="Apple", description="Tech", is_active=True)

    lm1 = LanguageModel(name="unknown", description="", is_active=True)
    lm2 = LanguageModel(name="ChatGPT", description="", is_active=True)

    mc1 = ModelChoice(name="unknown")
    mc2 = ModelChoice(name="web")

    app1 = Application(name="Office", description="software", manufacturer_id=1, languagemodel_id = 1, modelchoice_id = 1, is_active=True)
    app2 = Application(name="Visual Studio Code", description="software", manufacturer_id=1, languagemodel_id = 1, modelchoice_id = 1,is_active=True)
    app3 = Application(name="Alexa", description="software", manufacturer_id=2, languagemodel_id = 1, modelchoice_id = 1, is_active=False)

    inv1 = AuthInvite(code = "SpecialInvite", use_count = 0, use_max = 1)
    inv2 = AuthInvite(code = "invite1", use_count = 1, use_max = 2, duration_month=6)
    inv3 = AuthInvite(code = "invite2", use_count = 1, use_max = 1)

    risks_to_create = [
        {"id": 1, "name": "unknown", "sort": 1},
        {"id": 2, "name": "minimal", "sort": 2},
    ]

    for data in risks_to_create:
        existing_risk = db.query(Risk).filter(Risk.id == data["id"]).first()
        if not existing_risk:
            risk = Risk(**data)
            db.add(risk)
            db.commit()
            print(f"Risk with id={data['id']} created.")


    au1 = ApplicationUser(user_id=1, application_id=1, selected=True, risk_id=1)
    au2 = ApplicationUser(user_id=2, application_id=2, selected=True, risk_id=1)


    db.add_all([user1, user2, user3, user4, man1, man2, lm1, lm2, mc1, mc2, app1, app2, app3, inv1, inv2, inv3, au1, au2])
    db.commit()
    yield
    db.close()


@pytest.fixture(scope="function")
def valid_otp_for_email(db):
    def _get_otp(email: str) -> str:
        user = db.query(models.User).filter_by(email=email).first()
        if not user or not user.totp_secret:
            raise ValueError(f"No user with email '{email}' and valid TOTP secret.")
        return auth.get_current_totp(user.totp_secret)
    return _get_otp


@pytest.fixture(scope="function")
def authenticated_client_for_email(db, client):
    def _login(email: str, password: str = "passwordpassword") -> TestClient:
        user = db.query(models.User).filter_by(email=email).first()
        if not user:
            totp_secret = auth.generate_totp_secret()
            user = models.User(
                email=email,
                hashed_password=auth.pwd_context.hash(password),
                totp_secret=totp_secret,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        otp_code = auth.get_current_totp(user.totp_secret)

        response = client.post("/api/auth/login", json={
            "email": email,
            "password": password,
            "otp": otp_code
        })
        assert response.status_code == 200, f"Login failed: {response.text}"

        response = client.post("/api/auth/verify", json={
            "email": email,
            "otp_code": otp_code
        })
        assert response.status_code == 200, f"Verify failed: {response.text}"

        token = response.json()["access_token"]
        authed_client = TestClient(app)
        authed_client.headers.update({"Authorization": f"Bearer {token}"})
        return authed_client

    return _login
