def new_modelchoice(authenticated_client):
    response = authenticated_client.post("api/modelchoices/", json={
        "name": "Test Model",
    })

    return response


def test_create_modelchoice(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_modelchoice(authenticated_client)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Model"

def test_get_modelchoice(client,authenticated_client_for_email):
    response = client.get("api/modelchoices/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert isinstance(data, list)
    assert any(m["name"] == "unknown" for m in data)
    names = [m["name"] for m in data]
    assert "Test Model" not in names
    assert names == sorted(names)

    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_modelchoice(authenticated_client)

    response = client.get("api/modelchoices/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert isinstance(data, list)
    assert any(m["name"] == "Test Model" for m in data)


def test_get_modelchoices_id(client, authenticated_client_for_email):
    response = client.get(f"api/modelchoices/1")
    data = response.json()
    assert data["name"] == "unknown"

    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_modelchoice(authenticated_client)
    modelchoice_id = response.json()["id"]
    response = client.get(f"api/modelchoices/{modelchoice_id}")
    data = response.json()
    assert data["name"] == "Test Model"


def test_get_modelchoices_id_wrong(client):
    response = client.get("api/modelchoices/100")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Model choice not found"


def test_update_languagemodel(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_modelchoice(authenticated_client)
    modelchoice_id = response.json()["id"]
    response = authenticated_client.put(f"api/modelchoices/{modelchoice_id}", json={
        "name": "Updated Model",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Model"

def test_update_languagemodel_wrong_id(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.put(f"api/modelchoices/100", json={
        "name": "Updated Model",
    })
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Model choice not found"


def test_create_manufacturer_double(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_modelchoice(authenticated_client)
    response = new_modelchoice(authenticated_client)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Model choice already exists"

def test_update_modelchoices_double(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.put(f"api/modelchoices/2", json={
        "name": "unknown",
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Model choice already exists"
