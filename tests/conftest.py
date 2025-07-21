import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal, get_db


@pytest.fixture(scope="module")
def test_db():
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    # Limpiar después
    db.close()
    Base.metadata.drop_all(bind=engine)
    # Eliminar archivo de test
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(scope="module")
def client():
    # Configurar TestClient con dependencias override
    def override_get_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    # Usa un email único para cada test
    email = f"test_{uuid.uuid4().hex}@example.com"
    user_data = {"email": email, "password": "secret123"}
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    return user_data
