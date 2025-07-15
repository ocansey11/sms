@echo off
REM Start development environment
echo ========================================
echo  SMS Development Environment Startup
echo ========================================
echo This will start:
echo   - Backend API (port 8000)
echo   - Frontend (port 3000)  
echo   - PostgreSQL Database (port 5432)
echo   - Adminer (port 8080)
echo.

echo Step 1: Building and starting Docker containers...
docker-compose -f docker-compose.dev.yml up --build -d

echo.
echo Step 2: Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo.
echo Step 3: Testing existing demo credentials...
docker exec sms-app-1 python /app/scripts/test_demo_credentials.py

echo.
echo Step 4: Creating missing demo users...
docker exec sms-app-1 python /app/scripts/create_demo_users.py

echo.
echo Step 5: Testing all demo credentials again...
docker exec sms-app-1 python /app/scripts/test_demo_credentials.py

echo.
echo ========================================
echo  🎉 SMS Development Environment Ready!
echo ========================================
echo.
echo 📋 Demo Credentials:
echo   👨‍💼 Admin: admin@school.edu / admin123
echo   👩‍🏫 Teacher: sarah.johnson@teacher.schoolsms.com / teacher123  
echo   👩‍🎓 Student: emma.smith@student.schoolsms.com / student123
echo   👨‍👩‍👧‍👦 Guardian: john.smith@email.com / guardian123
echo.
echo 🌐 Access URLs:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000/docs
echo   - Adminer: http://localhost:8080
echo.
echo Press Ctrl+C to stop all services...
docker-compose -f docker-compose.dev.yml logs -f

echo.
echo Development environment stopped.
pause