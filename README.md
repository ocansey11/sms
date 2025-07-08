# School Management System (SMS)

A comprehensive school management system built with FastAPI (backend) and Next.js (frontend), featuring role-based authentication, quiz management, and progress tracking.

## 🏗️ Project Structure

```
sms/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   │   ├── dependencies.py
│   │   └── routes/        # Route modules by role
│   ├── core/              # Core configuration
│   ├── db/                # Database models, schemas, CRUD
│   └── utils/             # Utility functions
├── web/                   # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js 13+ app router
│   │   ├── components/    # Reusable React components
│   │   ├── contexts/      # React contexts
│   │   └── lib/           # Utility libraries
│   ├── public/            # Static assets
│   └── package.json
├── tests/                 # All test files organized by type
│   ├── integration/       # Integration tests
│   ├── frontend/          # Frontend tests
│   └── scripts/           # Test scripts
├── scripts/               # Deployment and utility scripts
├── alembic/               # Database migrations
├── docker-compose.dev.yml # Development environment
├── docker-compose.prod.yml # Production environment
├── start-dev.bat          # Windows development starter
├── start-prod.bat         # Windows production starter
└── README.md              # This file


## 🚀 Features

### Current Implementation Status

#### ✅ Backend (FastAPI)
- [x] User authentication (JWT)
- [x] Role-based access control (Teacher, Student, Guardian)
- [x] Database models (PostgreSQL)
- [x] API endpoints for all user types
- [x] Quiz management system
- [x] Progress tracking
- [x] Docker configuration
- [x] Comprehensive test data

#### ✅ Frontend (Next.js)
- [x] Next.js 15 with App Router
- [x] TypeScript configuration
- [x] Tailwind CSS styling
- [x] Authentication context
- [x] API client setup
- [x] Landing page
- [x] Login page with demo credentials
- [x] **Authentication flow working**
- [x] **Role-based access control (RBAC)**
- [x] **Permission system implementation**
- [x] Teacher dashboard
- [x] Student dashboard
- [x] Guardian dashboard
- [x] Quiz taking interface
- [x] Student quiz list
- [x] **Docker configuration for frontend**
- [x] **Full containerized development environment**

#### ✅ Permission System & RBAC
- [x] **Role-based access control (RBAC) fully implemented**
- [x] **Permission system with granular controls**
- [x] **PermissionGuard component for UI access control**
- [x] **Teachers can only create quizzes, not classes (enforced)**
- [x] **Admin-only class creation (enforced)**
- [x] **All dashboards respect user roles**

#### 🔄 In Progress
- [ ] Quiz results page
- [ ] Teacher quiz creation workflow
- [ ] Progress reports
- [ ] Guardian-student linking
- [ ] Error boundaries
- [ ] Loading states
- [ ] Mobile responsiveness

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Docker** - Containerization

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Query** - Server state management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client
- **Lucide React** - Icons

## 🐳 Development Setup

### Prerequisites
- Docker & Docker Compose

### Quick Start (Containerized - Recommended)

1. **Clone and navigate to project:**
   ```bash
   cd sms
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env.development
   # Edit .env.development with your settings
   ```

3. **Start the entire development environment:**
   ```bash
   # Option 1: Use convenience script
   ./start-dev.sh    # Linux/macOS
   start-dev.bat     # Windows
   
   # Option 2: Direct docker-compose command
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Load test data:**
   ```bash
   # Access the PostgreSQL container
   docker exec -it sms_postgres psql -U postgres -d sms_dev
   # Run the test data scripts
   \i scripts/complete_sample_data.sql
   ```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8080 (Adminer)

### Alternative: Local Development

If you prefer to run the frontend locally while using Docker for the backend:

1. **Start backend services only:**
   ```bash
   docker-compose -f docker-compose.dev.yml up postgres app adminer
   ```

2. **Run frontend locally:**
   ```bash
   cd web
   npm install
   npm run dev
   ```

## 🔐 Role-Based Access Control (RBAC)

### Permission System
The system implements a comprehensive permission system with granular access control:

#### Admin Permissions
- Create, edit, delete classes
- Create, edit, delete quizzes
- Manage users (create, update, deactivate)
- View all student progress
- Enroll students in classes
- Grade quizzes
- Full system access

