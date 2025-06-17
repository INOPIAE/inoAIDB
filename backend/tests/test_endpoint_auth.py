from app import models


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
    data = response.json()
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_login_unknown_email(client):
    response = client.post("api/auth/login", json={
        "email": "nobody@example.com",
        "password": "irrelevantpassword",
        "otp": "123456"
    })
    data = response.json()
    print(data)
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


def test_get_invites(authenticated_client_for_email, db):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)

    # Set up 2 Invites: einer gültig, einer aufgebraucht
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


def test_get_invite_uses_left(authenticated_client_for_email, db):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)

    invite = create_invite_in_db(db, code="testcode123", use_max=10, use_count=3)

    response = client.get("/api/auth/invite/testcode123")
    assert response.status_code == 200
    data = response.json()
    assert data["use_left"] == 7


def test_get_invite_uses_left_invalid_code(authenticated_client_for_email):
    email = "admin@example.com"
    client = authenticated_client_for_email(email)

    response = client.get("/api/auth/invite/nonexistentcode")
    assert response.status_code == 200
    data = response.json()
    assert data["use_left"] == 0
