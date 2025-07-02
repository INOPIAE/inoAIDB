from app.models import Application, AuthInvite, Manufacturer, User

def new_user(authenticated_client):
    response = authenticated_client.post("api/users/", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "pass123password"
    })
    return response


def test_create_user(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = new_user(authenticated_client)
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"


def test_create_user_double(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = new_user(authenticated_client)
    response = new_user(authenticated_client)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User already exists"


def test_get_user_id(client):
    response = client.get(f"api/users/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_user_id_admin(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.get(f"api/users/1")
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"

    response = new_user(authenticated_client)
    user_id = response.json()["id"]

    response = authenticated_client.get(f"api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"

def test_get_user_id_user(authenticated_client_for_email):
    email="user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.get(f"api/users/2")
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_get_user_id_user_wrong_id(authenticated_client_for_email):
    email="user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.get(f"api/users/1")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this user"


def test_get_users_id_wrong(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.get("api/users/100")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_get_user(client):
    response = client.get("api/users/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_user_admin(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.get("api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    assert any(m["email"] == "admin@example.com" for m in data)
    emails = [user["email"] for user in data]
    assert "testuser@example.com" not in emails

    response = new_user(authenticated_client)
    response = authenticated_client.get("api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert any(m["email"] == "testuser@example.com" for m in data)

def test_get_user_user(authenticated_client_for_email):
    email="user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.get("api/users/")
    assert response.status_code == 403
    data = response.json()


def test_update_user(client,authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = new_user(authenticated_client)
    user_id = response.json()["id"]
    response = client.put(f"api/users/{user_id}", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_user_admin(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = new_user(authenticated_client)
    user_id = response.json()["id"]
    response = authenticated_client.put(f"api/users/{user_id}", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateuser"
    assert data["email"] == "update@example.com"

def test_update_user_user(authenticated_client_for_email):
    email="user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.put(f"api/users/2", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateuser"
    assert data["email"] == "update@example.com"

def test_update_user_user_not_own(authenticated_client_for_email):
    email="user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.put(f"api/users/3", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this user"
    

def test_update_user_wrong_id(client):
    response = client.put(f"api/users/100", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_user_wrong_id_admin(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.put(f"api/users/100", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

def test_update_user_wrong_id_user(authenticated_client_for_email):
    email="user@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.put(f"api/users/100", json={
        "username": "updateuser",
        "email": "update@example.com",
        "password": "updatepassword12"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this user"

def test_change_password(authenticated_client_for_email,valid_otp_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.post("/api/users/creds/passwd", json={
        "old_password": "passwordpassword",
        "new_password": "newpassword12345",
        "totp": valid_otp_for_email(email)
    })
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Password changed successfully"

def test_change_password_wrong_pw(authenticated_client_for_email,valid_otp_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.post("/api/users/creds/passwd", json={
        "old_password": "oldpassword12345",
        "new_password": "newpassword12345",
        "totp": valid_otp_for_email(email)
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_change_password_wrong_otp(authenticated_client_for_email):
    email="admin@example.com"
    authenticated_client = authenticated_client_for_email(email)
    response = authenticated_client.post("/api/users/creds/passwd", json={
        "old_password": "passwordpassword",
        "new_password": "newpassword12345",
        "totp": "123456"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_register(client):
    payload = {
        "username": "demo",
        "email": "test3@example.com",
        "password": "testpassword1234",
        "invite": "invite1",
        "accept_terms": True,
    }

    response = client.post("/api/users/register", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["user"]["username"] == "demo"
    assert data["user"]["email"] == "test3@example.com"
    assert data["totp_uri"].startswith("otpauth://totp/")

def test_register_existing_entries(client):
    payload = {
        "username": "demo",
        "email": "admin@example.com",
        "password": "testpassword1234",
        "invite": "invite1",
        "accept_terms": True,
    }

    response = client.post("/api/users/register", json=payload)
    data = response.json()
    assert response.status_code == 400
    assert data["detail"] == "Email already taken"

    payload = {
        "username": "user",
        "email": "test3@example.com",
        "password": "testpassword1234",
        "invite": "invite1",
        "accept_terms": True,
    }

    response = client.post("/api/users/register", json=payload)
    data = response.json()
    assert response.status_code == 400
    assert data["detail"] == "Username already taken"


def test_register_invalid_invite(client):
    payload = {
       "username": "demo",
        "email": "test3@example.com",
        "password": "testpassword1234",
        "invite": "invalid",
        "accept_terms": True,
    }
    
    response = client.post("/api/users/register", json=payload)
    data = response.json()
    assert response.status_code == 400
    assert data["detail"] == "Invalid or expired invite code"

    payload = {
        "username": "demo",
        "email": "test3@example.com",
        "password": "testpassword1234",
        "invite": "invite2",
        "accept_terms": True,
    }

    response = client.post("/api/users/register", json=payload)
    data = response.json()
    assert response.status_code == 400
    assert data["detail"] == "Invalid or expired invite code"

def test_register_SpecialInvite(client, db):
    payload = {
        "username": "demo1",
        "email": "test4@example.com",
        "password": "testpassword1234",
        "invite": "SpecialInvite",
        "accept_terms": True,
    }

    response = client.post("/api/users/register", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["user"]["username"] == "demo1"
    assert data["user"]["email"] == "test4@example.com"
    assert data["totp_uri"].startswith("otpauth://totp/")

    user = db.query(User).filter(User.email == "test4@example.com").first()
    assert user is not None
    assert user.is_admin is True

def test_register_missing_Accept(client):
    payload = {
        "username": "demo",
        "email": "test3@example.com",
        "password": "testpassword1234",
        "invite": "invite1",
        "accept_terms": False,
    }

    response = client.post("/api/users/register", json=payload)
    data = response.json()
    print(data) 
    assert response.status_code == 400
    assert data["detail"] == "Missing accepted terms"
