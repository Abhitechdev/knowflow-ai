from app.api.v1.endpoints import admin, chat, documents, evaluation, health, search
from app.api.v1.router import api_v1_router
from fastapi import APIRouter

api_router = APIRouter()

# Mount direct /api endpoints for convenience
api_router.include_router(health.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(search.router)
api_router.include_router(admin.router)
api_router.include_router(evaluation.router)

# Mount versioned /api/v1 endpoints
api_router.include_router(api_v1_router, prefix="/v1")
