from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class ServiceRecord(db.Model):
    """ServiceRecord model for tracking vehicle service history"""
    __tablename__ = 'service_records'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Service details
    service_date = db.Column(db.DateTime, nullable=False)
    mileage_at_service = db.Column(db.Integer, nullable=False)
    actual_duration = db.Column(db.Integer)  # Duration in minutes
    actual_cost = db.Column(db.Numeric(10, 2))
    labor_cost = db.Column(db.Numeric(10, 2))
    parts_cost = db.Column(db.Numeric(10, 2))
    
    # Service status
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='normal', nullable=False)  # low, normal, high, urgent
    
    # Service details
    description = db.Column(db.Text)
    work_performed = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    next_service_mileage = db.Column(db.Integer)
    next_service_date = db.Column(db.Date)
    
    # Additional information
    images = db.Column(db.JSON)  # Store before/after images
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    used_parts = db.relationship('ServiceRecordPart', backref='service_record', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(ServiceRecord, self).__init__(**kwargs)
        if not self.images:
            self.images = []
    
    def to_dict(self):
        """Convert service record to dictionary"""
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'customer_id': self.customer_id,
            'service_id': self.service_id,
            'mechanic_id': self.mechanic_id,
            'service_date': self.service_date.isoformat(),
            'mileage_at_service': self.mileage_at_service,
            'actual_duration': self.actual_duration,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'labor_cost': float(self.labor_cost) if self.labor_cost else None,
            'parts_cost': float(self.parts_cost) if self.parts_cost else None,
            'status': self.status,
            'priority': self.priority,
            'description': self.description,
            'work_performed': self.work_performed,
            'recommendations': self.recommendations,
            'next_service_mileage': self.next_service_mileage,
            'next_service_date': self.next_service_date.isoformat() if self.next_service_date else None,
            'images': self.images,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'customer': self.customer.to_dict() if self.customer else None,
            'service_type': self.service_type.to_dict() if self.service_type else None,
            'mechanic': self.mechanic.to_dict() if self.mechanic else None,
            'used_parts': [part.to_dict() for part in self.used_parts]
        }
    
    def mark_completed(self, mechanic_id=None, work_performed=None, actual_cost=None):
        """Mark service as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        if mechanic_id:
            self.mechanic_id = mechanic_id
        if work_performed:
            self.work_performed = work_performed
        if actual_cost:
            self.actual_cost = actual_cost
        db.session.commit()
    
    def calculate_total_cost(self):
        """Calculate total cost including parts"""
        total = 0
        if self.labor_cost:
            total += float(self.labor_cost)
        if self.parts_cost:
            total += float(self.parts_cost)
        return total
    
    @staticmethod
    def get_by_vehicle(vehicle_id):
        """Get service records for a vehicle"""
        return ServiceRecord.query.filter_by(vehicle_id=vehicle_id).order_by(ServiceRecord.service_date.desc()).all()
    
    @staticmethod
    def get_by_customer(customer_id):
        """Get service records for a customer"""
        return ServiceRecord.query.filter_by(customer_id=customer_id).order_by(ServiceRecord.service_date.desc()).all()
    
    def __repr__(self):
        return f'<ServiceRecord {self.id} - {self.vehicle.get_full_name()}>'

class ServiceRecordPart(db.Model):
    """ServiceRecordPart model for tracking parts used in service"""
    __tablename__ = 'service_record_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    service_record_id = db.Column(db.Integer, db.ForeignKey('service_records.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))
    
    def to_dict(self):
        """Convert service record part to dictionary"""
        return {
            'id': self.id,
            'service_record_id': self.service_record_id,
            'part_id': self.part_id,
            'quantity_used': self.quantity_used,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'part': self.part.to_dict() if self.part else None
        }
    
    def __repr__(self):
        return f'<ServiceRecordPart {self.part.name} x{self.quantity_used}>'

class Appointment(db.Model):
    """Appointment model for scheduling service appointments"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Appointment details
    appointment_date = db.Column(db.DateTime, nullable=False)
    estimated_duration = db.Column(db.Integer)  # Duration in minutes
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, confirmed, in_progress, completed, cancelled
    
    # Additional information
    description = db.Column(db.Text)
    special_requests = db.Column(db.Text)
    customer_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'vehicle_id': self.vehicle_id,
            'service_id': self.service_id,
            'mechanic_id': self.mechanic_id,
            'appointment_date': self.appointment_date.isoformat(),
            'estimated_duration': self.estimated_duration,
            'status': self.status,
            'description': self.description,
            'special_requests': self.special_requests,
            'customer_notes': self.customer_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'customer': self.customer.to_dict() if self.customer else None,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'service': self.service.to_dict() if self.service else None,
            'mechanic': self.mechanic.to_dict() if self.mechanic else None
        }
    
    def confirm(self, mechanic_id=None):
        """Confirm appointment"""
        self.status = 'confirmed'
        if mechanic_id:
            self.mechanic_id = mechanic_id
        db.session.commit()
    
    def start_service(self):
        """Start service appointment"""
        self.status = 'in_progress'
        db.session.commit()
    
    def complete(self):
        """Complete appointment"""
        self.status = 'completed'
        db.session.commit()
    
    def cancel(self):
        """Cancel appointment"""
        self.status = 'cancelled'
        db.session.commit()
    
    @staticmethod
    def get_by_date_range(start_date, end_date):
        """Get appointments within a date range"""
        return Appointment.query.filter(
            Appointment.appointment_date.between(start_date, end_date)
        ).order_by(Appointment.appointment_date).all()
    
    @staticmethod
    def get_by_customer(customer_id):
        """Get appointments for a customer"""
        return Appointment.query.filter_by(customer_id=customer_id).order_by(Appointment.appointment_date.desc()).all()
    
    @staticmethod
    def get_by_mechanic(mechanic_id):
        """Get appointments for a mechanic"""
        return Appointment.query.filter_by(mechanic_id=mechanic_id).order_by(Appointment.appointment_date).all()
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_date}>'