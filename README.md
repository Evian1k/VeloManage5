# CMIS - Car Management Information System

A comprehensive car management and service tracking system built with React (Frontend) and Flask (Backend).

## Features

### MVP Features
- ✅ User authentication and authorization (Customer, Mechanic, Admin roles)
- ✅ Vehicle management (add, edit, delete, search)
- ✅ Service tracking and history
- ✅ Appointment scheduling and management
- ✅ Service reminders (3000km service)
- ✅ Parts inventory management
- ✅ Admin dashboard with analytics
- ✅ Mobile-friendly responsive design

### New Features
- ✅ Service offerings (Brake repair, 3000km service, etc.)
- ✅ Appointment booking system
- ✅ Regular service reminders
- ✅ Parts tracking for services
- ✅ Real-time notifications
- ✅ Google Maps integration (ready for implementation)

## Tech Stack

### Backend
- **Framework**: Flask
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Bcrypt
- **CORS**: Flask-CORS
- **Testing**: pytest

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State Management**: React Context API
- **Routing**: React Router DOM
- **HTTP Client**: Axios

## Project Structure

```
cmis/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── vehicle.py
│   │   │   ├── service.py
│   │   │   └── service_record.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── vehicles.py
│   │   │   ├── services.py
│   │   │   ├── appointments.py
│   │   │   └── admin.py
│   │   └── __init__.py
│   ├── scripts/
│   │   └── init_db.py
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
├── src/
│   ├── components/
│   │   └── Navbar.jsx
│   ├── contexts/
│   │   ├── AuthContext.jsx
│   │   └── ToastContext.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Dashboard.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── vehicleService.js
│   │   ├── serviceService.js
│   │   └── appointmentService.js
│   └── App.jsx
├── package.json
└── README.md
```

## Database Models

### User
- Authentication and role management
- Customer, Mechanic, Admin roles
- Profile information

### Vehicle
- Complete vehicle details (VIN, make, model, year, etc.)
- Service history tracking
- Status management (available, in_service, maintenance)
- Mileage tracking

### Service
- Service type definitions
- Estimated costs and duration
- Required parts mapping
- Mileage intervals

### ServiceRecord
- Service history tracking
- Work performed documentation
- Cost tracking (labor, parts)
- Mechanic assignment

### Appointment
- Scheduling system
- Status tracking (scheduled, confirmed, in_progress, completed)
- Customer and mechanic assignment

### Part
- Inventory management
- Stock level tracking
- Cost tracking
- Manufacturer information

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Vehicles
- `GET /api/vehicles` - Get user vehicles
- `POST /api/vehicles` - Create vehicle
- `GET /api/vehicles/:id` - Get vehicle details
- `PUT /api/vehicles/:id` - Update vehicle
- `DELETE /api/vehicles/:id` - Delete vehicle
- `GET /api/vehicles/:id/service-history` - Get service history
- `GET /api/vehicles/:id/service-reminder` - Check service due

### Services
- `GET /api/services/services` - Get available services
- `GET /api/services/parts` - Get parts inventory
- `GET /api/services/service-records` - Get service records
- `POST /api/services/service-records` - Create service record

### Appointments
- `GET /api/appointments` - Get appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/:id/confirm` - Confirm appointment
- `PUT /api/appointments/:id/start` - Start appointment
- `PUT /api/appointments/:id/complete` - Complete appointment
- `GET /api/appointments/available-slots` - Get available time slots

### Admin
- `GET /api/admin/dashboard` - Admin dashboard stats
- `GET /api/admin/users` - Get all users
- `GET /api/admin/vehicles` - Get all vehicles
- `GET /api/admin/reports/service-summary` - Service summary report

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cmis
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database and secret settings
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb cmis_db
   
   # Initialize database with sample data
   python scripts/init_db.py
   ```

5. **Run the backend**
   ```bash
   python run.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd ../src
   npm install
   ```

2. **Configure environment variables**
   ```bash
   # Create .env file
   VITE_API_URL=http://localhost:5000/api
   ```

3. **Run the frontend**
   ```bash
   npm run dev
   ```

## Default Credentials

After running the database initialization script, you can use these default accounts:

### Admin
- Email: admin@cmis.com
- Password: admin123

### Customer
- Email: mike@cmis.com
- Password: customer123

### Mechanic
- Email: john@cmis.com
- Password: mechanic123

## Features in Detail

### Vehicle Management
- Add vehicles with complete details (VIN, make, model, year, etc.)
- Track vehicle status (available, in_service, maintenance)
- Monitor mileage and service intervals
- View service history for each vehicle

### Service Tracking
- Predefined service types (Oil Change, Brake Repair, 3000km Service, etc.)
- Automatic service reminders based on mileage
- Parts tracking for each service
- Cost tracking (labor and parts)

### Appointment System
- Book appointments with available time slots
- Appointment status tracking
- Mechanic assignment
- Service completion tracking

### Admin Dashboard
- Overview statistics
- User management
- Vehicle inventory management
- Service reports and analytics
- Parts inventory management

### Mobile-Friendly Design
- Responsive design for all screen sizes
- Touch-friendly interface
- Mobile-optimized navigation

## Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd src
npm test
```

## Deployment

### Backend Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run database migrations
5. Start with Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 run:app`

### Frontend Deployment
1. Build the project: `npm run build`
2. Deploy the `dist` folder to your web server
3. Configure API URL in environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team.
