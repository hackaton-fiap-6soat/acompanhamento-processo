from fastapi import APIRouter

from app.api.api_v1.endpoints import acompanhamentos

router = APIRouter()
router.include_router(acompanhamentos.router, prefix="/acompanhamentos", tags=["Acompanhamentos"])