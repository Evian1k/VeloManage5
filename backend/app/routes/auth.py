from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.utils.auth import admin_required, validate_user_data, get_current_user
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input data
        errors = validate_user_data(data)
        if errors:
            return jsonify({
                'error': 'Validation failed',
                'message': 'Please check your input',
                'details': errors
            }), 400
        
        # Check if user already exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return jsonify({
                'error': 'User already exists',
                'message': 'Email is already registered'
            }), 400
        
        existing_username = User.find_by_username(data['username'])
        if existing_username:
            return jsonify({
                'error': 'Username taken',
                'message': 'Username is already taken'
            }), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='user'  # Default role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': 'Unable to register user'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = validate_user_data(data)
        if errors:
            return jsonify({
                'error': 'Validation failed',
                'message': 'Please check your input',
                'details': errors
            }), 400
        
        # Find user
        user = User.find_by_email(data['email'])
        if not user:
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Email or password is incorrect'
            }), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                'error': 'Account disabled',
                'message': 'Your account has been disabled'
            }), 401
        
        # Verify password
        if not user.check_password(data['password']):
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Email or password is incorrect'
            }), 401
        
        # Update last login
        user.update_last_login()
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'message': 'Unable to log in'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User does not exist'
            }), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Profile retrieval failed',
            'message': 'Unable to get user profile'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User does not exist'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            # Check if email is being changed and if it's already taken
            if data['email'] != user.email:
                existing_user = User.find_by_email(data['email'])
                if existing_user:
                    return jsonify({
                        'error': 'Email already exists',
                        'message': 'This email is already registered'
                    }), 400
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Profile update failed',
            'message': 'Unable to update profile'
        }), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User does not exist'
            }), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'error': 'Missing data',
                'message': 'Current password and new password are required'
            }), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({
                'error': 'Invalid password',
                'message': 'Current password is incorrect'
            }), 400
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Password change failed',
            'message': 'Unable to change password'
        }), 500

@auth_bp.route('/users', methods=['GET'])
@admin_required()
def get_all_users():
    """Get all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 20, type=int)
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        if is_active is not None:
            query = query.filter_by(is_active=is_active == 'true')
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'users': users,
            'pagination': {
                'current_page': page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'items_per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'User retrieval failed',
            'message': 'Unable to get users'
        }), 500

@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required()
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User does not exist'
            }), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role or new_role not in ['user', 'admin']:
            return jsonify({
                'error': 'Invalid role',
                'message': 'Role must be "user" or "admin"'
            }), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Role update failed',
            'message': 'Unable to update user role'
        }), 500 