import pytest
import json
from app import create_app, db
from app.models.user import User
from app.models.incident import Incident

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Get authentication headers"""
    def _auth_headers(token):
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    return _auth_headers

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'OK'

def test_user_registration(client):
    """Test user registration"""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    response = client.post('/api/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'token' in data
    assert data['user']['email'] == user_data['email']

def test_user_login(client):
    """Test user login"""
    # First register a user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    client.post('/api/auth/register',
                data=json.dumps(user_data),
                content_type='application/json')
    
    # Then login
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_create_incident(client, auth_headers):
    """Test incident creation"""
    # First register and login
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    register_response = client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
    
    token = json.loads(register_response.data)['token']
    headers = auth_headers(token)
    
    # Create incident
    incident_data = {
        'title': 'Test Incident',
        'description': 'This is a test incident description',
        'category': 'infrastructure',
        'priority': 'medium',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': '123 Test Street',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345'
    }
    
    response = client.post('/api/incidents',
                          data=json.dumps(incident_data),
                          headers=headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['incident']['title'] == incident_data['title']

def test_get_incidents(client):
    """Test getting all incidents"""
    response = client.get('/api/incidents')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'incidents' in data
    assert 'pagination' in data

def test_get_incident_stats(client):
    """Test getting incident statistics"""
    response = client.get('/api/incidents/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'stats' in data
    assert 'summary' in data

def test_admin_dashboard(client, auth_headers):
    """Test admin dashboard"""
    # Create admin user
    admin_data = {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin'
    }
    
    register_response = client.post('/api/auth/register',
                                  data=json.dumps(admin_data),
                                  content_type='application/json')
    
    token = json.loads(register_response.data)['token']
    headers = auth_headers(token)
    
    response = client.get('/api/admin/dashboard', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user_stats' in data
    assert 'incident_stats' in data

def test_invalid_login(client):
    """Test invalid login credentials"""
    login_data = {
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 401

def test_duplicate_registration(client):
    """Test duplicate user registration"""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    # Register first time
    client.post('/api/auth/register',
                data=json.dumps(user_data),
                content_type='application/json')
    
    # Try to register again
    response = client.post('/api/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400 