#### Teacher Permissions
- **Create quizzes only** (NOT classes)
- Edit and delete own quizzes
- View student progress in their classes
- Grade quizzes for their classes
- Access only assigned classes

#### Student Permissions
- View own progress
- Take assigned quizzes
- View quiz results
- Access enrolled classes only

#### Guardian Permissions
- View linked children's progress
- Communicate with teachers
- View children's quiz results

### Implementation Details
- **Frontend**: `PermissionGuard` component controls UI visibility
- **Backend**: Route-level permission checking with `require_admin`, `require_teacher`, etc.
- **Database**: Proper foreign key relationships ensure data access control

### Example: Teacher Sarah Johnson
- ✅ Can create quizzes for her classes
- ✅ Can grade student submissions
- ✅ Can view student progress
- ❌ **Cannot create new classes** (admin-only)
- ❌ Cannot manage other teachers' content
- ❌ Cannot access admin functions

## 🐳 Docker Configuration

### Current Status
- **Backend**: ✅ Fully Dockerized with PostgreSQL
- **Frontend**: ⏳ Currently runs in development mode (npm run dev)
- **Database**: ✅ PostgreSQL container with persistent storage
- **Admin Tools**: ✅ Adminer container for database management

### Frontend Dockerization
The frontend is **not currently Dockerized** by design for development flexibility. To add Docker support:

1. **Create `web/Dockerfile`:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

2. **Update `docker-compose.dev.yml`:**
```yaml
  web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - app
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Why Frontend Isn't Dockerized Yet
- **Development Speed**: Direct npm commands are faster for development
- **Hot Reload**: Better development experience with file watching
- **Debugging**: Easier to debug TypeScript/React issues
- **Flexibility**: Can easily switch Node versions or dependencies

### Future Dockerization Plans
- Add production-ready frontend Docker configuration
- Multi-stage builds for optimized production images
- Kubernetes deployment configurations
- CI/CD pipeline integration

## 🎯 Demo Credentials

### Teacher
- **Email**: teacher@schoolsms.com
- **Password**: teacher123
- **Name**: Sarah Johnson
- **Permissions**: Quiz creation, student progress, grading
- **Restrictions**: Cannot create classes (admin-only function)

### Students
- **Emma Smith**: emma.smith@student.schoolsms.com / student123
- **Noah Jones**: noah.jones@student.schoolsms.com / student123
- **Features**: Quiz taking, progress tracking, results viewing

### Guardians
- **John Smith**: john.smith@email.com / guardian123
- **Mary Jones**: mary.jones@email.com / guardian123
- **Features**: Child progress monitoring, communication

## 📊 Database Schema

### Core Tables
- `users` - User accounts with roles
- `classes` - Course/subject classes
- `enrollments` - Student-class relationships
- `quizzes` - Quiz definitions
- `quiz_questions` - Individual quiz questions
- `quiz_attempts` - Student quiz attempts
- `quiz_responses` - Individual question responses
- `guardian_students` - Guardian-student relationships

## 🔧 Development Commands

### Backend
```bash
# Start backend only
docker-compose -f docker-compose.dev.yml up app

# View logs
docker-compose -f docker-compose.dev.yml logs -f app

# Run database migrations
docker exec -it sms_app alembic upgrade head

# Access database
docker exec -it sms_postgres psql -U postgres -d sms_dev
```

### Frontend
```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

## 🚀 Deployment

### Production Environment

1. **Set up environment variables:**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with your production settings
   ```

2. **Deploy with Docker Compose:**
   ```bash
   # Option 1: Use convenience script
   ./start-prod.sh    # Linux/macOS
   start-prod.bat     # Windows
   
   # Option 2: Direct docker-compose command
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **Load production data:**
   ```bash
   # Access the PostgreSQL container
   docker exec -it sms_postgres psql -U postgres -d sms_prod
   # Run your production data scripts
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Production Considerations
- Set up proper SSL certificates
- Configure database backups
- Set up monitoring and logging
- Use environment-specific secrets
- Configure proper CORS origins

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sms_prod

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=School Management System
```

## 📝 API Documentation

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout

