def new_application(authenticated_client):
    response = authenticated_client.post("api/applications/", json={
        "name": "Test Application",
        "description": "This is a test.",
        "manufacturer_id": 1,
        "is_active": True
    })

    return response

def test_create_application(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_application(authenticated_client)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Application"
    assert data["description"] == "This is a test."
    assert data["is_active"] is True


def test_create_application_duplicate(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_application(authenticated_client)
    response = new_application(authenticated_client)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Application already exists"

def test_create_application_wrong_maufacturer(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.post("api/applications/", json={
        "name": "Test Application1",
        "description": "This is a test.",
        "manufacturer_id": 999999,
        "is_active": True
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Manufacturer not found"

def test_get_applications(client):
    response = client.get("/api/applications/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(response.json(), list)

    assert len(data) == 3
    assert isinstance(data, list)
    assert any(a["name"] == "Office" for a in data)
    names = [a["name"] for a in data]
    assert "Test Application" not in names
    assert names == sorted(names)


def test_get_application_by_id(client):
    response = client.get(f"/api/applications/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Office"


def test_get_application_not_found(client):
    response = client.get("/api/applications/999999")
    assert response.status_code == 404


def test_update_application(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_application(authenticated_client)
    application_id = response.json()["id"]
    response = authenticated_client.put(f"api/applications/{application_id}", json={
        "name": "Updated Application",
        "description": "Updated description",
        "manufacturer_id": 2,
        "is_active": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Application"
    assert data["description"] == "Updated description"
    assert data["is_active"] is False


def test_update_application_not_found(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")

    response = authenticated_client.put("/api/applications/999999", json= {
        "name": "Does Not Exist",
        "description": "Should fail",
        "manufacturer_id": 1,
        "is_active": True
    })
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Application not found"

def test_update_application_wrong_maufacturer(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_application(authenticated_client)
    application_id = response.json()["id"]
    response = authenticated_client.put(f"api/applications/{application_id}", json={
        "name": "Updated Application",
        "description": "Updated description",
        "manufacturer_id": 9999999,
        "is_active": False
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Manufacturer not found"


def test_get_applications_by_manufacturer(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")

    response = authenticated_client.get("api/applications/by-manufacturer/1")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all(app["manufacturer_id"] == 1 for app in data)

    response = new_application(authenticated_client)
    response = authenticated_client.get("api/applications/by-manufacturer/1")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert all(app["manufacturer_id"] == 1 for app in data)

def test_get_applications_by_manufacturer_wrong(client):
    response = client.get("api/applications/by-manufacturer/9999999")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Manufacturer not found"


def test_get_applications_with_manufacturer(client):
    response = client.get("/api/applications/with-manufacturer")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    for app in data:
        assert app["is_active"] is True
        assert "manufacturer_id" in app
        assert "manufacturer_name" in app
