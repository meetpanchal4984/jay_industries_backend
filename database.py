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

# Use QueuePool (default) with safety checks for Render
# pool_pre_ping is the most important fix for "SSL closed unexpectedly" on Render/Supabase
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,      # Checks connection health before every request
    pool_recycle=300,        # Recycles connections every 5 minutes
    pool_size=10,            # Standard pooling for Render
    max_overflow=20,
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
