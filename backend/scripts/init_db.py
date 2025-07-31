#!/usr/bin/env python3
"""
Database initialization script for CMIS
Creates tables and populates with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.service import Service, Part, ServicePart
from app.models.service_record import ServiceRecord, ServiceRecordPart, Appointment
from datetime import datetime, timedelta
from decimal import Decimal

def init_database():
    """Initialize database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create sample users
        print("Creating sample users...")
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@cmis.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            phone='555-0001',
            address='123 Admin St, City, State 12345'
        )
        db.session.add(admin)
        
        # Mechanic users
        mechanic1 = User(
            username='john_mechanic',
            email='john@cmis.com',
            password='mechanic123',
            first_name='John',
            last_name='Smith',
            role='mechanic',
            phone='555-0002',
            address='456 Mechanic Ave, City, State 12345'
        )
        db.session.add(mechanic1)
        
        mechanic2 = User(
            username='sarah_mechanic',
            email='sarah@cmis.com',
            password='mechanic123',
            first_name='Sarah',
            last_name='Johnson',
            role='mechanic',
            phone='555-0003',
            address='789 Mechanic Blvd, City, State 12345'
        )
        db.session.add(mechanic2)
        
        # Customer users
        customer1 = User(
            username='mike_customer',
            email='mike@cmis.com',
            password='customer123',
            first_name='Mike',
            last_name='Davis',
            role='customer',
            phone='555-0004',
            address='321 Customer Dr, City, State 12345'
        )
        db.session.add(customer1)
        
        customer2 = User(
            username='lisa_customer',
            email='lisa@cmis.com',
            password='customer123',
            first_name='Lisa',
            last_name='Wilson',
            role='customer',
            phone='555-0005',
            address='654 Customer Ln, City, State 12345'
        )
        db.session.add(customer2)
        
        db.session.commit()
        
        # Create sample services
        print("Creating sample services...")
        
        services = [
            Service(
                name='Oil Change',
                description='Complete oil change service including filter replacement',
                category='maintenance',
                estimated_duration=60,
                estimated_cost=Decimal('45.00'),
                mileage_interval=3000
            ),
            Service(
                name='Brake Repair',
                description='Complete brake system inspection and repair',
                category='repair',
                estimated_duration=120,
                estimated_cost=Decimal('150.00'),
                mileage_interval=None
            ),
            Service(
                name='Tire Rotation',
                description='Rotate and balance all four tires',
                category='maintenance',
                estimated_duration=45,
                estimated_cost=Decimal('35.00'),
                mileage_interval=6000
            ),
            Service(
                name='Air Filter Replacement',
                description='Replace engine air filter',
                category='maintenance',
                estimated_duration=30,
                estimated_cost=Decimal('25.00'),
                mileage_interval=15000
            ),
            Service(
                name='Battery Replacement',
                description='Replace vehicle battery',
                category='repair',
                estimated_duration=45,
                estimated_cost=Decimal('120.00'),
                mileage_interval=None
            ),
            Service(
                name='3000km Service',
                description='Complete 3000km maintenance service',
                category='maintenance',
                estimated_duration=90,
                estimated_cost=Decimal('85.00'),
                mileage_interval=3000
            )
        ]
        
        for service in services:
            db.session.add(service)
        
        db.session.commit()
        
        # Create sample parts
        print("Creating sample parts...")
        
        parts = [
            Part(
                name='Oil Filter',
                part_number='OF-001',
                description='High-quality oil filter for most vehicles',
                category='engine',
                manufacturer='FilterPro',
                unit_cost=Decimal('8.50'),
                stock_quantity=50,
                min_stock_level=10
            ),
            Part(
                name='Brake Pads',
                part_number='BP-001',
                description='Ceramic brake pads for front wheels',
                category='brakes',
                manufacturer='BrakeMax',
                unit_cost=Decimal('45.00'),
                stock_quantity=25,
                min_stock_level=5
            ),
            Part(
                name='Air Filter',
                part_number='AF-001',
                description='Engine air filter replacement',
                category='engine',
                manufacturer='AirFlow',
                unit_cost=Decimal('15.00'),
                stock_quantity=30,
                min_stock_level=8
            ),
            Part(
                name='Battery',
                part_number='BAT-001',
                description='12V automotive battery',
                category='electrical',
                manufacturer='PowerCell',
                unit_cost=Decimal('95.00'),
                stock_quantity=10,
                min_stock_level=3
            ),
            Part(
                name='Motor Oil',
                part_number='MO-001',
                description='5W-30 synthetic motor oil',
                category='engine',
                manufacturer='OilMax',
                unit_cost=Decimal('12.00'),
                stock_quantity=100,
                min_stock_level=20
            )
        ]
        
        for part in parts:
            db.session.add(part)
        
        db.session.commit()
        
        # Create service-part relationships
        print("Creating service-part relationships...")
        
        # Oil Change parts
        oil_change = Service.query.filter_by(name='Oil Change').first()
        oil_filter = Part.query.filter_by(part_number='OF-001').first()
        motor_oil = Part.query.filter_by(part_number='MO-001').first()
        
        ServicePart(service_id=oil_change.id, part_id=oil_filter.id, quantity_required=1)
        ServicePart(service_id=oil_change.id, part_id=motor_oil.id, quantity_required=5)
        
        # Brake Repair parts
        brake_repair = Service.query.filter_by(name='Brake Repair').first()
        brake_pads = Part.query.filter_by(part_number='BP-001').first()
        
        ServicePart(service_id=brake_repair.id, part_id=brake_pads.id, quantity_required=2)
        
        # Air Filter Replacement parts
        air_filter_service = Service.query.filter_by(name='Air Filter Replacement').first()
        air_filter = Part.query.filter_by(part_number='AF-001').first()
        
        ServicePart(service_id=air_filter_service.id, part_id=air_filter.id, quantity_required=1)
        
        # Battery Replacement parts
        battery_service = Service.query.filter_by(name='Battery Replacement').first()
        battery = Part.query.filter_by(part_number='BAT-001').first()
        
        ServicePart(service_id=battery_service.id, part_id=battery.id, quantity_required=1)
        
        db.session.commit()
        
        # Create sample vehicles
        print("Creating sample vehicles...")
        
        vehicles = [
            Vehicle(
                vin='1HGBH41JXMN109186',
                make='Honda',
                model='Civic',
                year=2020,
                color='Blue',
                mileage=15000,
                fuel_type='gasoline',
                transmission='automatic',
                engine_size='1.5L',
                license_plate='ABC123',
                registration_expiry=datetime.now().date() + timedelta(days=180),
                insurance_expiry=datetime.now().date() + timedelta(days=90),
                status='available',
                location='Main Garage',
                purchase_price=Decimal('18000.00'),
                current_value=Decimal('16000.00'),
                owner_id=customer1.id,
                is_company_owned=False
            ),
            Vehicle(
                vin='2T1BURHE0JC123456',
                make='Toyota',
                model='Camry',
                year=2019,
                color='Silver',
                mileage=25000,
                fuel_type='gasoline',
                transmission='automatic',
                engine_size='2.5L',
                license_plate='XYZ789',
                registration_expiry=datetime.now().date() + timedelta(days=120),
                insurance_expiry=datetime.now().date() + timedelta(days=60),
                status='in_service',
                location='Service Bay 1',
                purchase_price=Decimal('22000.00'),
                current_value=Decimal('19000.00'),
                owner_id=customer2.id,
                is_company_owned=False
            ),
            Vehicle(
                vin='3VWDX7AJ5DM123789',
                make='Volkswagen',
                model='Jetta',
                year=2021,
                color='White',
                mileage=8000,
                fuel_type='gasoline',
                transmission='manual',
                engine_size='1.4L',
                license_plate='DEF456',
                registration_expiry=datetime.now().date() + timedelta(days=365),
                insurance_expiry=datetime.now().date() + timedelta(days=365),
                status='available',
                location='Main Garage',
                purchase_price=Decimal('20000.00'),
                current_value=Decimal('18500.00'),
                owner_id=customer1.id,
                is_company_owned=False
            )
        ]
        
        for vehicle in vehicles:
            db.session.add(vehicle)
        
        db.session.commit()
        
        # Create sample service records
        print("Creating sample service records...")
        
        service_records = [
            ServiceRecord(
                vehicle_id=vehicles[0].id,
                customer_id=customer1.id,
                service_id=oil_change.id,
                mechanic_id=mechanic1.id,
                service_date=datetime.now() - timedelta(days=30),
                mileage_at_service=12000,
                actual_duration=60,
                actual_cost=Decimal('45.00'),
                labor_cost=Decimal('30.00'),
                parts_cost=Decimal('15.00'),
                status='completed',
                priority='normal',
                description='Regular oil change service',
                work_performed='Changed oil and filter, topped off fluids',
                recommendations='Next service due at 15,000 miles',
                next_service_mileage=15000,
                next_service_date=datetime.now().date() + timedelta(days=60)
            ),
            ServiceRecord(
                vehicle_id=vehicles[1].id,
                customer_id=customer2.id,
                service_id=brake_repair.id,
                mechanic_id=mechanic2.id,
                service_date=datetime.now() - timedelta(days=7),
                mileage_at_service=24000,
                actual_duration=120,
                actual_cost=Decimal('180.00'),
                labor_cost=Decimal('90.00'),
                parts_cost=Decimal('90.00'),
                status='completed',
                priority='high',
                description='Brake pad replacement',
                work_performed='Replaced front brake pads, inspected brake system',
                recommendations='Monitor brake performance, next inspection in 6 months',
                next_service_mileage=30000
            )
        ]
        
        for record in service_records:
            db.session.add(record)
        
        db.session.commit()
        
        # Create sample appointments
        print("Creating sample appointments...")
        
        appointments = [
            Appointment(
                customer_id=customer1.id,
                vehicle_id=vehicles[0].id,
                service_id=air_filter_service.id,
                mechanic_id=mechanic1.id,
                appointment_date=datetime.now() + timedelta(days=3),
                estimated_duration=30,
                status='confirmed',
                description='Air filter replacement appointment',
                special_requests='Please check cabin air filter as well'
            ),
            Appointment(
                customer_id=customer2.id,
                vehicle_id=vehicles[1].id,
                service_id=oil_change.id,
                mechanic_id=mechanic2.id,
                appointment_date=datetime.now() + timedelta(days=5),
                estimated_duration=60,
                status='scheduled',
                description='Oil change and inspection'
            )
        ]
        
        for appointment in appointments:
            db.session.add(appointment)
        
        db.session.commit()
        
        print("Database initialization completed successfully!")
        print("\nSample data created:")
        print(f"- {User.query.count()} users")
        print(f"- {Vehicle.query.count()} vehicles")
        print(f"- {Service.query.count()} services")
        print(f"- {Part.query.count()} parts")
        print(f"- {ServiceRecord.query.count()} service records")
        print(f"- {Appointment.query.count()} appointments")
        print("\nDefault admin credentials:")
        print("Email: admin@cmis.com")
        print("Password: admin123")

if __name__ == '__main__':
    init_database()