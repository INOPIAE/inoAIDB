def test_page_exists_success(client):
    response = client.get("api/utils/page-exists", params={"file": "about_en.html"})
    assert response.status_code == 200
    assert response.json() == {"exists": True}

def test_page_exists_not_found(client):
    response = client.get("api/utils/page-exists", params={"file": "missing.txt"})
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"

def test_page_exists_invalid_name_traversal(client):
    response = client.get("api/utils/page-exists", params={"file": "../secret.txt"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file name"

def test_page_exists_invalid_name_absolute(client):
    response = client.get("api/utils/page-exists", params={"file": "/etc/passwd"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file name"
