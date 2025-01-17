from fastapi import APIRouter, HTTPException

from app.adapter.adaptersDB import AcompanhamentoDB
from app.domain.services import AcompanhamentoService

router = APIRouter()

@router.get("/{id}")
async def obter_acompanhamento(id: str):
    dynamodb = AcompanhamentoDB("AcompanhamentoProcesso")
    service = AcompanhamentoService(dynamodb)
    acompanhamento = service.buscar_acompanhamento(id)

    if acompanhamento is None:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    else:
        return acompanhamento