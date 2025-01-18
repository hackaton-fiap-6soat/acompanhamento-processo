import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.adapter.http_api import HTTPAPIAdapter
from app.domain.services import AcompanhamentoService
from fastapi import HTTPException


@pytest.fixture
def mock_acompanhamento_service():
    return MagicMock(AcompanhamentoService)


@pytest.fixture
def client(mock_acompanhamento_service):
    api_adapter = HTTPAPIAdapter(mock_acompanhamento_service)
    return TestClient(api_adapter.router)


def test_buscar_acompanhamento_success(client, mock_acompanhamento_service):
    # Arrange
    mock_acompanhamento_service.buscar_acompanhamento.return_value = {"processos": []}

    # Act
    response = client.get("/acompanhamento/user123")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"processos": []}
    mock_acompanhamento_service.buscar_acompanhamento.assert_called_once_with("user123")


def test_buscar_acompanhamento_error(client, mock_acompanhamento_service):
    # Arrange
    mock_acompanhamento_service.buscar_acompanhamento.side_effect = Exception("Erro ao buscar")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        client.get("/acompanhamento/U12346")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Erro ao buscar acompanhamento: Erro ao buscar"