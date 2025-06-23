def new_languagemodel(authenticated_client):
    response = authenticated_client.post("api/languagemodels/", json={
        "name": "Test Model",
        "description": "This is a test.",
        "is_active": True
    })

    return response


def test_create_languagemodel(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_languagemodel(authenticated_client)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Model"
    assert data["description"] == "This is a test."
    assert data["is_active"] is True

def test_get_languagemodel(client,authenticated_client_for_email):
    response = client.get("api/languagemodels/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert isinstance(data, list)
    assert any(m["name"] == "unknown" for m in data)
    names = [m["name"] for m in data]
    assert "Test Model" not in names
    assert names == sorted(names)

    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_languagemodel(authenticated_client)

    response = client.get("api/languagemodels/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert isinstance(data, list)
    assert any(m["name"] == "Test Model" for m in data)


def test_get_languagemodels_id(client, authenticated_client_for_email):
    response = client.get(f"api/languagemodels/1")
    data = response.json()
    print(data)
    assert data["name"] == "unknown"

    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_languagemodel(authenticated_client)
    languagemodel_id = response.json()["id"]
    response = client.get(f"api/languagemodels/{languagemodel_id}")
    data = response.json()
    assert data["name"] == "Test Model"
    assert data["description"] == "This is a test."


def test_get_languagemodels_id_wrong(client):
    response = client.get("api/languagemodels/100")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Language model not found"


def test_update_languagemodel(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_languagemodel(authenticated_client)
    languagemodel_id = response.json()["id"]
    response = authenticated_client.put(f"api/languagemodels/{languagemodel_id}", json={
        "name": "Updated Model",
        "description": "Updated description.",
        "is_active": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Model"
    assert data["is_active"] is False


def test_update_languagemodel_wrong_id(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.put(f"api/languagemodels/100", json={
        "name": "Updated Model",
        "description": "Updated description.",
        "is_active": False
    })
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Language model not found"


def test_create_manufacturer_double(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_languagemodel(authenticated_client)
    response = new_languagemodel(authenticated_client)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Language model already exists"

def test_update_languagemodel_double(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.put(f"api/languagemodels/2", json={
        "name": "unknown",
        "description": "Updated description.",
        "is_active": False
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Language model already exists"
