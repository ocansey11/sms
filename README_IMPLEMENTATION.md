# School Management System - Backend Implementation

This is the complete backend implementation of the School Management System built with FastAPI, PostgreSQL, and Docker.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (for local development)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd sms

# Copy environment variables
cp .env.example .env

# Edit .env with your database credentials
# At minimum, set DATABASE_URL and SECRET_KEY
```

### 2. Database Setup

#### Using Docker (Recommended)
```bash
# Start PostgreSQL with Docker Compose
docker-compose -f docker-compose.dev.yml up -d

# This will start:
# - PostgreSQL database on port 5432
# - Adminer (database UI) on port 8080
```

#### Manual Database Setup
```bash
# Create database
createdb sms_dev

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/sms_dev
```

### 3. Application Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/dev_setup.py init-db

# Create sample data (optional)
python scripts/dev_setup.py create-sample-data

# Start development server
python run_dev.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📁 Project Structure

```
sms/
├── app/
│   ├── api/
│   │   ├── dependencies.py      # Dependency injection
│   │   └── routes/
│   │       ├── admin.py         # Admin endpoints
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── guardian.py      # Guardian endpoints
│   │       ├── student.py       # Student endpoints
│   │       └── teacher.py       # Teacher endpoints
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # Security utilities
│   ├── db/
│   │   ├── crud.py             # Database operations
│   │   ├── database.py         # Database connection
│   │   ├── models.py           # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── exceptions/
│   │   └── custom_exceptions.py # Custom exceptions
│   ├── middleware/
│   │   └── custom_middleware.py # Custom middleware
│   ├── services/
│   │   ├── auth_service.py     # Authentication service
│   │   └── class_service.py    # Class management service
│   ├── utils/
│   │   ├── email_service.py    # Email utilities
│   │   └── helpers.py          # Helper functions
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── scripts/                    # Development scripts
├── docker-compose.dev.yml      # Development Docker setup
├── docker-compose.prod.yml     # Production Docker setup
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## 🔧 Development Tools

### Database Management
```bash
# Check database status
python scripts/dev_setup.py check-db

# Reset database (WARNING: Deletes all data)
python scripts/dev_setup.py reset-db

# Create sample data
python scripts/dev_setup.py create-sample-data
```

### Database Migrations
```bash
# Generate new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

## 🐳 Docker Deployment

### Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f app

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Build and start production environment
docker-compose -f docker-compose.prod.yml up -d

# Scale the application
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

## 🔐 API Authentication

### Sample Users (after running create-sample-data)
- **Admin**: admin@school.com / admin123
- **Teacher**: teacher@school.com / teacher123
- **Student**: student@school.com / student123
- **Guardian**: guardian@school.com / guardian123

### API Usage
```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@school.com", "password": "admin123"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <your-token>"
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/change-password` - Change password

### Admin
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create user
- `GET /api/admin/classes` - List all classes
- `POST /api/admin/classes` - Create class
- `GET /api/admin/analytics` - Get system analytics

### Teacher
- `GET /api/teacher/classes` - Get teacher's classes
- `POST /api/teacher/classes/{id}/students` - Enroll student
- `GET /api/teacher/quizzes` - Get teacher's quizzes
- `POST /api/teacher/quizzes` - Create quiz
- `POST /api/teacher/attendance` - Record attendance

### Student
- `GET /api/student/profile` - Get student profile
- `GET /api/student/classes` - Get enrolled classes
- `GET /api/student/quizzes` - Get available quizzes
- `POST /api/student/quizzes/{id}/attempts` - Submit quiz
- `GET /api/student/attendance` - Get attendance records

### Guardian
- `GET /api/guardian/students` - Get associated students
- `GET /api/guardian/students/{id}/classes` - Get student's classes
- `GET /api/guardian/students/{id}/attendance` - Get student's attendance
- `GET /api/guardian/students/{id}/grades` - Get student's grades

## 🚀 Production Deployment

### Environment Variables
For production, set these environment variables:
```bash
ENV=production
DEBUG=false
SECRET_KEY=<strong-secret-key>
DATABASE_URL=<production-database-url>
CORS_ORIGINS=["https://yourdomain.com"]
```

### Security Considerations
- Use strong SECRET_KEY
- Set proper CORS origins
- Use HTTPS in production
- Set up proper database backups
- Configure rate limiting
- Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed description
4. Include logs and error messages

---

**Note**: This is a complete backend implementation ready for development and production use. The frontend can be built separately using React, Vue, or any other framework that can consume REST APIs.
