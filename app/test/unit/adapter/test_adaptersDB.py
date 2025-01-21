import pytest
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from app.adapter.adapters_out import AcompanhamentoDB, CustomDynamoDBException
from app.domain.models import ProcessosUsuario

@pytest.fixture
def mock_dynamodb():
    with patch('app.adapter.adapters_out.boto3.Session') as mock:
        yield mock


def test_criar_usuario_raises_exception(mock_dynamodb):
    db = AcompanhamentoDB("nome_da_tabela")
    processos_usuario = ProcessosUsuario(id_usuario="user123", processos={})

    # Simulando a exceção ao chamar put_item
    db._AcompanhamentoDB__table.put_item.side_effect = Exception("Erro ao criar usuário")

    with pytest.raises(Exception) as context:
        db.criar_usuario(processos_usuario)

    assert "Erro ao criar usuário" in str(context.value)

def test_atualizar_processo_raises_client_error(mock_dynamodb):
    db = AcompanhamentoDB("nome_da_tabela")

    # Simulando a exceção ClientError
    client_error = ClientError({"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem")
    db._AcompanhamentoDB__table.update_item.side_effect = client_error

    result = db.atualizar_processo("user123", "processo1", "novo_status", 2)

    assert result is None  # Verifica que o retorno é None para ConditionalCheckFailedException

def test_atualizar_processo_raises_exception(mock_dynamodb):
    db = AcompanhamentoDB("nome_da_tabela")

    # Simulando a exceção ao chamar update_item
    db._AcompanhamentoDB__table.update_item.side_effect = Exception("Erro inesperado")

    with pytest.raises(Exception) as context:
        db.atualizar_processo("user123", "processo1", "novo_status", 2)

    assert "Erro inesperado" in str(context.value)

def test_buscar_processos_raises_exception(mock_dynamodb):
    db = AcompanhamentoDB("nome_da_tabela")

    # Simulando a exceção ao chamar get_item
    db._AcompanhamentoDB__table.get_item.side_effect = Exception("Erro ao buscar processos")

    with pytest.raises(ValueError) as context:
        db.buscar_processos("user123")

    assert "Erro ao buscar processos" in str(context.value)

def test_criar_usuario(mock_dynamodb):
    # Arrange
    db = AcompanhamentoDB("test_table")
    processos_usuario = ProcessosUsuario(id_usuario="user123", processos={})

    # Act
    db.criar_usuario(processos_usuario)

    # Assert
    db._AcompanhamentoDB__table.put_item.assert_called_once_with(Item=processos_usuario.model_dump(mode="json"))

def test_adicionar_processo(mock_dynamodb):
    # Arrange
    db = AcompanhamentoDB("test_table")
    processos_usuario = ProcessosUsuario(id_usuario="user123", processos={
        "processo1": {"id_status": 1, "status_processo": "Em andamento", "timestamp_processo": "2023-01-01T00:00:00"}
    })

    # Act
    response = db.adicionar_processo(processos_usuario)

    # Assert
    assert response is not None  # Verifica se a resposta não é None
    db._AcompanhamentoDB__table.update_item.assert_called()  # Verifica se o método foi chamado

def test_atualizar_processo(mock_dynamodb):
    # Arrange
    db = AcompanhamentoDB("test_table")
    db._AcompanhamentoDB__table.update_item = MagicMock(return_value={"Attributes": {}})
    
    # Act
    response = db.atualizar_processo("user123", "processo1", "Concluído", 2)

    # Assert
    assert response is not None  # Verifica se a resposta não é None
    db._AcompanhamentoDB__table.update_item.assert_called()  # Verifica se o método foi chamado

def test_buscar_processos(mock_dynamodb):
    # Arrange
    db = AcompanhamentoDB("test_table")
    db._AcompanhamentoDB__table.get_item = MagicMock(return_value={"Item": {"id_usuario": "user123", "processos": {}}})

    # Act
    processos_usuario = db.buscar_processos("user123")

    # Assert
    assert processos_usuario.id_usuario == "user123"  # Verifica se o ID do usuário está correto