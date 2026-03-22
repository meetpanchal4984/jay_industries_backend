from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models, database
from routes import router

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Jay Industries API")

# Configure CORS for Next.js frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
    return {"message": "Welcome to Jay Industries Authentication API"}
