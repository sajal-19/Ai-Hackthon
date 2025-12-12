from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.auth.router import router as auth_router
from app.users_org.router import router as users_router
from app.trainings.router import router as trainings_router
from app.enrollments_attendance.router import router as enrollments_router
from app.profiles.router import router as profiles_router
from app.reporting.router import router as reporting_router
from app.gamification.router import router as gamification_router
from app.certificates.router import router as certificates_router

app = FastAPI(
    title="L&D Portal API",
    version="0.1.0",
)

origins = [
    "http://localhost:3000",  # React dev
    "http://localhost:5173",  # Vite dev
    # add your Render frontend URL later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(trainings_router)
app.include_router(enrollments_router)
app.include_router(profiles_router)
app.include_router(reporting_router)
app.include_router(gamification_router)
app.include_router(certificates_router)