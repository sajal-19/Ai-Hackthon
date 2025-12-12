from fastapi import FastAPI

from app.api.health import router as health_router
from app.auth.router import router as auth_router
from app.users_org.router import router as users_router
from app.trainings.router import router as trainings_router

app = FastAPI(
    title="L&D Portal API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(trainings_router)
