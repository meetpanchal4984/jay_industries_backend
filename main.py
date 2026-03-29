from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models, database
from routes import router

# Database tables will be initialized on the first request if this fails
# Adding resilience for production environments on Render
try:
    print(f"[INFO] Initializing database connection to: {database.SQLALCHEMY_DATABASE_URL.split('@')[-1].split('/')[0]}")
    models.Base.metadata.create_all(bind=database.engine)
    print("[INFO] Database tables verified/created successfully")
except Exception as e:
    print(f"[WARNING] Database connection during startup failed: {e}")
    print("FastAPI will retry connection automatically on the first API request.")

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Jay Industries API")

# Ensure static/uploads exists
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    import time
    max_retries = 3
    for attempt in range(max_retries):
        db = database.SessionLocal()
        try:
            db.query(models.User).update({models.User.is_logged_in: False})
            db.commit()
            print("[INFO] Reset all user login statuses on startup")
            break
        except Exception as e:
            print(f"[WARNING] Attempt {attempt + 1}: Could not reset login statuses: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
        finally:
            db.close()

# Configure CORS for Next.js frontend (localhost + Vercel production + local network)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://jay-industries-opal.vercel.app",
    "https://*.vercel.app",
]

# Add middleware with more permissive development settings to support mobile testing on local network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to Jay Industries Authentication API", "status": "ok"}

@app.get("/health")
def health_check():
    """Health check endpoint - doesn't require database"""
    return {"status": "ok", "message": "FastAPI server is running"}

@app.get("/api/health")
def api_health_check():
    """API health endpoint"""
    return {"status": "ok", "api": "online"}
