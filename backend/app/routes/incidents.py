from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.models.incident import Incident
from app.models.user import User
from app.utils.auth import admin_required, optional_auth, validate_incident_data, get_current_user
from app import db
from datetime import datetime

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/', methods=['GET'])
@optional_auth()
def get_all_incidents():
    """Get all incidents with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        search = request.args.get('search')
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 10, type=float)
        
        query = Incident.query
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if priority:
            query = query.filter_by(priority=priority)
        
        # Search functionality
        if search:
            search_filter = or_(
                Incident.title.ilike(f'%{search}%'),
                Incident.description.ilike(f'%{search}%'),
                Incident.address.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Location-based filtering
        if lat and lng:
            lat_min = lat - radius/111
            lat_max = lat + radius/111
            lng_min = lng - radius/111
            lng_max = lng + radius/111
            
            query = query.filter(
                Incident.latitude.between(lat_min, lat_max),
                Incident.longitude.between(lng_min, lng_max)
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Incident.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        incidents = [incident.to_dict() for incident in pagination.items]
        
        return jsonify({
            'incidents': incidents,
            'pagination': {
                'current_page': page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'items_per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Incident retrieval failed',
            'message': 'Unable to get incidents'
        }), 500

@incidents_bp.route('/<int:incident_id>', methods=['GET'])
@optional_auth()
def get_incident(incident_id):
    """Get incident by ID"""
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({
                'error': 'Incident not found',
                'message': 'Incident does not exist'
            }), 404
        
        return jsonify({
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Incident retrieval failed',
            'message': 'Unable to get incident'
        }), 500

@incidents_bp.route('/', methods=['POST'])
@jwt_required()
def create_incident():
    """Create new incident"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please log in to report incidents'
            }), 401
        
        data = request.get_json()
        
        # Validate incident data
        errors = validate_incident_data(data)
        if errors:
            return jsonify({
                'error': 'Validation failed',
                'message': 'Please check your input',
                'details': errors
            }), 400
        
        # Create incident
        incident = Incident(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            priority=data.get('priority', 'medium'),
            latitude=data['latitude'],
            longitude=data['longitude'],
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            images=data.get('images', []),
            contact_info=data.get('contact_info', {}),
            estimated_cost=data.get('estimated_cost'),
            estimated_timeframe=data.get('estimated_timeframe'),
            reported_by=current_user_id
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Get incident with reporter info
        incident_with_reporter = Incident.query.get(incident.id)
        
        return jsonify({
            'message': 'Incident reported successfully',
            'incident': incident_with_reporter.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Incident creation failed',
            'message': 'Unable to create incident'
        }), 500

@incidents_bp.route('/<int:incident_id>', methods=['PUT'])
@admin_required()
def update_incident(incident_id):
    """Update incident (admin only)"""
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({
                'error': 'Incident not found',
                'message': 'Incident does not exist'
            }), 404
        
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Update fields
        if 'title' in data:
            incident.title = data['title']
        if 'description' in data:
            incident.description = data['description']
        if 'status' in data:
            incident.status = data['status']
            # Handle status change to resolved
            if data['status'] == 'resolved' and incident.status != 'resolved':
                incident.resolved_at = datetime.utcnow()
                incident.assigned_to = current_user_id
        if 'priority' in data:
            incident.priority = data['priority']
        if 'assigned_to' in data:
            incident.assigned_to = data['assigned_to']
        if 'resolution_notes' in data:
            incident.resolution_notes = data['resolution_notes']
        
        db.session.commit()
        
        # Get updated incident with associations
        updated_incident = Incident.query.get(incident_id)
        
        return jsonify({
            'message': 'Incident updated successfully',
            'incident': updated_incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Incident update failed',
            'message': 'Unable to update incident'
        }), 500

@incidents_bp.route('/<int:incident_id>', methods=['DELETE'])
@admin_required()
def delete_incident(incident_id):
    """Delete incident (admin only)"""
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({
                'error': 'Incident not found',
                'message': 'Incident does not exist'
            }), 404
        
        db.session.delete(incident)
        db.session.commit()
        
        return jsonify({
            'message': 'Incident deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Incident deletion failed',
            'message': 'Unable to delete incident'
        }), 500

@incidents_bp.route('/user/incidents', methods=['GET'])
@jwt_required()
def get_user_incidents():
    """Get current user's reported incidents"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        
        query = Incident.query.filter_by(reported_by=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Incident.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        incidents = [incident.to_dict() for incident in pagination.items]
        
        return jsonify({
            'incidents': incidents,
            'pagination': {
                'current_page': page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'items_per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Incident retrieval failed',
            'message': 'Unable to get user incidents'
        }), 500

@incidents_bp.route('/<int:incident_id>/vote', methods=['POST'])
@jwt_required()
def vote_incident(incident_id):
    """Vote on incident"""
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({
                'error': 'Incident not found',
                'message': 'Incident does not exist'
            }), 404
        
        data = request.get_json()
        vote_type = data.get('vote_type')
        
        if not vote_type or vote_type not in ['upvote', 'downvote']:
            return jsonify({
                'error': 'Invalid vote type',
                'message': 'Vote type must be "upvote" or "downvote"'
            }), 400
        
        incident.add_vote(vote_type)
        
        return jsonify({
            'message': 'Vote recorded successfully',
            'incident': {
                'id': incident.id,
                'upvotes': incident.upvotes,
                'downvotes': incident.downvotes,
                'vote_count': incident.get_vote_count()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Vote recording failed',
            'message': 'Unable to record vote'
        }), 500

@incidents_bp.route('/stats', methods=['GET'])
@optional_auth()
def get_incident_stats():
    """Get incident statistics"""
    try:
        stats = Incident.get_stats()
        
        # Calculate additional statistics
        total_incidents = Incident.query.count()
        open_incidents = Incident.query.filter_by(status='open').count()
        resolved_incidents = Incident.query.filter_by(status='resolved').count()
        in_progress_incidents = Incident.query.filter_by(status='in_progress').count()
        
        return jsonify({
            'stats': stats,
            'summary': {
                'total': total_incidents,
                'open': open_incidents,
                'resolved': resolved_incidents,
                'in_progress': in_progress_incidents
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Statistics retrieval failed',
            'message': 'Unable to get incident statistics'
        }), 500

@incidents_bp.route('/<int:incident_id>/assign', methods=['POST'])
@admin_required()
def assign_incident(incident_id):
    """Assign incident to admin"""
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({
                'error': 'Incident not found',
                'message': 'Incident does not exist'
            }), 404
        
        data = request.get_json()
        admin_id = data.get('admin_id')
        
        if not admin_id:
            return jsonify({
                'error': 'Missing data',
                'message': 'Admin ID is required'
            }), 400
        
        # Verify admin exists
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin():
            return jsonify({
                'error': 'Invalid admin',
                'message': 'Specified user is not an admin'
            }), 400
        
        incident.assigned_to = admin_id
        db.session.commit()
        
        return jsonify({
            'message': 'Incident assigned successfully',
            'incident': {
                'id': incident.id,
                'assigned_to': admin_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Assignment failed',
            'message': 'Unable to assign incident'
        }), 500 