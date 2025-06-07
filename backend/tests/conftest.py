import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import auth, models
from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models import Application, Manufacturer, User


@pytest.fixture(scope="session")
def engine():
    settings = get_settings("test")  # <-- explizit Testkonfiguration verwenden
    engine = create_engine(settings.database_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(engine, tables):
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
    db.query(User).delete()
    db.query(Application).delete()
    db.query(Manufacturer).delete()
    db.commit()

    db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE manufacturers_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE applications_id_seq RESTART WITH 1"))


    user1 = User(username="admin", email="admin@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_admin=True, totp_secret=auth.generate_totp_secret())
    user2 = User(username="user", email="user@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_admin=False, totp_secret=auth.generate_totp_secret())
    user3 = User(username="missingotp", email="missingotp@example.com", hashed_password=auth.pwd_context.hash("passwordpassword"), is_admin=False)

    man1 = Manufacturer(name="Microsoft", description="Tech", is_active=True)
    man2 = Manufacturer(name="Apple", description="Tech", is_active=True)

    app1 = Application(name="Office", description="software", manufacturer_id = 1, is_active=True)
    app2 = Application(name="Visual Studio Code", description="software", manufacturer_id = 1, is_active=True)
    app3 = Application(name="Alexa", description="software", manufacturer_id = 2, is_active=True)

    db.add_all([user1, user2, user3, man1, man2, app1, app2, app3])
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
                hashed_password=auth.pwd_context.hash("passwordpassword"),
                totp_secret=totp_secret,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            totp_secret = user.totp_secret

        otp_code = auth.get_current_totp(user.totp_secret)

        response = client.post("/api/auth/login", json={
            "email": email,
            "password": password,
            "otp": otp_code
        })

        assert response.status_code == 200, f"Login failed: {response.text}"

        response = client.post("api/auth/verify", json={
            "email": email,
            "otp_code": otp_code
        })

        assert response.status_code == 200, f"Login failed: {response.text}"

        token = response.json()["access_token"]
        authed_client = TestClient(app)
        authed_client.headers.update({"Authorization": f"Bearer {token}"})
        return authed_client

    return _login
