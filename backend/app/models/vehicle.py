from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Vehicle(db.Model):
    """Vehicle model for CMIS car inventory management"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)  # Vehicle Identification Number
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30))
    mileage = db.Column(db.Integer, default=0)
    fuel_type = db.Column(db.String(20))  # gasoline, diesel, electric, hybrid
    transmission = db.Column(db.String(20))  # manual, automatic, cvt
    engine_size = db.Column(db.String(20))
    license_plate = db.Column(db.String(20))
    registration_expiry = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date)
    
    # Status and availability
    status = db.Column(db.String(20), default='available', nullable=False)  # available, in_service, sold, maintenance
    location = db.Column(db.String(100))  # Where the vehicle is currently located
    
    # Financial information
    purchase_price = db.Column(db.Numeric(12, 2))
    current_value = db.Column(db.Numeric(12, 2))
    sale_price = db.Column(db.Numeric(12, 2))
    
    # Ownership
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_company_owned = db.Column(db.Boolean, default=False)
    
    # Additional details
    features = db.Column(db.JSON)  # Store vehicle features
    images = db.Column(db.JSON)  # Store image URLs
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_records = db.relationship('ServiceRecord', backref='vehicle', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='vehicle', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Vehicle, self).__init__(**kwargs)
        if not self.features:
            self.features = []
        if not self.images:
            self.images = []
    
    def to_dict(self):
        """Convert vehicle to dictionary"""
        return {
            'id': self.id,
            'vin': self.vin,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'engine_size': self.engine_size,
            'license_plate': self.license_plate,
            'registration_expiry': self.registration_expiry.isoformat() if self.registration_expiry else None,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'status': self.status,
            'location': self.location,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'current_value': float(self.current_value) if self.current_value else None,
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'owner_id': self.owner_id,
            'is_company_owned': self.is_company_owned,
            'features': self.features,
            'images': self.images,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'owner': self.owner.to_dict() if self.owner else None
        }
    
    def update_mileage(self, new_mileage):
        """Update vehicle mileage"""
        self.mileage = new_mileage
        db.session.commit()
    
    def change_status(self, new_status):
        """Change vehicle status"""
        self.status = new_status
        db.session.commit()
    
    def get_full_name(self):
        """Get full vehicle name"""
        return f"{self.year} {self.make} {self.model}"
    
    def is_due_for_service(self, service_mileage=3000):
        """Check if vehicle is due for service"""
        last_service = self.service_records.order_by(ServiceRecord.service_date.desc()).first()
        if last_service:
            return (self.mileage - last_service.mileage_at_service) >= service_mileage
        return self.mileage >= service_mileage
    
    @staticmethod
    def find_by_vin(vin):
        """Find vehicle by VIN"""
        return Vehicle.query.filter_by(vin=vin).first()
    
    @staticmethod
    def find_by_status(status):
        """Find vehicles by status"""
        return Vehicle.query.filter_by(status=status).all()
    
    def __repr__(self):
        return f'<Vehicle {self.get_full_name()}>'