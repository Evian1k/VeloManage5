from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Incident(db.Model):
    """Incident model for civic incident reporting"""
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # infrastructure, safety, environmental, traffic, public_service, other
    status = db.Column(db.String(20), default='open', nullable=False)  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium', nullable=False)  # low, medium, high, critical
    
    # Geolocation
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    
    # Additional fields
    images = db.Column(db.JSON)  # Store image URLs
    contact_info = db.Column(db.JSON)  # Store contact information
    estimated_cost = db.Column(db.Numeric(12, 2))
    estimated_timeframe = db.Column(db.String(100))
    
    # Relationships
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Resolution fields
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Voting
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Incident, self).__init__(**kwargs)
        if not self.images:
            self.images = []
        if not self.contact_info:
            self.contact_info = {}
    
    def to_dict(self):
        """Convert incident to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'images': self.images,
            'contact_info': self.contact_info,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'estimated_timeframe': self.estimated_timeframe,
            'reported_by': self.reported_by,
            'assigned_to': self.assigned_to,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'vote_count': self.get_vote_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'reporter': self.reporter.to_dict() if self.reporter else None,
            'assigned_admin': self.assigned_admin.to_dict() if self.assigned_admin else None
        }
    
    def get_vote_count(self):
        """Get net vote count"""
        return self.upvotes - self.downvotes
    
    def mark_as_resolved(self, notes=None, admin_id=None):
        """Mark incident as resolved"""
        self.status = 'resolved'
        self.resolved_at = datetime.utcnow()
        self.resolution_notes = notes
        self.assigned_to = admin_id
        db.session.commit()
    
    def add_vote(self, vote_type):
        """Add a vote to the incident"""
        if vote_type == 'upvote':
            self.upvotes += 1
        elif vote_type == 'downvote':
            self.downvotes += 1
        else:
            raise ValueError("Vote type must be 'upvote' or 'downvote'")
        db.session.commit()
    
    def get_location(self):
        """Get location information"""
        return {
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code
        }
    
    @staticmethod
    def get_stats():
        """Get incident statistics"""
        from sqlalchemy import func
        
        stats = db.session.query(
            Incident.status,
            Incident.category,
            func.count(Incident.id).label('count')
        ).group_by(Incident.status, Incident.category).all()
        
        return [
            {
                'status': stat.status,
                'category': stat.category,
                'count': stat.count
            }
            for stat in stats
        ]
    
    @staticmethod
    def find_by_location(lat, lng, radius=10):
        """Find incidents near a location"""
        # Simple distance calculation (can be improved with PostGIS)
        lat_min = lat - radius/111
        lat_max = lat + radius/111
        lng_min = lng - radius/111
        lng_max = lng + radius/111
        
        return Incident.query.filter(
            Incident.latitude.between(lat_min, lat_max),
            Incident.longitude.between(lng_min, lng_max)
        ).all()
    
    def __repr__(self):
        return f'<Incident {self.title}>' 