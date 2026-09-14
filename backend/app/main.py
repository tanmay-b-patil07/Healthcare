from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.api.routes.auth import router as auth_router
from app.api.routes.donor import router as donor_router
from app.api.routes.hospital import router as hospital_router
from app.api.routes.blood_bank import router as blood_bank_router
from app.api.routes.blood_inventory import router as blood_inventory_router
from app.api.routes.blood_request import router as blood_request_router
from app.api.routes.donar_match import router as donar_match_router

app = FastAPI(
    title="Blood Donation Emergency Connector",
    version="1.0.0",
    debug=settings.DEBUG,
)


# API Routers
app.include_router(auth_router)
app.include_router(donor_router)
app.include_router(hospital_router)
app.include_router(blood_bank_router)
app.include_router(blood_inventory_router)
app.include_router(blood_request_router)
app.include_router(donar_match_router)


@app.get("/")
def root():
    return {
        "message": "Blood Donation Emergency Connector API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected",
        }