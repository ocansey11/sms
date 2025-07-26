"""
Diagnostic script to check current database schema
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_schema():
    """Check current database schema."""
    # Test database URL
    DATABASE_URL = "postgresql+asyncpg://sms_user:sms_password@postgres:5432/test_db"
    
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # Check if tenants table exists
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('users', 'tenants')
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📊 Existing tables: {tables}")
            
            # Check users table columns
            if 'users' in tables:
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='users'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print("\n👤 Users table columns:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Check tenants table columns
            if 'tenants' in tables:
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='tenants'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print("\n🏢 Tenants table columns:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
                    
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure your database is running and accessible")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_schema())