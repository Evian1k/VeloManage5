#!/usr/bin/env python3
"""
Database seeding script for VeloManage CMIS
Creates initial admin users and sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.incident import Incident
from datetime import datetime

def seed_database():
    """Seed the database with initial data"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("🌱 Starting database seeding...")
            
            # Create tables
            db.create_all()
            print("✅ Database tables created")
            
            # Admin users to create
            admin_users = [
                {
                    'username': 'emmanuel_admin',
                    'email': 'emmanuel@velomanage.com',
                    'password': 'admin123456',
                    'first_name': 'Emmanuel',
                    'last_name': 'Lead',
                    'role': 'admin',
                    'is_active': True
                },
                {
                    'username': 'joyrose_admin',
                    'email': 'joyrose@velomanage.com',
                    'password': 'admin123456',
                    'first_name': 'Joyrose',
                    'last_name': 'Admin',
                    'role': 'admin',
                    'is_active': True
                },
                {
                    'username': 'joel_admin',
                    'email': 'joel@velomanage.com',
                    'password': 'admin123456',
                    'first_name': 'Joel',
                    'last_name': 'Admin',
                    'role': 'admin',
                    'is_active': True
                },
                {
                    'username': 'patience_admin',
                    'email': 'patience@velomanage.com',
                    'password': 'admin123456',
                    'first_name': 'Patience',
                    'last_name': 'Admin',
                    'role': 'admin',
                    'is_active': True
                },
                {
                    'username': 'ibrahim_admin',
                    'email': 'ibrahim@velomanage.com',
                    'password': 'admin123456',
                    'first_name': 'Ibrahim',
                    'last_name': 'Admin',
                    'role': 'admin',
                    'is_active': True
                }
            ]
            
            # Create admin users
            print("👥 Creating admin users...")
            created_admins = []
            for admin_data in admin_users:
                existing_user = User.find_by_email(admin_data['email'])
                if not existing_user:
                    user = User(**admin_data)
                    db.session.add(user)
                    created_admins.append(user)
                    print(f"✅ Created admin: {admin_data['first_name']} {admin_data['last_name']}")
                else:
                    print(f"⚠️  Admin already exists: {admin_data['first_name']} {admin_data['last_name']}")
            
            db.session.commit()
            
            # Create sample incidents
            print("📝 Creating sample incidents...")
            if created_admins:
                first_admin = created_admins[0]
                
                sample_incidents = [
                    {
                        'title': 'Pothole on Main Street',
                        'description': 'Large pothole causing traffic issues and potential damage to vehicles. Located near the intersection of Main Street and Oak Avenue.',
                        'category': 'infrastructure',
                        'priority': 'high',
                        'status': 'open',
                        'latitude': 40.7128,
                        'longitude': -74.0060,
                        'address': '123 Main Street',
                        'city': 'New York',
                        'state': 'NY',
                        'zip_code': '10001',
                        'reported_by': first_admin.id
                    },
                    {
                        'title': 'Broken Street Light',
                        'description': 'Street light not working on Elm Street. Creates safety concerns for pedestrians at night.',
                        'category': 'safety',
                        'priority': 'medium',
                        'status': 'in_progress',
                        'latitude': 40.7589,
                        'longitude': -73.9851,
                        'address': '456 Elm Street',
                        'city': 'New York',
                        'state': 'NY',
                        'zip_code': '10002',
                        'reported_by': first_admin.id
                    },
                    {
                        'title': 'Garbage Overflow',
                        'description': 'Public trash bins overflowing with garbage. Need immediate attention to prevent littering.',
                        'category': 'environmental',
                        'priority': 'medium',
                        'status': 'open',
                        'latitude': 40.7505,
                        'longitude': -73.9934,
                        'address': '789 Park Avenue',
                        'city': 'New York',
                        'state': 'NY',
                        'zip_code': '10003',
                        'reported_by': first_admin.id
                    },
                    {
                        'title': 'Traffic Signal Malfunction',
                        'description': 'Traffic light at 5th Avenue and 42nd Street is not working properly. Causing traffic congestion.',
                        'category': 'traffic',
                        'priority': 'critical',
                        'status': 'open',
                        'latitude': 40.7589,
                        'longitude': -73.9851,
                        'address': '5th Avenue and 42nd Street',
                        'city': 'New York',
                        'state': 'NY',
                        'zip_code': '10018',
                        'reported_by': first_admin.id
                    },
                    {
                        'title': 'Public Bench Damaged',
                        'description': 'Wooden bench in Central Park is broken and unsafe for use. Needs replacement.',
                        'category': 'public_service',
                        'priority': 'low',
                        'status': 'open',
                        'latitude': 40.7829,
                        'longitude': -73.9654,
                        'address': 'Central Park',
                        'city': 'New York',
                        'state': 'NY',
                        'zip_code': '10024',
                        'reported_by': first_admin.id
                    }
                ]
                
                for incident_data in sample_incidents:
                    incident = Incident(**incident_data)
                    db.session.add(incident)
                    print(f"✅ Created incident: {incident_data['title']}")
                
                db.session.commit()
            
            print("\n🎉 Database seeding completed successfully!")
            print("\n📋 Admin Login Credentials:")
            print("Email: emmanuel@velomanage.com")
            print("Password: admin123456")
            print("\n🔗 API Endpoints:")
            print("POST /api/auth/login - User login")
            print("POST /api/auth/register - User registration")
            print("GET /api/incidents - Get all incidents")
            print("POST /api/incidents - Create new incident")
            print("GET /api/admin/dashboard - Admin dashboard")
            
        except Exception as e:
            print(f"❌ Database seeding failed: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    seed_database() 