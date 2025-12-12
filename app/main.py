from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(title="L&D Portal API", version="0.1.0")

# Routers
app.include_router(health_router)
