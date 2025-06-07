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
