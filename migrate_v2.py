import sys
import os

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
import models

def migrate():
    print("Starting Database Migration V2...")
    try:
        # Create all tables (will skip existing ones and create product_images)
        Base.metadata.create_all(bind=engine)
        print("Done: Database migration successful: 'product_images' table and relationships created.")
    except Exception as e:
        print(f"Error: Migration failed: {e}")

if __name__ == "__main__":
    migrate()
