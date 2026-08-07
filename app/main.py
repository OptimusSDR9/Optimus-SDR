from fastapi import FastAPI
from app.database import Base, engine
import app.models
app = FastAPI(
    title="Optimus AI SDR",
    version="1.0.0",
    description="AI Sales Development Representative for Optimus RCM Solutions"
)
Base.metadata.create_all(bind=engine)
@app.get("/")
async def home():
    return {
        "status": "running",
        "message": "Optimus AI SDR is Running 🚀"
    }