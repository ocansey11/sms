# SMS Database Scripts

This directory contains database setup scripts and utilities for the SMS (Student Management System) project.

## Database Schema Files

### 📁 `local_postgres_schema.sql`
**Purpose:** Local development database schema  
**Database:** PostgreSQL (Docker container)  
**Environment:** Local development (`sms_dev`)  

**Features:**
- Complete normalized ERD structure
- Sample data for testing
- No Supabase-specific features (RLS, auth.uid())
- Optimized for local development and testing

**Usage:**
```bash
# Apply to local Docker PostgreSQL
docker exec -i sms-postgres-1 psql -U sms_user -d sms_dev < scripts/local_postgres_schema.sql
```

### 🌐 `supabase_schema.sql`
**Purpose:** Supabase cloud database schema  
**Database:** Supabase PostgreSQL  
**Environment:** Development, Staging, Production  

**Features:**
- Complete normalized ERD structure
- Row Level Security (RLS) policies
- Supabase Auth integration
- Production-ready security features

**Usage:**
1. Copy and paste into Supabase SQL Editor
2. Execute in your Supabase project
3. Configure environment variables in your app

## Database Environment Strategy

### 🏗️ **Four-Environment Setup**

1. **Local Development** (`sms_dev`)
   - PostgreSQL in Docker
   - Fast development and testing
   - Uses `local_postgres_schema.sql`

2. **Supabase Development**
   - Online development testing
   - Team collaboration
   - Uses `supabase_schema.sql`

3. **Supabase Staging**
   - Pre-production testing
   - Production data simulation
   - Uses `supabase_schema.sql`

4. **Supabase Production**
   - Live application
   - Real users and data
   - Uses `supabase_schema.sql`

## Other Scripts

### 👥 `create_demo_users.py`
Creates demo users for testing signup and authentication flows.

### 🔐 `test_demo_credentials.py`
Tests authentication with demo user credentials.

## Database Migration Workflow

```mermaid
graph LR
    A[Local Dev] --> B[Supabase Dev]
    B --> C[Supabase Staging]
    C --> D[Supabase Production]
```

1. **Develop locally** with Docker PostgreSQL
2. **Test online** with Supabase Development
3. **Validate** in Supabase Staging
4. **Deploy** to Supabase Production

## Quick Start

### Local Development Setup
```bash
# Start Docker containers
docker-compose -f docker-compose.dev.yml up -d

# Apply local schema
docker exec -i sms-postgres-1 psql -U sms_user -d sms_dev < scripts/local_postgres_schema.sql

# Start backend
python run_dev.py
```

### Supabase Setup
1. Create new Supabase project
2. Copy `scripts/supabase_schema.sql` content
3. Execute in Supabase SQL Editor
4. Configure environment variables
5. Test with frontend

## Environment Variables

### Local Development
```env
DATABASE_URL=postgresql+asyncpg://sms_user:sms_password@localhost:5432/sms_dev
```

### Supabase
```env
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Notes

- Both schemas implement the same normalized ERD design
- Local schema excludes Supabase-specific features for compatibility
- Supabase schema includes RLS policies for security
- Migration scripts will be added as the project evolves
