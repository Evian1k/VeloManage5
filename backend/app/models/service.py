from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Service(db.Model):
    """Service model for defining available service types"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # maintenance, repair, inspection, emergency
    estimated_duration = db.Column(db.Integer)  # Duration in minutes
    estimated_cost = db.Column(db.Numeric(10, 2))
    mileage_interval = db.Column(db.Integer)  # Service interval in miles
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_parts = db.relationship('ServicePart', backref='service', lazy='dynamic')
    service_records = db.relationship('ServiceRecord', backref='service_type', lazy='dynamic')
    
    def to_dict(self):
        """Convert service to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'estimated_duration': self.estimated_duration,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'mileage_interval': self.mileage_interval,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'parts': [part.to_dict() for part in self.service_parts]
        }
    
    @staticmethod
    def get_active_services():
        """Get all active services"""
        return Service.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_by_category(category):
        """Get services by category"""
        return Service.query.filter_by(category=category, is_active=True).all()
    
    def __repr__(self):
        return f'<Service {self.name}>'

class Part(db.Model):
    """Part model for tracking service parts"""
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # engine, transmission, brakes, electrical, etc.
    manufacturer = db.Column(db.String(100))
    unit_cost = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_parts = db.relationship('ServicePart', backref='part', lazy='dynamic')
    
    def to_dict(self):
        """Convert part to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'part_number': self.part_number,
            'description': self.description,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'stock_quantity': self.stock_quantity,
            'min_stock_level': self.min_stock_level,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_stock(self, quantity):
        """Update stock quantity"""
        self.stock_quantity = max(0, self.stock_quantity + quantity)
        db.session.commit()
    
    def is_low_stock(self):
        """Check if part is low on stock"""
        return self.stock_quantity <= self.min_stock_level
    
    @staticmethod
    def get_low_stock_parts():
        """Get all parts with low stock"""
        return Part.query.filter(
            Part.stock_quantity <= Part.min_stock_level,
            Part.is_active == True
        ).all()
    
    def __repr__(self):
        return f'<Part {self.name}>'

class ServicePart(db.Model):
    """ServicePart model for linking services with required parts"""
    __tablename__ = 'service_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity_required = db.Column(db.Integer, default=1, nullable=False)
    is_optional = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert service part to dictionary"""
        return {
            'id': self.id,
            'service_id': self.service_id,
            'part_id': self.part_id,
            'quantity_required': self.quantity_required,
            'is_optional': self.is_optional,
            'part': self.part.to_dict() if self.part else None
        }
    
    def __repr__(self):
        return f'<ServicePart {self.service.name} - {self.part.name}>'