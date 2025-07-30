from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.incident import Incident
from app.utils.auth import admin_required
from app import db
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required()
def admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        # Incident statistics
        total_incidents = Incident.query.count()
        open_incidents = Incident.query.filter_by(status='open').count()
        in_progress_incidents = Incident.query.filter_by(status='in_progress').count()
        resolved_incidents = Incident.query.filter_by(status='resolved').count()
        
        # Category statistics
        category_stats = db.session.query(
            Incident.category,
            func.count(Incident.id).label('count')
        ).group_by(Incident.category).all()
        
        # Priority statistics
        priority_stats = db.session.query(
            Incident.priority,
            func.count(Incident.id).label('count')
        ).group_by(Incident.priority).all()
        
        # Recent incidents
        recent_incidents = Incident.query.order_by(
            Incident.created_at.desc()
        ).limit(5).all()
        
        return jsonify({
            'user_stats': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users
            },
            'incident_stats': {
                'total': total_incidents,
                'open': open_incidents,
                'in_progress': in_progress_incidents,
                'resolved': resolved_incidents
            },
            'category_stats': [
                {'category': stat.category, 'count': stat.count}
                for stat in category_stats
            ],
            'priority_stats': [
                {'priority': stat.priority, 'count': stat.count}
                for stat in priority_stats
            ],
            'recent_incidents': [
                incident.to_dict() for incident in recent_incidents
            ]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Dashboard retrieval failed',
            'message': 'Unable to get dashboard data'
        }), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@admin_required()
def toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'User does not exist'
            }), 404
        
        # Prevent admin from deactivating themselves
        current_user_id = get_jwt_identity()
        if user.id == current_user_id:
            return jsonify({
                'error': 'Cannot deactivate self',
                'message': 'You cannot deactivate your own account'
            }), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Status update failed',
            'message': 'Unable to update user status'
        }), 500

@admin_bp.route('/incidents/bulk-update', methods=['PUT'])
@admin_required()
def bulk_update_incidents():
    """Bulk update incidents (admin only)"""
    try:
        data = request.get_json()
        incident_ids = data.get('incident_ids', [])
        updates = data.get('updates', {})
        
        if not incident_ids:
            return jsonify({
                'error': 'Missing data',
                'message': 'Incident IDs are required'
            }), 400
        
        # Validate updates
        allowed_fields = ['status', 'priority', 'assigned_to']
        for field in updates:
            if field not in allowed_fields:
                return jsonify({
                    'error': 'Invalid field',
                    'message': f'Field "{field}" cannot be updated in bulk'
                }), 400
        
        # Update incidents
        updated_count = 0
        for incident_id in incident_ids:
            incident = Incident.query.get(incident_id)
            if incident:
                for field, value in updates.items():
                    setattr(incident, field, value)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'{updated_count} incidents updated successfully',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Bulk update failed',
            'message': 'Unable to update incidents'
        }), 500

@admin_bp.route('/reports/incident-summary', methods=['GET'])
@admin_required()
def incident_summary_report():
    """Generate incident summary report (admin only)"""
    try:
        from datetime import datetime, timedelta
        
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get incidents in date range
        incidents = Incident.query.filter(
            Incident.created_at.between(start_date, end_date)
        ).all()
        
        # Calculate statistics
        total_incidents = len(incidents)
        resolved_incidents = len([i for i in incidents if i.status == 'resolved'])
        avg_resolution_time = None
        
        if resolved_incidents > 0:
            resolution_times = []
            for incident in incidents:
                if incident.status == 'resolved' and incident.resolved_at:
                    resolution_time = (incident.resolved_at - incident.created_at).days
                    resolution_times.append(resolution_time)
            
            if resolution_times:
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        # Category breakdown
        category_breakdown = {}
        for incident in incidents:
            category = incident.category
            if category not in category_breakdown:
                category_breakdown[category] = 0
            category_breakdown[category] += 1
        
        # Priority breakdown
        priority_breakdown = {}
        for incident in incidents:
            priority = incident.priority
            if priority not in priority_breakdown:
                priority_breakdown[priority] = 0
            priority_breakdown[priority] += 1
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_incidents': total_incidents,
                'resolved_incidents': resolved_incidents,
                'resolution_rate': (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0,
                'avg_resolution_time_days': round(avg_resolution_time, 1) if avg_resolution_time else None
            },
            'category_breakdown': category_breakdown,
            'priority_breakdown': priority_breakdown
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Report generation failed',
            'message': 'Unable to generate report'
        }), 500 