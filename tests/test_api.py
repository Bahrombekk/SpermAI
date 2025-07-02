# tests/test_api.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['server']['debug'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sperm AI Tahlil Tizimi' in response.data