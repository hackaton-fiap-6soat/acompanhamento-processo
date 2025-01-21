import json
import pytest
from unittest.mock import patch, MagicMock

from app.adapter.adapters_in import handler


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
def mock_dynamodb():
    # Mock do recurso DynamoDB
    mock_session = MagicMock()
    mock_dynamodb_resource = MagicMock()
    mock_table = MagicMock()

    # Configura o mock para retornar o recurso e a tabela
    mock_session.resource.return_value = mock_dynamodb_resource
    mock_dynamodb_resource.Table.return_value = mock_table

    with patch('app.adapter.adaptersDB.boto3.Session', return_value=mock_session):
        yield mock_dynamodb_resource

@pytest.fixture
def mock_acompanhamento_service(mock_dynamodb):    
    service = MagicMock()
    service.criar_atualizar_processo = MagicMock()  # Mock do método
    with patch('app.domain.services.AcompanhamentoService', return_value=service):
        yield service

def test_handler_success(mock_acompanhamento_service):
    # Arrange
    event = {
        "Records": [
            {"body": json.dumps({"id_usuario": "U12345", "processo": "recepcao", "nome_arquivo": "Arquivo1", "status": "ok"})}
        ]
    }

    # Act
    with patch('app.sqs_handler.AcompanhamentoService', return_value=mock_acompanhamento_service):
        response = handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert response["body"] == "Mensagens processadas com sucesso"

def test_handler_no_records(mock_acompanhamento_service):
    # Arrange
    event = {
        "Records": []
    }
    
    # Act
    with patch('app.sqs_handler.AcompanhamentoService', return_value=mock_acompanhamento_service):
        response = handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    assert response["body"] == "Mensagens processadas com sucesso"
