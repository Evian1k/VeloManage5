from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.service import Service, Part
from app.models.service_record import ServiceRecord, Appointment
from datetime import datetime, timedelta
from sqlalchemy import func
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Get admin dashboard statistics"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get statistics
        total_vehicles = Vehicle.query.count()
        total_customers = User.query.filter_by(role='customer').count()
        total_mechanics = User.query.filter_by(role='mechanic').count()
        total_services = Service.query.filter_by(is_active=True).count()
        
        # Get recent appointments
        recent_appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).limit(5).all()
        
        # Get vehicles due for service
        vehicles_due_service = []
        all_vehicles = Vehicle.query.all()
        for vehicle in all_vehicles:
            if vehicle.is_due_for_service():
                vehicles_due_service.append(vehicle.to_dict())
        
        # Get low stock parts
        low_stock_parts = Part.get_low_stock_parts()
        
        # Get today's appointments
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        today_appointments = Appointment.query.filter(
            Appointment.appointment_date.between(today, tomorrow)
        ).all()
        
        return jsonify({
            'statistics': {
                'total_vehicles': total_vehicles,
                'total_customers': total_customers,
                'total_mechanics': total_mechanics,
                'total_services': total_services,
                'today_appointments': len(today_appointments),
                'vehicles_due_service': len(vehicles_due_service),
                'low_stock_parts': len(low_stock_parts)
            },
            'recent_appointments': [appointment.to_dict() for appointment in recent_appointments],
            'vehicles_due_service': vehicles_due_service,
            'low_stock_parts': [part.to_dict() for part in low_stock_parts],
            'today_appointments': [appointment.to_dict() for appointment in today_appointments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    role = request.args.get('role')
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    users = query.all()
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user (admin only)"""
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or not admin_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user (admin only)"""
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or not admin_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (admin only)"""
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or not admin_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/vehicles', methods=['GET'])
@jwt_required()
def admin_get_vehicles():
    """Get all vehicles (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    status = request.args.get('status')
    make = request.args.get('make')
    model = request.args.get('model')
    
    query = Vehicle.query
    
    if status:
        query = query.filter_by(status=status)
    if make:
        query = query.filter(Vehicle.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))
    
    vehicles = query.all()
    
    return jsonify({
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    }), 200

@admin_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def admin_update_vehicle(vehicle_id):
    """Update a vehicle (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'status' in data:
            vehicle.status = data['status']
        if 'location' in data:
            vehicle.location = data['location']
        if 'current_value' in data:
            vehicle.current_value = data['current_value']
        if 'sale_price' in data:
            vehicle.sale_price = data['sale_price']
        if 'owner_id' in data:
            vehicle.owner_id = data['owner_id']
        if 'is_company_owned' in data:
            vehicle.is_company_owned = data['is_company_owned']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/service-records', methods=['GET'])
@jwt_required()
def admin_get_service_records():
    """Get all service records (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    status = request.args.get('status')
    vehicle_id = request.args.get('vehicle_id')
    customer_id = request.args.get('customer_id')
    
    query = ServiceRecord.query
    
    if status:
        query = query.filter_by(status=status)
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    records = query.order_by(ServiceRecord.service_date.desc()).all()
    
    return jsonify({
        'service_records': [record.to_dict() for record in records]
    }), 200

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
def admin_get_appointments():
    """Get all appointments (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Appointment.query
    
    if status:
        query = query.filter_by(status=status)
    
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Appointment.appointment_date.between(start_dt, end_dt))
    
    appointments = query.order_by(Appointment.appointment_date).all()
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments]
    }), 200

@admin_bp.route('/reports/service-summary', methods=['GET'])
@jwt_required()
def service_summary_report():
    """Get service summary report (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = ServiceRecord.query
    
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(ServiceRecord.service_date.between(start_dt, end_dt))
    
    # Get statistics
    total_services = query.count()
    completed_services = query.filter_by(status='completed').count()
    total_revenue = query.with_entities(func.sum(ServiceRecord.actual_cost)).scalar() or 0
    
    # Get services by category
    services_by_category = db.session.query(
        Service.category,
        func.count(ServiceRecord.id).label('count')
    ).join(ServiceRecord).group_by(Service.category).all()
    
    # Get top mechanics
    top_mechanics = db.session.query(
        User.first_name,
        User.last_name,
        func.count(ServiceRecord.id).label('service_count')
    ).join(ServiceRecord, User.id == ServiceRecord.mechanic_id).group_by(User.id).order_by(func.count(ServiceRecord.id).desc()).limit(5).all()
    
    return jsonify({
        'summary': {
            'total_services': total_services,
            'completed_services': completed_services,
            'completion_rate': (completed_services / total_services * 100) if total_services > 0 else 0,
            'total_revenue': float(total_revenue)
        },
        'services_by_category': [
            {'category': item.category, 'count': item.count}
            for item in services_by_category
        ],
        'top_mechanics': [
            {
                'name': f"{item.first_name} {item.last_name}",
                'service_count': item.service_count
            }
            for item in top_mechanics
        ]
    }), 200

@admin_bp.route('/reports/vehicle-status', methods=['GET'])
@jwt_required()
def vehicle_status_report():
    """Get vehicle status report (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get vehicles by status
    vehicles_by_status = db.session.query(
        Vehicle.status,
        func.count(Vehicle.id).label('count')
    ).group_by(Vehicle.status).all()
    
    # Get vehicles by make
    vehicles_by_make = db.session.query(
        Vehicle.make,
        func.count(Vehicle.id).label('count')
    ).group_by(Vehicle.make).order_by(func.count(Vehicle.id).desc()).limit(10).all()
    
    # Get vehicles due for service
    vehicles_due_service = []
    all_vehicles = Vehicle.query.all()
    for vehicle in all_vehicles:
        if vehicle.is_due_for_service():
            vehicles_due_service.append(vehicle.to_dict())
    
    return jsonify({
        'vehicles_by_status': [
            {'status': item.status, 'count': item.count}
            for item in vehicles_by_status
        ],
        'vehicles_by_make': [
            {'make': item.make, 'count': item.count}
            for item in vehicles_by_make
        ],
        'vehicles_due_service': vehicles_due_service
    }), 200

@admin_bp.route('/notifications/service-reminders', methods=['POST'])
@jwt_required()
def send_service_reminders():
    """Send service reminders to customers (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Find vehicles due for service
        vehicles_due_service = []
        all_vehicles = Vehicle.query.all()
        
        for vehicle in all_vehicles:
            if vehicle.is_due_for_service():
                vehicles_due_service.append(vehicle)
        
        # Send notifications (placeholder for email/SMS integration)
        notifications_sent = 0
        for vehicle in vehicles_due_service:
            if vehicle.owner:
                # Here you would integrate with email/SMS service
                notifications_sent += 1
        
        return jsonify({
            'message': f'Service reminders sent to {notifications_sent} customers',
            'vehicles_due_service': [vehicle.to_dict() for vehicle in vehicles_due_service]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 