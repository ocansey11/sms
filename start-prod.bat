@echo off
REM Start production environment
echo Starting production environment...
echo This will start:
echo   - Backend API (port 8000)
echo   - Frontend (port 3000)
echo   - PostgreSQL Database
echo.

REM Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

echo.
echo Production environment started.
echo Access the application at:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo.
echo To stop the production environment, run:
echo docker-compose -f docker-compose.prod.yml down
