from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.service import Service
from app.models.service_record import Appointment
from datetime import datetime, timedelta
import os

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get appointments for the authenticated user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get query parameters
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    if user.is_admin():
        query = Appointment.query
    elif user.is_mechanic():
        query = Appointment.query.filter_by(mechanic_id=current_user_id)
    else:
        query = Appointment.query.filter_by(customer_id=current_user_id)
    
    # Apply filters
    if status:
        query = query.filter(Appointment.status == status)
    
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Appointment.appointment_date.between(start_dt, end_dt))
    
    appointments = query.order_by(Appointment.appointment_date).all()
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments]
    }), 200

@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get a specific appointment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if not user.is_admin() and appointment.customer_id != current_user_id and appointment.mechanic_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(appointment.to_dict()), 200

@appointments_bp.route('/', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'service_id', 'appointment_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify vehicle ownership
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    if not user.is_admin() and vehicle.owner_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Verify service exists
    service = Service.query.get(data['service_id'])
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    try:
        appointment = Appointment(
            customer_id=current_user_id,
            vehicle_id=data['vehicle_id'],
            service_id=data['service_id'],
            mechanic_id=data.get('mechanic_id'),
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%dT%H:%M:%S'),
            estimated_duration=data.get('estimated_duration', service.estimated_duration),
            description=data.get('description'),
            special_requests=data.get('special_requests'),
            customer_notes=data.get('customer_notes')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update an appointment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if not user.is_admin() and appointment.customer_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    try:
        # Update fields
        if 'appointment_date' in data:
            appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%dT%H:%M:%S')
        if 'estimated_duration' in data:
            appointment.estimated_duration = data['estimated_duration']
        if 'description' in data:
            appointment.description = data['description']
        if 'special_requests' in data:
            appointment.special_requests = data['special_requests']
        if 'customer_notes' in data:
            appointment.customer_notes = data['customer_notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Delete an appointment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if not user.is_admin() and appointment.customer_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        
        return jsonify({'message': 'Appointment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>/confirm', methods=['PUT'])
@jwt_required()
def confirm_appointment(appointment_id):
    """Confirm an appointment (admin/mechanic only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not (user.is_admin() or user.is_mechanic()):
        return jsonify({'error': 'Admin or mechanic access required'}), 403
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    data = request.get_json()
    
    try:
        appointment.confirm(mechanic_id=data.get('mechanic_id', current_user_id))
        
        return jsonify({
            'message': 'Appointment confirmed successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>/start', methods=['PUT'])
@jwt_required()
def start_appointment(appointment_id):
    """Start an appointment (admin/mechanic only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not (user.is_admin() or user.is_mechanic()):
        return jsonify({'error': 'Admin or mechanic access required'}), 403
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    try:
        appointment.start_service()
        
        return jsonify({
            'message': 'Appointment started successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>/complete', methods=['PUT'])
@jwt_required()
def complete_appointment(appointment_id):
    """Complete an appointment (admin/mechanic only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not (user.is_admin() or user.is_mechanic()):
        return jsonify({'error': 'Admin or mechanic access required'}), 403
    
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    try:
        appointment.complete()
        
        return jsonify({
            'message': 'Appointment completed successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check if user has access to this appointment
    if not user.is_admin() and appointment.customer_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        appointment.cancel()
        
        return jsonify({
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    """Get available appointment slots for a specific date"""
    date_str = request.args.get('date')
    service_id = request.args.get('service_id')
    
    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Define business hours (9 AM to 5 PM)
    start_hour = 9
    end_hour = 17
    slot_duration = 60  # 1 hour slots
    
    # Generate available slots
    available_slots = []
    current_time = target_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = target_date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    while current_time < end_time:
        # Check if slot is available (not conflicting with existing appointments)
        conflicting_appointments = Appointment.query.filter(
            Appointment.appointment_date == current_time,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).count()
        
        if conflicting_appointments == 0:
            available_slots.append(current_time.strftime('%Y-%m-%dT%H:%M:%S'))
        
        current_time += timedelta(minutes=slot_duration)
    
    return jsonify({
        'date': date_str,
        'available_slots': available_slots
    }), 200

@appointments_bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_appointments():
    """Get upcoming appointments for the authenticated user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get appointments from today onwards
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if user.is_admin():
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).order_by(Appointment.appointment_date).all()
    elif user.is_mechanic():
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.mechanic_id == current_user_id,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).order_by(Appointment.appointment_date).all()
    else:
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.customer_id == current_user_id,
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).order_by(Appointment.appointment_date).all()
    
    return jsonify({
        'upcoming_appointments': [appointment.to_dict() for appointment in appointments]
    }), 200