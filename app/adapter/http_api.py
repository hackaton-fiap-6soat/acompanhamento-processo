from fastapi import APIRouter, HTTPException

from app.domain.services import AcompanhamentoService


class HTTPAPIAdapter:
    def __init__(self, acompanhamento_service: AcompanhamentoService):
        self.__acompanhamento_service = acompanhamento_service
        self.router = APIRouter()

        self.router.add_api_route("/acompanhamento/{id_usuario}", self.buscar_acompanhamento, methods=["GET"])


    def buscar_acompanhamento(self, id_usuario: str):
        try:
            return self.__acompanhamento_service.buscar_acompanhamento(id_usuario)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar acompanhamento: {e}")