@echo off
REM Start development environment
echo Starting development environment...
echo This will start:
echo   - Backend API (port 8000)
echo   - Frontend (port 3000)
echo   - PostgreSQL Database (port 5432)
echo   - Adminer (port 8080)
echo.

REM Build and start services
docker-compose -f docker-compose.dev.yml up --build

echo.
echo Development environment stopped.
echo Access the application at:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - Adminer: http://localhost:8080
