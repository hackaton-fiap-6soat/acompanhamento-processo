import pytest
from unittest.mock import Mock
from app.domain.models import ProcessosUsuario
from app.domain.services import AcompanhamentoService

def carregar_arquivo():
    return {
        "recepcao_ok": {
            "id_status": 1,
            "status_processo": "recebido"
        },
        "verificacao_ok": {
            "id_status": 2,
            "status_processo": "verificado"
        },
        "verificacao_erro": {
            "id_status": 9,
            "status_processo": "Erro Verificação"
        },
        "geracao_ok": {
            "id_status": 3,
            "status_processo": "gerado"
        },
        "geracao_erro": {
            "id_status": 10,
            "status_processo": "Erro Geração"
        },
        "notificacao_ok": {
            "id_status": 4,
            "status_processo": "notificado"
        },
        "notificacao_erro": {
            "id_status": 11,
            "status_processo": "Erro notificação"
        }
    }

@pytest.fixture
def setup_service():
    acompanhamento_repository = Mock()
    service = AcompanhamentoService(acompanhamento_repository, carregar_arquivo())
    return acompanhamento_repository, service

def test_inserir_processo_para_usuario_nao_cadastrado(setup_service):
    acompanhamento_repository, service = setup_service
    acompanhamento_repository.buscar_processos.return_value = None

    service.criar_atualizar_processo({'id_usuario': 'U12345', 'processo': 'recepcao', 'nome_arquivo': 'Arquivo1', 'status': 'ok'})

    acompanhamento_repository.criar_usuario.assert_called_once()

def test_inserir_novo_processo_para_usuario_cadastrado(setup_service):
    acompanhamento_repository, service = setup_service
    data = {
        "id_usuario": "U12345",
        "processos": {
            "Arquivo2": {
                "id_status": 1,
                "status_processo": "recebido",
                "timestamp_processo": "2025-01-16T21:55:36.151890"
            }
        }
    }

    acompanhamento_repository.buscar_processos.return_value = ProcessosUsuario(**data)

    service.criar_atualizar_processo({'id_usuario': 'U12345', 'processo': 'recepcao', 'nome_arquivo': 'Arquivo1', 'status': 'ok'})

    acompanhamento_repository.adicionar_processo.assert_called_once()

def test_atualizar_processo_para_usuario_cadastrado(setup_service):
    acompanhamento_repository, service = setup_service
    data = {
        "id_usuario": "U12345",
        "processos": {
            "Arquivo1": {
                "id_status": 1,
                "status_processo": "recebido",
                "timestamp_processo": "2025-01-16T21:55:36.151890"
            }
        }
    }

    acompanhamento_repository.buscar_processos.return_value = ProcessosUsuario(**data)

    service.criar_atualizar_processo({'id_usuario': 'U12345', 'processo': 'verificacao', 'nome_arquivo': 'Arquivo1', 'status': 'ok'})

    acompanhamento_repository.atualizar_processo.assert_called_once()