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

# Priority: Use SUPABASE_DATABASE_URL for production
# Render sometimes fills DATABASE_URL with its own internal values, so we prioritize the Supabase one
SUPABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
RENDER_URL = os.getenv("DATABASE_URL")
LOCAL_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:admin@localhost/jay_industries")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_DEPLOYED = os.getenv("RENDER") or os.getenv("VERCEL")

if IS_DEPLOYED or ENVIRONMENT == "production":
    SQLALCHEMY_DATABASE_URL = SUPABASE_URL or RENDER_URL
    print(f"[INFO] Backend Running in PRODUCTION mode (Using: {'SUPABASE' if SUPABASE_URL else 'RENDER'} URL)")
else:
    SQLALCHEMY_DATABASE_URL = LOCAL_URL
    print("[INFO] Backend Running in DEVELOPMENT mode")

if not SQLALCHEMY_DATABASE_URL:
    print("[ERROR] CRITICAL: No database URL found!")
    SQLALCHEMY_DATABASE_URL = LOCAL_URL

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
    pool_recycle=300,        # Recycles connections every 5 minutes (more standard)
    pool_size=20,            # High capacity pooling
    max_overflow=30,         # Allow up to 50 concurrent connections
    connect_args={
        "connect_timeout": 30,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
