from fastapi import APIRouter

from app.adapter.api.api_v1.endpoints import adapters_in

router = APIRouter()
router.include_router(acompanhamentos.router, prefix="/acompanhamentos", tags=["Acompanhamentos"])