from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    """FastAPI test client fixture for testing endpoints."""
    return TestClient(app)