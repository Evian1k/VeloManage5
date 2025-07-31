from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.service_record import ServiceRecord
from datetime import datetime
import os

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/', methods=['GET'])
@jwt_required()
def get_vehicles():
    """Get all vehicles for the authenticated user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Admin can see all vehicles, customers see only their own
    if user.is_admin():
        vehicles = Vehicle.query.all()
    else:
        vehicles = Vehicle.query.filter_by(owner_id=current_user_id).all()
    
    return jsonify({
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    }), 200

@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicle(vehicle_id):
    """Get a specific vehicle by ID"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    # Check if user has access to this vehicle
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(vehicle.to_dict()), 200

@vehicles_bp.route('/', methods=['POST'])
@jwt_required()
def create_vehicle():
    """Create a new vehicle"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vin', 'make', 'model', 'year']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if VIN already exists
    existing_vehicle = Vehicle.find_by_vin(data['vin'])
    if existing_vehicle:
        return jsonify({'error': 'Vehicle with this VIN already exists'}), 400
    
    try:
        vehicle = Vehicle(
            vin=data['vin'],
            make=data['make'],
            model=data['model'],
            year=data['year'],
            color=data.get('color'),
            mileage=data.get('mileage', 0),
            fuel_type=data.get('fuel_type'),
            transmission=data.get('transmission'),
            engine_size=data.get('engine_size'),
            license_plate=data.get('license_plate'),
            registration_expiry=datetime.strptime(data['registration_expiry'], '%Y-%m-%d').date() if data.get('registration_expiry') else None,
            insurance_expiry=datetime.strptime(data['insurance_expiry'], '%Y-%m-%d').date() if data.get('insurance_expiry') else None,
            location=data.get('location'),
            purchase_price=data.get('purchase_price'),
            current_value=data.get('current_value'),
            sale_price=data.get('sale_price'),
            owner_id=current_user_id,
            is_company_owned=data.get('is_company_owned', False),
            features=data.get('features', []),
            notes=data.get('notes')
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle created successfully',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update a vehicle"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    # Check if user has access to this vehicle
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'make' in data:
            vehicle.make = data['make']
        if 'model' in data:
            vehicle.model = data['model']
        if 'year' in data:
            vehicle.year = data['year']
        if 'color' in data:
            vehicle.color = data['color']
        if 'mileage' in data:
            vehicle.mileage = data['mileage']
        if 'fuel_type' in data:
            vehicle.fuel_type = data['fuel_type']
        if 'transmission' in data:
            vehicle.transmission = data['transmission']
        if 'engine_size' in data:
            vehicle.engine_size = data['engine_size']
        if 'license_plate' in data:
            vehicle.license_plate = data['license_plate']
        if 'registration_expiry' in data:
            vehicle.registration_expiry = datetime.strptime(data['registration_expiry'], '%Y-%m-%d').date() if data['registration_expiry'] else None
        if 'insurance_expiry' in data:
            vehicle.insurance_expiry = datetime.strptime(data['insurance_expiry'], '%Y-%m-%d').date() if data['insurance_expiry'] else None
        if 'location' in data:
            vehicle.location = data['location']
        if 'status' in data:
            vehicle.status = data['status']
        if 'purchase_price' in data:
            vehicle.purchase_price = data['purchase_price']
        if 'current_value' in data:
            vehicle.current_value = data['current_value']
        if 'sale_price' in data:
            vehicle.sale_price = data['sale_price']
        if 'features' in data:
            vehicle.features = data['features']
        if 'notes' in data:
            vehicle.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    # Check if user has access to this vehicle
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({'message': 'Vehicle deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vehicles_bp.route('/<int:vehicle_id>/service-history', methods=['GET'])
@jwt_required()
def get_vehicle_service_history(vehicle_id):
    """Get service history for a vehicle"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    # Check if user has access to this vehicle
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    service_records = ServiceRecord.get_by_vehicle(vehicle_id)
    
    return jsonify({
        'vehicle': vehicle.to_dict(),
        'service_history': [record.to_dict() for record in service_records]
    }), 200

@vehicles_bp.route('/<int:vehicle_id>/service-reminder', methods=['GET'])
@jwt_required()
def get_service_reminder(vehicle_id):
    """Check if vehicle is due for service"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    # Check if user has access to this vehicle
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    is_due = vehicle.is_due_for_service()
    last_service = vehicle.service_records.order_by(ServiceRecord.service_date.desc()).first()
    
    return jsonify({
        'vehicle': vehicle.to_dict(),
        'is_due_for_service': is_due,
        'last_service': last_service.to_dict() if last_service else None,
        'current_mileage': vehicle.mileage
    }), 200

@vehicles_bp.route('/search', methods=['GET'])
@jwt_required()
def search_vehicles():
    """Search vehicles by various criteria"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Get search parameters
    make = request.args.get('make')
    model = request.args.get('model')
    status = request.args.get('status')
    year = request.args.get('year')
    
    # Build query
    query = Vehicle.query
    
    # Apply filters
    if make:
        query = query.filter(Vehicle.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))
    if status:
        query = query.filter(Vehicle.status == status)
    if year:
        query = query.filter(Vehicle.year == year)
    
    # Apply user access restrictions
    if not user.is_admin():
        query = query.filter(Vehicle.owner_id == current_user_id)
    
    vehicles = query.all()
    
    return jsonify({
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    }), 200