# VeloManage CMIS Backend

A comprehensive **Civic Management Information System** backend built with **Python Flask** and **PostgreSQL**. This system enables citizens to report civic incidents and administrators to manage and resolve them efficiently.

## 🚀 Features

- **User Authentication & Authorization** - JWT-based authentication with role-based access control
- **Incident Management** - Full CRUD operations for civic incident reporting
- **Geolocation Support** - Location-based incident tracking and filtering
- **Admin Dashboard** - Comprehensive admin tools for incident management
- **Real-time Statistics** - Incident analytics and reporting
- **Voting System** - Community voting on incident importance
- **Search & Filtering** - Advanced search and filtering capabilities
- **API-First Design** - RESTful API for frontend integration

## 🛠️ Tech Stack

- **Runtime**: Python 3.8+
- **Framework**: Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT + Flask-Bcrypt
- **Validation**: Custom validators
- **Security**: Flask-CORS, Helmet
- **Testing**: pytest

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py          # App factory and configuration
│   ├── models/              # Database models
│   │   ├── user.py          # User accounts and authentication
│   │   └── incident.py      # Incident reports
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── incidents.py     # Incident management API
│   │   └── admin.py         # Admin endpoints
│   ├── utils/               # Utility functions
│   │   └── auth.py          # Auth utilities and decorators
│   ├── static/              # Uploaded files (images, etc.)
│   └── templates/           # Email templates
├── scripts/
│   └── seed.py              # Database seeding
├── tests/                   # Unit and integration tests
│   └── test_basic.py        # API endpoint tests
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (v12 or higher)
- pip or pipenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd VeloManage5/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://postgres:password@localhost:5432/velomanage_db
   
   # JWT Configuration
   JWT_SECRET_KEY=your_super_secret_jwt_key_here
   
   # Server Configuration
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   
   # CORS Configuration
   CORS_ORIGIN=http://localhost:3000
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb velomanage_db
   
   # Run database migrations and seed data
   python scripts/seed.py
   ```

6. **Start the server**
   ```bash
   # Development mode
   python run.py
   
   # Production mode
   gunicorn run:app
   ```

## 🔐 Authentication

### User Roles

- **User**: Can report incidents, view public incidents, vote
- **Admin**: Full access to all features, can manage incidents and users

### Default Admin Users

The seeding script creates these admin accounts:

| Name | Email | Username | Password |
|------|-------|----------|----------|
| Emmanuel (Lead) | emmanuel@velomanage.com | emmanuel_admin | admin123456 |
| Joyrose | joyrose@velomanage.com | joyrose_admin | admin123456 |
| Joel | joel@velomanage.com | joel_admin | admin123456 |
| Patience | patience@velomanage.com | patience_admin | admin123456 |
| Ibrahim | ibrahim@velomanage.com | ibrahim_admin | admin123456 |

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | User login | No |
| GET | `/api/auth/profile` | Get user profile | Yes |
| PUT | `/api/auth/profile` | Update profile | Yes |
| PUT | `/api/auth/change-password` | Change password | Yes |
| GET | `/api/auth/users` | Get all users (Admin) | Yes |
| PUT | `/api/auth/users/:id/role` | Update user role (Admin) | Yes |

### Incidents

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/incidents` | Get all incidents | Optional |
| GET | `/api/incidents/stats` | Get incident statistics | Optional |
| GET | `/api/incidents/:id` | Get incident by ID | Optional |
| POST | `/api/incidents` | Create new incident | Yes |
| GET | `/api/incidents/user/incidents` | Get user's incidents | Yes |
| POST | `/api/incidents/:id/vote` | Vote on incident | Yes |
| PUT | `/api/incidents/:id` | Update incident (Admin) | Yes |
| DELETE | `/api/incidents/:id` | Delete incident (Admin) | Yes |
| POST | `/api/incidents/:id/assign` | Assign incident (Admin) | Yes |

### Admin

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/dashboard` | Admin dashboard | Yes |
| PUT | `/api/admin/users/:id/toggle-status` | Toggle user status | Yes |
| PUT | `/api/admin/incidents/bulk-update` | Bulk update incidents | Yes |
| GET | `/api/admin/reports/incident-summary` | Incident summary report | Yes |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgresql://postgres:password@localhost:5432/velomanage_db |
| `JWT_SECRET_KEY` | JWT secret key | - |
| `SECRET_KEY` | Flask secret key | - |
| `FLASK_ENV` | Environment | development |
| `CORS_ORIGIN` | CORS origin | http://localhost:3000 |

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash` (Hashed)
- `first_name`
- `last_name`
- `role` (user/admin)
- `is_active`
- `last_login`
- `created_at`
- `updated_at`

### Incidents Table
- `id` (Primary Key)
- `title`
- `description`
- `category` (infrastructure/safety/environmental/traffic/public_service/other)
- `status` (open/in_progress/resolved/closed)
- `priority` (low/medium/high/critical)
- `latitude`
- `longitude`
- `address`
- `city`
- `state`
- `zip_code`
- `images` (JSON)
- `contact_info` (JSON)
- `estimated_cost`
- `estimated_timeframe`
- `reported_by` (Foreign Key to Users)
- `assigned_to` (Foreign Key to Users)
- `resolved_at`
- `resolution_notes`
- `upvotes`
- `downvotes`
- `created_at`
- `updated_at`

## 🚀 Deployment

### Render
1. Connect your GitHub repository
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn run:app`

### Railway
1. Connect your GitHub repository
2. Add PostgreSQL addon
3. Set environment variables
4. Deploy automatically

### Fly.io
1. Install flyctl
2. Run `fly launch`
3. Set secrets: `fly secrets set JWT_SECRET_KEY=your_secret`
4. Deploy: `fly deploy`

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt for password security
- **Input Validation** - Comprehensive request validation
- **CORS Protection** - Cross-origin resource sharing
- **SQL Injection Protection** - SQLAlchemy ORM protection
- **Role-based Access Control** - Admin/user permissions

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_basic.py
```

## 📊 Monitoring

- **Health Check**: `GET /health`
- **Error Handling**: Comprehensive error handling
- **Logging**: Flask logging system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

- **Emmanuel** (Lead Developer)
- **Joyrose** (Admin)
- **Joel** (Admin)
- **Patience** (Admin)
- **Ibrahim** (Admin)

## 📞 Support

For support, email: support@velomanage.com

---

**VeloManage CMIS** - Empowering communities through civic engagement technology. 