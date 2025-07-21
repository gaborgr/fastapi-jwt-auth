import uuid

# Para generar emails únicos en tests


def test_signup(client):  # 'client' es inyectado desde conftest.py
    email = f"test_{uuid.uuid4().hex}@example.com"  # Email único
    response = client.post(
        "/auth/signup", json={"email": email, "password": "secret123"}
    )
    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == email


def test_login(client, test_user):  # 'test_user' es inyectado desde conftest.py
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
