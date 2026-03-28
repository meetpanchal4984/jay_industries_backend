import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# Handle potential Render/Supabase postgres:// instead of postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        print("Migrating database schema...")
        
        # Add is_published to products
        try:
            print("Adding 'is_published' column to products table...")
            conn.execute(text("ALTER TABLE products ADD COLUMN is_published BOOLEAN DEFAULT TRUE"))
            conn.commit()
            print("Successfully added 'is_published' column.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("'is_published' column already exists.")
            else:
                print(f"Failed to add 'is_published' column: {e}")

if __name__ == "__main__":
    migrate()
