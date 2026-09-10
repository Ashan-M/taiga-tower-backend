from fastapi import FastAPI, Request
import time
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
import app.models  # Ensures all models are registered with Base
from app.routers import dashboard, mqtt
from app.logger import logger
from contextlib import asynccontextmanager

from app.mqtt.client import MQTTClient
from app.mqtt.service import mqttService
# Automatically create tables in PostgreSQL on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")

    mqttService.connect()

    yield

    print("Shutting down application...")

    mqttService.disconnect()

app = FastAPI(title="TaigaTower System API", lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {formatted_process_time}"
    )
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "https://taiga-tower.web.app",
        "https://taiga-tower.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(mqtt.router)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "message": "Taiga Tower API is running successfully!"
    }





if __name__ == "__main__":
    logger.info("Starting Taiga Tower FastAPI application...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)