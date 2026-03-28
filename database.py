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

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Fallback to local if still not found, but this shouldn't happen if .env is correct
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost/jay_industries"
    print("WARNING: DATABASE_URL not found in environment, falling back to local database.")
else:
    # Print the host to verify connection (omitting password for security)
    host = SQLALCHEMY_DATABASE_URL.split('@')[-1]
    print(f"Connecting to database host: {host}")

# Use NullPool when connecting to an external pooler (like Supabase Transaction pooler)
# to avoid double-pooling and session issues.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 10}  # 10 second timeout
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
