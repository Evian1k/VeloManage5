from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.service import Service, Part, ServicePart
from app.models.service_record import ServiceRecord, ServiceRecordPart
from app.models.vehicle import Vehicle
from datetime import datetime
import os

services_bp = Blueprint('services', __name__)

# Service routes
@services_bp.route('/services', methods=['GET'])
@jwt_required()
def get_services():
    """Get all available services"""
    category = request.args.get('category')
    
    if category:
        services = Service.get_by_category(category)
    else:
        services = Service.get_active_services()
    
    return jsonify({
        'services': [service.to_dict() for service in services]
    }), 200

@services_bp.route('/services/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service(service_id):
    """Get a specific service by ID"""
    service = Service.query.get(service_id)
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    return jsonify(service.to_dict()), 200

@services_bp.route('/services', methods=['POST'])
@jwt_required()
def create_service():
    """Create a new service (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        service = Service(
            name=data['name'],
            description=data.get('description'),
            category=data['category'],
            estimated_duration=data.get('estimated_duration'),
            estimated_cost=data.get('estimated_cost'),
            mileage_interval=data.get('mileage_interval')
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """Update a service (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'category' in data:
            service.category = data['category']
        if 'estimated_duration' in data:
            service.estimated_duration = data['estimated_duration']
        if 'estimated_cost' in data:
            service.estimated_cost = data['estimated_cost']
        if 'mileage_interval' in data:
            service.mileage_interval = data['mileage_interval']
        if 'is_active' in data:
            service.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service updated successfully',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Parts routes
@services_bp.route('/parts', methods=['GET'])
@jwt_required()
def get_parts():
    """Get all parts"""
    category = request.args.get('category')
    low_stock = request.args.get('low_stock', 'false').lower() == 'true'
    
    query = Part.query
    
    if category:
        query = query.filter(Part.category == category)
    
    if low_stock:
        query = query.filter(Part.stock_quantity <= Part.min_stock_level)
    
    parts = query.filter(Part.is_active == True).all()
    
    return jsonify({
        'parts': [part.to_dict() for part in parts]
    }), 200

@services_bp.route('/parts/<int:part_id>', methods=['GET'])
@jwt_required()
def get_part(part_id):
    """Get a specific part by ID"""
    part = Part.query.get(part_id)
    
    if not part:
        return jsonify({'error': 'Part not found'}), 404
    
    return jsonify(part.to_dict()), 200

@services_bp.route('/parts', methods=['POST'])
@jwt_required()
def create_part():
    """Create a new part (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'part_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if part number already exists
    existing_part = Part.query.filter_by(part_number=data['part_number']).first()
    if existing_part:
        return jsonify({'error': 'Part with this part number already exists'}), 400
    
    try:
        part = Part(
            name=data['name'],
            part_number=data['part_number'],
            description=data.get('description'),
            category=data.get('category'),
            manufacturer=data.get('manufacturer'),
            unit_cost=data.get('unit_cost'),
            stock_quantity=data.get('stock_quantity', 0),
            min_stock_level=data.get('min_stock_level', 5)
        )
        
        db.session.add(part)
        db.session.commit()
        
        return jsonify({
            'message': 'Part created successfully',
            'part': part.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/parts/<int:part_id>', methods=['PUT'])
@jwt_required()
def update_part(part_id):
    """Update a part (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    part = Part.query.get(part_id)
    if not part:
        return jsonify({'error': 'Part not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'name' in data:
            part.name = data['name']
        if 'description' in data:
            part.description = data['description']
        if 'category' in data:
            part.category = data['category']
        if 'manufacturer' in data:
            part.manufacturer = data['manufacturer']
        if 'unit_cost' in data:
            part.unit_cost = data['unit_cost']
        if 'stock_quantity' in data:
            part.stock_quantity = data['stock_quantity']
        if 'min_stock_level' in data:
            part.min_stock_level = data['min_stock_level']
        if 'is_active' in data:
            part.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Part updated successfully',
            'part': part.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/parts/<int:part_id>/stock', methods=['PUT'])
@jwt_required()
def update_part_stock(part_id):
    """Update part stock quantity (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    part = Part.query.get(part_id)
    if not part:
        return jsonify({'error': 'Part not found'}), 404
    
    data = request.get_json()
    quantity = data.get('quantity')
    
    if quantity is None:
        return jsonify({'error': 'Quantity is required'}), 400
    
    try:
        part.update_stock(quantity)
        
        return jsonify({
            'message': 'Stock updated successfully',
            'part': part.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Service records routes
@services_bp.route('/service-records', methods=['GET'])
@jwt_required()
def get_service_records():
    """Get service records for the authenticated user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Admin can see all records, customers see only their own
    if user.is_admin():
        records = ServiceRecord.query.order_by(ServiceRecord.service_date.desc()).all()
    else:
        records = ServiceRecord.get_by_customer(current_user_id)
    
    return jsonify({
        'service_records': [record.to_dict() for record in records]
    }), 200

@services_bp.route('/service-records/<int:record_id>', methods=['GET'])
@jwt_required()
def get_service_record(record_id):
    """Get a specific service record"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    record = ServiceRecord.query.get(record_id)
    
    if not record:
        return jsonify({'error': 'Service record not found'}), 404
    
    # Check if user has access to this record
    if not user.is_admin() and record.customer_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(record.to_dict()), 200

@services_bp.route('/service-records', methods=['POST'])
@jwt_required()
def create_service_record():
    """Create a new service record"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'service_id', 'service_date', 'mileage_at_service']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify vehicle ownership
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        service_record = ServiceRecord(
            vehicle_id=data['vehicle_id'],
            customer_id=current_user_id,
            service_id=data['service_id'],
            mechanic_id=data.get('mechanic_id'),
            service_date=datetime.strptime(data['service_date'], '%Y-%m-%dT%H:%M:%S'),
            mileage_at_service=data['mileage_at_service'],
            actual_duration=data.get('actual_duration'),
            actual_cost=data.get('actual_cost'),
            labor_cost=data.get('labor_cost'),
            parts_cost=data.get('parts_cost'),
            status=data.get('status', 'scheduled'),
            priority=data.get('priority', 'normal'),
            description=data.get('description'),
            work_performed=data.get('work_performed'),
            recommendations=data.get('recommendations'),
            next_service_mileage=data.get('next_service_mileage'),
            next_service_date=datetime.strptime(data['next_service_date'], '%Y-%m-%d').date() if data.get('next_service_date') else None,
            notes=data.get('notes')
        )
        
        db.session.add(service_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Service record created successfully',
            'service_record': service_record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/service-records/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_service_record(record_id):
    """Update a service record"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    record = ServiceRecord.query.get(record_id)
    
    if not record:
        return jsonify({'error': 'Service record not found'}), 404
    
    # Check if user has access to this record
    if not user.is_admin() and record.customer_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'service_date' in data:
            record.service_date = datetime.strptime(data['service_date'], '%Y-%m-%dT%H:%M:%S')
        if 'mileage_at_service' in data:
            record.mileage_at_service = data['mileage_at_service']
        if 'actual_duration' in data:
            record.actual_duration = data['actual_duration']
        if 'actual_cost' in data:
            record.actual_cost = data['actual_cost']
        if 'labor_cost' in data:
            record.labor_cost = data['labor_cost']
        if 'parts_cost' in data:
            record.parts_cost = data['parts_cost']
        if 'status' in data:
            record.status = data['status']
        if 'priority' in data:
            record.priority = data['priority']
        if 'description' in data:
            record.description = data['description']
        if 'work_performed' in data:
            record.work_performed = data['work_performed']
        if 'recommendations' in data:
            record.recommendations = data['recommendations']
        if 'next_service_mileage' in data:
            record.next_service_mileage = data['next_service_mileage']
        if 'next_service_date' in data:
            record.next_service_date = datetime.strptime(data['next_service_date'], '%Y-%m-%d').date() if data['next_service_date'] else None
        if 'notes' in data:
            record.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service record updated successfully',
            'service_record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/service-records/<int:record_id>/complete', methods=['PUT'])
@jwt_required()
def complete_service_record(record_id):
    """Mark a service record as completed (mechanic/admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not (user.is_admin() or user.is_mechanic()):
        return jsonify({'error': 'Mechanic or admin access required'}), 403
    
    record = ServiceRecord.query.get(record_id)
    if not record:
        return jsonify({'error': 'Service record not found'}), 404
    
    data = request.get_json()
    
    try:
        record.mark_completed(
            mechanic_id=current_user_id,
            work_performed=data.get('work_performed'),
            actual_cost=data.get('actual_cost')
        )
        
        return jsonify({
            'message': 'Service record completed successfully',
            'service_record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500