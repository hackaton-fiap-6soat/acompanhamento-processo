import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.domain.services import AcompanhamentoService
from app.main import app

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
def client():
    return TestClient(app)

@pytest.fixture
def mock_dynamodb():
    with patch('app.adapter.adaptersDB.boto3.Session') as mock:
        yield mock

@pytest.fixture
def mock_acompanhamento_service(mock_dynamodb):
    service = MagicMock()
    service.criar_atualizar_processo = MagicMock()

    with patch('app.domain.services.AcompanhamentoService', return_value=service):
        AcompanhamentoService(mock_dynamodb, carregar_arquivo())
    return service

def test_root(client):
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}
