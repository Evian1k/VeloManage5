import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Enable CORS
    CORS(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models.user import User
    from app.models.vehicle import Vehicle
    from app.models.service import Service, Part, ServicePart
    from app.models.service_record import ServiceRecord, ServiceRecordPart, Appointment
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.services import services_bp
    from app.routes.appointments import appointments_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vehicles_bp, url_prefix='/api/vehicles')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'OK',
            'message': 'CMIS Backend is running',
            'environment': app.config['ENV']
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error', 'message': 'Something went wrong'}, 500
    
    return app 