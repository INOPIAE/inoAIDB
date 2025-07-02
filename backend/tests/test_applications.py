import io
import csv
from app.models import ApplicationUser

def new_application(authenticated_client):
    response = authenticated_client.post("api/applications/", json={
        "name": "Test Application",
        "description": "This is a test.",
        "manufacturer_id": 1,
        "languagemodel_id": 1,
        "modelchoice_id": 1,
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

def test_create_application_wrong_data(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.post("api/applications/", json={
        "name": "Test Application1",
        "description": "This is a test.",
        "manufacturer_id": 999999,
        "languagemodel_id": 1,
        "modelchoice_id": 1,
        "is_active": True
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Manufacturer not found"

    response = authenticated_client.post("api/applications/", json={
        "name": "Test Application1",
        "description": "This is a test.",
        "manufacturer_id": 1,
        "languagemodel_id": 999999,
        "modelchoice_id": 1,
        "is_active": True
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Language model not found"

    response = authenticated_client.post("api/applications/", json={
        "name": "Test Application1",
        "description": "This is a test.",
        "manufacturer_id": 1,
        "languagemodel_id": 1,
        "modelchoice_id": 99999,
        "is_active": True
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Model choice not found"

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
        "languagemodel_id": 2,
        "modelchoice_id": 2,
        "is_active": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Application"
    assert data["description"] == "Updated description"
    assert data["manufacturer_id"] == 2
    assert data["languagemodel_id"] == 2
    assert data["modelchoice_id"] == 2
    assert data["is_active"] is False


def test_update_application_not_found(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")

    response = authenticated_client.put("/api/applications/999999", json= {
        "name": "Does Not Exist",
        "description": "Should fail",
        "manufacturer_id": 1,
        "languagemodel_id": 1,
        "modelchoice_id": 1,
        "is_active": True
    })
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Application not found"

def test_update_application_wrong_data(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = new_application(authenticated_client)
    application_id = response.json()["id"]
    response = authenticated_client.put(f"api/applications/{application_id}", json={
        "name": "Updated Application",
        "description": "Updated description",
        "manufacturer_id": 9999999,
        "languagemodel_id": 1,
        "modelchoice_id": 1,
        "is_active": False
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Manufacturer not found"

    response = authenticated_client.put(f"api/applications/{application_id}", json={
        "name": "Updated Application",
        "description": "Updated description",
        "manufacturer_id": 1,
        "languagemodel_id": 999999,
        "modelchoice_id": 1,
        "is_active": True
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Language model not found"

    response = authenticated_client.put(f"api/applications/{application_id}", json={
        "name": "Updated Application",
        "description": "Updated description",
        "manufacturer_id": 1,
        "languagemodel_id": 1,
        "modelchoice_id": 99999,
        "is_active": True
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Model choice not found"


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


def test_get_active_applications_with_manufacturer(client):
    response = client.get("/api/applications/with-manufacturer")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for app in data:
        assert app["is_active"] is True
        assert "manufacturer_id" in app
        assert "manufacturer_name" in app
        assert "languagemodel_name" in app
        assert "modelchoice_name" in app

def test_get_applications_with_manufacturer_admin(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    response = authenticated_client.get("/api/applications/with-manufacturer-user")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

def test_get_applications_with_manufacturer_user(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("user@example.com")
    response = authenticated_client.get("/api/applications/with-manufacturer-user")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_applications_with_manufacturer_no_login(client):
    response = client.get("/api/applications/with-manufacturer-user")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_applications_with_manufacturer_inactive_user(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("inactive@example.com")
    response = authenticated_client.get("/api/applications/with-manufacturer-user")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this data"

def test_get_application_stats(client):
    response = client.get("/api/applications/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert data["active"] == 2

def test_selection_save(authenticated_client_for_email, db):
    userid = 1
    authenticated_client = authenticated_client_for_email("admin@example.com")
    au = db.query(ApplicationUser).filter(ApplicationUser.user_id == userid).all()
    assert au is not None
    assert len(au) == 1
    payload = {
        "application_id": 1,
        "selected": False
    }
    response = authenticated_client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 200

    payload = {
        "application_id": 2,
        "selected": True
    }
    response = authenticated_client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 200


    db.expire_all() 
    entry1 = db.query(ApplicationUser).filter_by(user_id=userid, application_id=1).first()
    entry2 = db.query(ApplicationUser).filter_by(user_id=userid, application_id=2).first()

    assert not entry1.selected
    assert entry2 is not None
    assert entry2.selected is True

    au = db.query(ApplicationUser).filter(ApplicationUser.user_id == userid).all()
    assert au is not None
    assert len(au) == 2

    userid = 2
    authenticated_client = authenticated_client_for_email("user@example.com")
    au = db.query(ApplicationUser).filter(ApplicationUser.user_id == userid).all()
    assert au is not None
    assert len(au) == 1
    payload = {
        "application_id": 2,
        "selected": False
    }
    response = authenticated_client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 200

    payload = {
        "application_id": 1,
        "selected": True
    }
    response = authenticated_client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 200


    db.expire_all() 
    entry1 = db.query(ApplicationUser).filter_by(user_id=userid, application_id=2).first()
    entry2 = db.query(ApplicationUser).filter_by(user_id=userid, application_id=1).first()

    assert not entry1.selected
    assert entry2 is not None
    assert entry2.selected is True

    au = db.query(ApplicationUser).filter(ApplicationUser.user_id == userid).all()
    assert au is not None
    assert len(au) == 2

def test_selection_save_no_user(authenticated_client_for_email, client):
    authenticated_client = authenticated_client_for_email("inactive@example.com")
    payload = {
        "application_id": 1,
        "selected": False
    }

    response = authenticated_client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to change this data"

    response = client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_selection_save_no_application(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")
    payload = {
        "application_id": 99999,
        "selected": True
    }

    response = authenticated_client.post(
        "/api/applications/application_selection",
        json=payload
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Application with id 99999 not found"

def test_export_applications_csv(authenticated_client_for_email):
    authenticated_client = authenticated_client_for_email("admin@example.com")

    payload = {
        "application_id": 2,
        "selected": False
    }
    response = authenticated_client.post("/api/applications/application_selection", json=payload)
    assert response.status_code == 200

    response = authenticated_client.get("/api/applications/export/csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=applications.csv" in response.headers["content-disposition"]

    content = response.content.decode()
    f = io.StringIO(content)
    reader = csv.reader(f)
    rows = list(reader)

    assert rows[0] == ["Application", "Description", "Manufacturer", "LanguageModel", "ModelChoice", "Selected"]


    app1_row = next(row for row in rows if "Office" in row)
    assert app1_row[-1] in ("True", "true", "1", "True") 

    app1_row = next(row for row in rows if "Visual Studio Code" in row)
    assert app1_row[-1] in ("False", "false", "0")

def test_export_applications_csv_no_user(authenticated_client_for_email, client):
    authenticated_client = authenticated_client_for_email("inactive@example.com")


    response = authenticated_client.get("/api/applications/export/csv")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to retrieve this data"

    response = client.get("/api/applications/export/csv")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
