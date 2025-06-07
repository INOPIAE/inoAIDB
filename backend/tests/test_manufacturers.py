def new_manufacturer(authenticated_client):
    response = authenticated_client.post("api/manufacturers/", json={
        "name": "Test Manufacturer",
        "description": "This is a test.",
        "is_active": True
    })

    return response


def test_create_manufacturer(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_manufacturer(authenticated_client)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Manufacturer"
    assert data["description"] == "This is a test."
    assert data["is_active"] is True


def test_get_manufacturers(client,authenticated_client_for_email):
    response = client.get("api/manufacturers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert isinstance(data, list)
    assert any(m["name"] == "Microsoft" for m in data)
    names = [m["name"] for m in data]
    assert "Test Manufacturer" not in names
    assert names == sorted(names)

    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_manufacturer(authenticated_client)

    response = client.get("api/manufacturers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert isinstance(data, list)
    assert any(m["name"] == "Test Manufacturer" for m in data)


def test_get_manufacturers_id(client, authenticated_client_for_email):
    response = client.get(f"api/manufacturers/1")
    data = response.json()
    assert data["name"] == "Microsoft"

    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_manufacturer(authenticated_client)
    manufacturer_id = response.json()["id"]
    response = client.get(f"api/manufacturers/{manufacturer_id}")
    data = response.json()
    assert data["name"] == "Test Manufacturer"
    assert data["description"] == "This is a test."


def test_get_manufacturers_id_wrong(client):
    response = client.get("api/manufacturers/100")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Manufacturer not found"


def test_update_manufacturer(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_manufacturer(authenticated_client)
    manufacturer_id = response.json()["id"]
    response = authenticated_client.put(f"api/manufacturers/{manufacturer_id}", json={
        "name": "Updated Manufacturer",
        "description": "Updated description.",
        "is_active": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Manufacturer"
    assert data["is_active"] is False


def test_update_manufacturer_wrong_id(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.put(f"api/manufacturers/100", json={
        "name": "Updated Manufacturer",
        "description": "Updated description.",
        "is_active": False
    })
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Manufacturer not found"


def test_create_manufacturer_double(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_manufacturer(authenticated_client)
    response = new_manufacturer(authenticated_client)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Manufacturer already exists"
