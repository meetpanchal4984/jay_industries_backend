import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost/jay_industries"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def fix_database():
    with engine.connect() as connection:
        # Add is_admin column to users table if it doesn't exist
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
            connection.commit()
            print("Successfully added 'is_admin' column to 'users' table (if it wasn't there)")
        except Exception as e:
            print(f"Error adding 'is_admin' column: {e}")

        # Re-check products table
        try:
            # Check if name column exists in products table
            res = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='name'"))
            column_exists = res.fetchone()
            
            if not column_exists:
                print("Products table is missing 'name' column or doesn't exist. Recreating...")
                connection.execute(text("DROP TABLE IF EXISTS products CASCADE"))
                connection.execute(text("""
                    CREATE TABLE products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR,
                        description VARCHAR,
                        image_url VARCHAR
                    )
                """))
                connection.execute(text("CREATE INDEX ix_products_id ON products (id)"))
                connection.execute(text("CREATE INDEX ix_products_name ON products (name)"))
                connection.commit()
                print("Successfully recreated 'products' table")
            else:
                print("Products table exists and has 'name' column. Skipping recreation.")
        except Exception as e:
            print(f"Error handling 'products' table: {e}")

if __name__ == "__main__":
    fix_database()
