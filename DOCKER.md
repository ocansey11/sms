# Docker Setup Guide for SMS

## Quick Start Commands

### Start Everything
```bash
# From the sms root directory
docker-compose -f docker-compose.dev.yml up -d
```

### Check Status
```bash
docker-compose -f docker-compose.dev.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f app
```

### Access Database
```bash
# Connect to PostgreSQL
docker exec -it sms_postgres psql -U postgres -d sms_dev

# Load test data
docker exec -it sms_postgres psql -U postgres -d sms_dev -f /scripts/complete_sample_data.sql
```

### Stop Everything
```bash
docker-compose -f docker-compose.dev.yml down
```

### Reset Database
```bash
# Stop containers
docker-compose -f docker-compose.dev.yml down

# Remove volumes (this will delete all data)
docker volume rm sms_postgres_data

# Start fresh
docker-compose -f docker-compose.dev.yml up -d
```

## Service URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8080

## Environment Files
- `.env.development` - Development settings
- `.env.production` - Production settings
- `web/.env.local` - Frontend environment

## Troubleshooting
- If ports are in use, check docker-compose.dev.yml
- If database connection fails, ensure PostgreSQL container is running
- If frontend can't connect to API, check NEXT_PUBLIC_API_URL in web/.env.local
