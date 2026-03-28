import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_DEPLOYED = os.getenv("RENDER") or os.getenv("VERCEL")

if IS_DEPLOYED or ENVIRONMENT == "production":
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL")
    print("[INFO] Fixing PRODUCTION database")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL", "postgresql://postgres:admin@localhost/jay_industries")
    print("[INFO] Fixing DEVELOPMENT database")

if not SQLALCHEMY_DATABASE_URL:
    print("[ERROR] No database URL found!")
    exit(1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def fix_database():
    with engine.connect() as connection:
        # Add columns to users table if they don't exist
        columns_to_add = [
            ("is_admin", "BOOLEAN DEFAULT FALSE"),
            ("is_logged_in", "BOOLEAN DEFAULT FALSE"),
            ("is_registered", "BOOLEAN DEFAULT FALSE")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                # PostgreSQL specific check for column existence
                query = text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                connection.execute(query)
                connection.commit()
                print(f"[SUCCESS] Ensured '{col_name}' column exists in 'users' table")
            except Exception as e:
                print(f"[ERROR] Error adding '{col_name}' column: {e}")

        # Add indexes for performance
        indexes_to_add = ["is_logged_in", "is_admin"]
        for idx_col in indexes_to_add:
            try:
                # PostgreSQL doesn't have CREATE INDEX IF NOT EXISTS in all versions, 
                # but we can check if it exists or just try and handle the error.
                idx_name = f"ix_users_{idx_col}"
                connection.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON users ({idx_col})"))
                connection.commit()
                print(f"[SUCCESS] Ensured index exists for '{idx_col}'")
            except Exception as e:
                print(f"[WARNING] Could not create index for {idx_col}: {e}")

        # Check products table
        try:
            res = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='name'"))
            column_exists = res.fetchone()
            
            if not column_exists:
                print("[INFO] Products table is missing 'name' column or doesn't exist. Recreating...")
                connection.execute(text("DROP TABLE IF EXISTS products CASCADE"))
                connection.execute(text("""
                    CREATE TABLE products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR,
                        description VARCHAR,
                        image_url VARCHAR,
                        is_published BOOLEAN DEFAULT TRUE
                    )
                """))
                connection.execute(text("CREATE INDEX ix_products_id ON products (id)"))
                connection.execute(text("CREATE INDEX ix_products_name ON products (name)"))
                connection.commit()
                print("[SUCCESS] Successfully recreated 'products' table")
            else:
                print("[INFO] Products table exists and has 'name' column. Skipping recreation.")
        except Exception as e:
            print(f"[ERROR] Error handling 'products' table: {e}")

if __name__ == "__main__":
    fix_database()
