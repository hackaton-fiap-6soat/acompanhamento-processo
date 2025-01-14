from abc import ABC, abstractmethod

from app.domain.models import ProcessosUsuario


class AcompanhamentoRepository(ABC):

    @abstractmethod
    def criar_usuario(self, processosUsuario: ProcessosUsuario):
        pass

    @abstractmethod
    def adicionar_processo(self, processosUsuario: ProcessosUsuario):
        pass

    @abstractmethod
    def atualizar_processo(self, id_usuario: str, nome_processo: str, status, id_status: int):
        pass

    @abstractmethod
    def buscar_processos(self, user_id: str):
        pass