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

# Configure CORS for Next.js frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to Jay Industries Authentication API"}

@app.get("/health")
def health_check():
    """Health check endpoint - doesn't require database"""
    return {"status": "ok", "message": "FastAPI server is running"}
