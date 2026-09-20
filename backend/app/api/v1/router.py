from fastapi import APIRouter
from app.api.v1.endpoints import health, documents, chat, search, admin, evaluation

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(chat.router)
api_v1_router.include_router(search.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(evaluation.router)
