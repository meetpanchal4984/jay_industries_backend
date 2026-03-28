from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

# Explicitly load .env from the same directory as this file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Automatically detect if running on Render or Vercel
IS_DEPLOYED = os.getenv("RENDER") or os.getenv("VERCEL")

if IS_DEPLOYED or ENVIRONMENT == "production":
    # Use DATABASE_URL (standard for most deployment platforms) or the specific Supabase one from .env
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL")
    print("[INFO] Backend Running in PRODUCTION mode")
else:
    # Use local database for development
    SQLALCHEMY_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:admin@localhost/jay_industries")
    print("[INFO] Backend Running in DEVELOPMENT mode")

if not SQLALCHEMY_DATABASE_URL:
    print("[ERROR] CRITICAL ERROR: No database URL found!")
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost/jay_industries"

# Print the host to verify connection (omitting password for security)
try:
    # Try to extract host for debugging
    host = SQLALCHEMY_DATABASE_URL.split('@')[-1].split('/')[0]
    print(f"Connecting to database host: {host}")
except Exception:
    print("Connecting to database...")

# Enhanced engine configuration for Production (Supabase Session Pooler)
# Adding ?prepared_statements=false as a safeguard for poolers
if IS_DEPLOYED or ENVIRONMENT == "production":
    if "?" in SQLALCHEMY_DATABASE_URL:
        if "prepared_statements=false" not in SQLALCHEMY_DATABASE_URL:
            SQLALCHEMY_DATABASE_URL += "&prepared_statements=false"
    else:
        SQLALCHEMY_DATABASE_URL += "?prepared_statements=false"

# Use QueuePool (default) with safety checks for Render
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,      # Checks connection health before every request
    pool_recycle=300,        # Recycles connections every 5 minutes to prevent stale ones
    pool_size=5,             # Limit connections to avoid hitting Supabase limits
    max_overflow=10,
    connect_args={"connect_timeout": 30} # Longer timeout for cloud connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
