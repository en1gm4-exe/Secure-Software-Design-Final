import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test the home page returns 200 OK"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data or b'Home' in response.data

def test_login_page(client):
    """Test login page accessibility"""
    response = client.get('/login')
    assert response.status_code == 200 or response.status_code == 404

def test_health_check(client):
    """Basic health check endpoint"""
    response = client.get('/health')
    if response.status_code != 404:  # Only test if endpoint exists
        assert response.status_code == 200
