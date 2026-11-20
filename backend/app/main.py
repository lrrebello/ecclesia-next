from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import router
from app.modules.churches.routes import router as churches_router
from app.modules.ministries.routes import router as ministries_router
from app.modules.members.routes import router as members_router
from app.modules.families.routes import router as families_router
from app.modules.events.routes import router as events_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

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

app.include_router(router, prefix="/api/v1")
app.include_router(churches_router, prefix="/api/v1")
app.include_router(ministries_router, prefix="/api/v1")
app.include_router(members_router, prefix="/api/v1")
app.include_router(families_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