### Teacher Endpoints
- `GET /teacher/classes` - Get teacher's classes
- `POST /teacher/classes` - Create new class
- `GET /teacher/quizzes` - Get teacher's quizzes
- `POST /teacher/quizzes` - Create new quiz
- `GET /teacher/stats` - Get teacher statistics

### Student Endpoints
- `GET /student/classes` - Get enrolled classes
- `GET /student/quizzes` - Get available quizzes
- `POST /student/quizzes/{id}/start` - Start quiz attempt
- `POST /student/quiz-attempts/{id}/submit` - Submit quiz
- `GET /student/results` - Get quiz results

### Guardian Endpoints
- `GET /guardian/students` - Get linked students
- `GET /guardian/students/{id}/progress` - Get student progress
- `GET /guardian/communications` - Get communications

## 🧪 Testing

### Test Data
The system includes comprehensive test data:
- 1 Teacher with 2 classes (Grade 5 English & Science)
- 2 Students enrolled in both classes
- 2 Guardians linked to the students
- 4 Sample quizzes with questions
- Sample quiz attempts and results

### Running Tests
```bash
# Backend tests
docker exec -it sms_app pytest

# Frontend tests
cd web
npm test
```

## 🔍 Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check if PostgreSQL container is running
   - Verify DATABASE_URL in environment variables
   - Check if database exists

2. **Frontend build errors**
   - Clear Next.js cache: `rm -rf .next`
   - Reinstall dependencies: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npx tsc --noEmit`

3. **Authentication issues**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration
   - Ensure API_URL is correct

## 🛣️ Roadmap

### Phase 1 (Current - Complete)
- [x] Basic authentication and dashboards
- [x] Quiz taking functionality
- [x] **Role-based access control (RBAC)**
- [x] **Permission system implementation**
- [x] **Teacher profile restrictions working**
- [x] **All user dashboards functional**

### Phase 2 (Next)
- [ ] Complete quiz management workflow
- [ ] Progress reporting and analytics
- [ ] Teacher quiz creation UI
- [ ] Guardian-student communication
- [ ] Error boundaries and loading states
- [ ] Mobile responsiveness
- [ ] **Frontend Docker configuration**

### Phase 3 (Future)
- [ ] Real-time notifications
- [ ] File upload/download
- [ ] Advanced reporting
- [ ] AI-powered quiz generation
- [ ] Multi-tenant support
- [ ] Mobile app

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For support, please contact [your-email@example.com] or create an issue in the repository.

---

## 🔄 Current Status & Next Steps

### ✅ What's Working Now
1. **Complete authentication system** - All login flows work
2. **Role-based dashboards** - Teacher, Student, Guardian dashboards
3. **Permission system** - Teachers can only create quizzes, not classes
4. **Database integration** - Test data loaded, API calls working
5. **Security** - JWT tokens, bcrypt passwords, environment variables
6. **Backend API** - All endpoints functional with proper authorization

### 🎯 What's Next
1. **Quiz Creation UI** - Teacher interface to create quizzes
2. **Quiz Results Page** - Display quiz results and analytics
3. **Progress Reports** - Student progress tracking
4. **Guardian Features** - Student-parent linking and communication
5. **Error Handling** - Proper error boundaries and loading states
6. **Mobile Support** - Responsive design improvements

### 🐳 Docker Status
- **Backend**: ✅ Fully containerized with PostgreSQL
- **Frontend**: ✅ **Now fully containerized in development**
- **Database**: ✅ PostgreSQL container with persistent data
- **All Services**: ✅ Single command startup with `docker-compose`

### 🚀 Complete Docker Setup
Now both frontend and backend are containerized! Start everything with:

```bash
# Start all services (backend, frontend, database, admin)
docker-compose -f docker-compose.dev.yml up --build -d

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000  
# - Database Admin: http://localhost:8080
```

### Benefits of Full Containerization
1. **Consistent Environment**: Same setup across all machines
2. **Single Command Start**: No need for separate `npm run dev`
3. **CORS Issues Eliminated**: All services in same Docker network
4. **Port Conflicts Resolved**: Frontend always on port 3000
5. **Production Ready**: Easy deployment to any Docker environment
