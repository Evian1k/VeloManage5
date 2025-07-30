from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from app import db

def admin_required():
    """Decorator to require admin role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin():
                return jsonify({
                    'error': 'Access denied',
                    'message': 'Admin privileges required'
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def optional_auth():
    """Decorator for optional authentication"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                if user and user.is_active:
                    request.current_user = user
                else:
                    request.current_user = None
            except:
                request.current_user = None
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """Get current authenticated user"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None

def validate_user_data(data):
    """Validate user registration/login data"""
    errors = []
    
    if 'email' in data:
        if not data['email'] or '@' not in data['email']:
            errors.append('Valid email is required')
    
    if 'password' in data:
        if not data['password'] or len(data['password']) < 6:
            errors.append('Password must be at least 6 characters')
    
    if 'username' in data:
        if not data['username'] or len(data['username']) < 3:
            errors.append('Username must be at least 3 characters')
    
    if 'first_name' in data:
        if not data['first_name']:
            errors.append('First name is required')
    
    if 'last_name' in data:
        if not data['last_name']:
            errors.append('Last name is required')
    
    return errors

def validate_incident_data(data):
    """Validate incident data"""
    errors = []
    
    if not data.get('title') or len(data['title']) < 5:
        errors.append('Title must be at least 5 characters')
    
    if not data.get('description') or len(data['description']) < 10:
        errors.append('Description must be at least 10 characters')
    
    if not data.get('category'):
        errors.append('Category is required')
    elif data['category'] not in ['infrastructure', 'safety', 'environmental', 'traffic', 'public_service', 'other']:
        errors.append('Invalid category')
    
    if not data.get('latitude') or not data.get('longitude'):
        errors.append('Location coordinates are required')
    else:
        try:
            lat = float(data['latitude'])
            lng = float(data['longitude'])
            if lat < -90 or lat > 90:
                errors.append('Invalid latitude')
            if lng < -180 or lng > 180:
                errors.append('Invalid longitude')
        except ValueError:
            errors.append('Invalid coordinates')
    
    return errors 