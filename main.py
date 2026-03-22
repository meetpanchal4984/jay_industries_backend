from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models, database
from routes import router

# Create the database tables with error handling
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("✓ Database tables created successfully")
except Exception as e:
    print(f"⚠ Warning: Could not create database tables on startup: {e}")
    print("The app will continue running. Tables will be created on first database operation.")

app = FastAPI(title="Jay Industries API")

# Configure CORS for Next.js frontend (localhost + Vercel production)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://jay-industries-opal.vercel.app",  # Your Vercel domain
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
