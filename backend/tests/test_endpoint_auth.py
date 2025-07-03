from unittest.mock import patch

from app import models
from app.models import PasswordResetToken, User
from datetime import datetime, timedelta, UTC
import secrets

def test_login_success(client, valid_otp_for_email):
    email = "admin@example.com"
    valid_otp = valid_otp_for_email(email)
    response = client.post("api/auth/login", json={
        "email": email,
        "password": "passwordpassword", 
        "otp": valid_otp
    })
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == email

def test_login_wrong_password(client):
    response = client.post("api/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpasspassword",
        "otp": "123456"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_login_unknown_email(client):
    response = client.post("api/auth/login", json={
        "email": "nobody@example.com",
        "password": "irrelevantpassword",
        "otp": "123456"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_login_success_wrong_otp(client, db):
    email = "admin@example.com"
    response = client.post("api/auth/login", json={
        "email": email,
        "password": "passwordpassword", 
        "otp": "123456"
    })
    data = response.json()
    assert response.status_code == 401
    assert data["detail"] == "Invalid OTP code"

def test_verify_otp_success(client, valid_otp_for_email):
    email = "admin@example.com"
    valid_otp = valid_otp_for_email(email)

    response = client.post("api/auth/verify", json={
        "email": email,
        "otp_code": valid_otp
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_verify_otp_invalid(client):
    response = client.post("api/auth/verify", json={
        "email": "admin@example.com",
        "otp_code": "123456"  # absichtlich ungültig
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid OTP code"

def test_verify_otp_user_without_secret(client):
    response = client.post("api/auth/verify", json={
        "email": "missingotp@example.com",
        "otp_code": "123456"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "OTP not set up"


def create_invite_in_db(db, code: str, use_max: int = 5, use_count: int = 0):
    invite = models.AuthInvite(code=code, use_max=use_max, use_count=use_count)
    db.add(invite)
    db.commit()
    return invite


def test_create_invite(authenticated_client_for_email, db):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)
    
    response = client.post("/api/auth/invite", json={"use_max": 5})
    
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["use_max"] == 5

    # Optional: prüfe, ob Invite auch in DB ist
    db_invite = db.query(models.AuthInvite).filter_by(code=data["code"]).first()
    assert db_invite is not None
    assert db_invite.use_max == 5
    assert db_invite.use_count == 0

def test_create_invite_no_admin(authenticated_client_for_email, client):
    email = "user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    
    response = authenticated_client.post("/api/auth/invite", json={"use_max": 5})
    
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized to access this data"

    response = client.post("/api/auth/invite", json={"use_max": 5})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_invites(authenticated_client_for_email, db):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)

    create_invite_in_db(db, code="invite-valid", use_max=3, use_count=1)
    create_invite_in_db(db, code="invite-used-up", use_max=2, use_count=2)

    response = client.get("/api/auth/invite")
    assert response.status_code == 200
    data = response.json()
    assert "invites" in data

    invites = data["invites"]
    codes = [invite["code"] for invite in invites]
    assert "invite-valid" in codes
    assert "invite-used-up" not in codes

def test_get_invites_no_admin(authenticated_client_for_email, client):
    email = "user@example.com"
    authenticated_client = authenticated_client_for_email(email)

    response = authenticated_client.get("/api/auth/invite")
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized to access this data"

    response = client.get("/api/auth/invite")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_invite_uses_left(authenticated_client_for_email, db):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)

    invite = create_invite_in_db(db, code="testcode123", use_max=10, use_count=3)

    response = client.get("/api/auth/invite/testcode123")
    assert response.status_code == 200
    data = response.json()
    assert data["use_left"] == 7

def test_get_invite_uses_left_no_admin(authenticated_client_for_email, client):
    email = "user@example.com"
    authenticated_client = authenticated_client_for_email(email)

    response = authenticated_client.get("/api/auth/invite/testcode123")
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized to access this data"

    response = client.get("/api/auth/invite/testcode123")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_invite_uses_left_invalid_code(authenticated_client_for_email):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)

    response = client.get("/api/auth/invite/nonexistentcode")
    assert response.status_code == 200
    data = response.json()
    assert data["use_left"] == 0

@patch("app.api.endpoints.auth.send_email")
def test_forgot_password(mock_send_email, client, db):
    token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == 2).first()
    assert token is None

    email = "user@example.com"
    response = client.post("/api/auth/forgot-password", json={"email": email})
    assert response.status_code == 200
    assert response.json()["message"].startswith("If the email exists")

    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert kwargs["to"] == "user@example.com"

    token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == 2).first()
    assert token is not None
    assert token.user_id == 2

@patch("app.api.endpoints.auth.send_email")
def test_forgot_password_wrong_email(mock_send_email, client, db):
    tokens = db.query(PasswordResetToken).all()
    assert len(tokens) == 0

    email = "test@example.com"
    response = client.post("/api/auth/forgot-password", json={"email": email})
    assert response.status_code == 200
    assert response.json()["message"].startswith("If the email exists")

    mock_send_email.assert_not_called()

    tokens = db.query(PasswordResetToken).all()
    assert len(tokens) == 0

def test_reset_password_success(client, db):
    email = "user@example.com"

    user = db.query(User).filter_by(email=email).first()
    oldpassword = user.hashed_password

    response = client.post("/api/auth/forgot-password", json={"email": email})
    assert response.status_code == 200

    token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
    assert token is not None
    assert token.used is False

    new_password = "MyNewSecurePassword123"
    response = client.post("/api/auth/reset-password", json={
        "token": token.token,
        "new_password": new_password
    })

    assert response.status_code == 200
    assert "successfully" in response.json()["message"]

    db.expire_all()
    updated_user = db.query(User).filter_by(email=email).first()
    assert updated_user.hashed_password != oldpassword

    token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
    assert token.used is True


def test_reset_password_invalid(client, db):
    email = "user@example.com"
    new_password = "MyNewSecurePassword123"
    response = client.post("/api/auth/reset-password", json={
        "token": "1234",
        "new_password": new_password
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"

    response = client.post("/api/auth/forgot-password", json={"email": email})
    assert response.status_code == 200

    user = db.query(User).filter_by(email=email).first()
    token = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).first()
    assert token is not None
    assert token.used is False


    response = client.post("/api/auth/reset-password", json={
        "token": token.token,
        "new_password": new_password
    })

    assert response.status_code == 200
    assert "successfully" in response.json()["message"]

    response = client.post("/api/auth/reset-password", json={
        "token": token.token,
        "new_password": new_password
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"


def test_reset_password_token_expired(client, db):
    new_password = "MyNewSecurePassword123"

    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(hours=-3)

    db_token = PasswordResetToken(user_id=2, token=token, expires_at=expires)
    db.add(db_token)
    db.commit()
    response = client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"

