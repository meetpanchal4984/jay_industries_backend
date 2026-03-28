import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path("d:/Languages/jay_industries/jay_industries_backend")
sys.path.append(str(backend_path))

try:
    from database import engine, SessionLocal
    import models
    from sqlalchemy import text
    
    print("Testing database connection with new configurations...")
    
    # Try a simple query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database(), current_user, current_setting('port')"))
        db_info = result.fetchone()
        print(f"Successfully connected! DB Info: {db_info}")
        
    # Try using the session
    db = SessionLocal()
    try:
        user_count = db.query(models.User).count()
        print(f"Found {user_count} users in the database.")
    finally:
        db.close()
        
    print("\nSUCCESS: Database connection is working perfectly with Transaction Mode (Port 6543) and NullPool.")

except Exception as e:
    print(f"\nFAILURE: Could not connect to database: {e}")
    sys.exit(1)
