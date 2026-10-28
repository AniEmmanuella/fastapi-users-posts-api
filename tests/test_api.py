import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


USER = {"username": "ada", "email": "ada@example.com"}


def test_create_user_returns_201(client):
    r = client.post("/users", json=USER)
    assert r.status_code == 201
    assert r.json()["username"] == "ada"


def test_duplicate_user_returns_409(client):
    client.post("/users", json=USER)
    r = client.post("/users", json=USER)
    assert r.status_code == 409
    assert r.json() == {"detail": "Username or email already exists"}


def test_invalid_input_returns_422(client):
    r = client.post("/users", json={"username": "ab", "email": "not-an-email"})
    assert r.status_code == 422
    fields = {err["loc"][-1] for err in r.json()["detail"]}
    assert fields == {"username", "email"}


def test_missing_user_returns_404(client):
    r = client.get("/users/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "User not found"}


def test_create_post_and_read_user_with_posts(client):
    user_id = client.post("/users", json=USER).json()["id"]
    r = client.post(f"/users/{user_id}/posts", json={"title": "Hi", "content": "Hello"})
    assert r.status_code == 201
    detail = client.get(f"/users/{user_id}").json()
    assert len(detail["posts"]) == 1


def test_post_for_missing_user_returns_404(client):
    r = client.post("/users/999/posts", json={"title": "Hi", "content": "Hello"})
    assert r.status_code == 404


def test_delete_user_returns_204_then_404(client):
    user_id = client.post("/users", json=USER).json()["id"]
    assert client.delete(f"/users/{user_id}").status_code == 204
    assert client.get(f"/users/{user_id}").status_code == 404
