import os
import tempfile

database_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
database_file.close()
os.environ["DATABASE_PATH"] = database_file.name
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"

from fastapi.testclient import TestClient

from main import app

def login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_public_route_is_open() -> None:
    with TestClient(app) as client:
        response = client.get("/publico")
    assert response.status_code == 200

def test_login_and_private_route() -> None:
    with TestClient(app) as client:
        token = login(client, "estudiante@ujap.edu.ve", "estudiante123")
        response = client.get(
            "/privado", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert "estudiante@ujap.edu.ve" in response.json()["msg"]

def test_student_cannot_access_admin() -> None:
    with TestClient(app) as client:
        token = login(client, "estudiante@ujap.edu.ve", "estudiante123")
        response = client.get(
            "/admin", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 403

def test_missing_or_invalid_token_is_unauthorized() -> None:
    with TestClient(app) as client:
        missing = client.get("/privado")
        invalid = client.get(
            "/privado", headers={"Authorization": "Bearer not-a-jwt"}
        )
    assert missing.status_code == 401
    assert invalid.status_code == 401