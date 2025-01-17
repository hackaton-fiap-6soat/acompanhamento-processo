import json
import unittest
from unittest.mock import Mock, patch

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


class TestAcompanhamentoServices(unittest.TestCase):



    def setUp(self):
        self.acompanhamentoRepository = Mock()
        self.service = AcompanhamentoService(self.acompanhamentoRepository, carregar_arquivo())

    def testInserirProcessoParaUsuarioNaoCadastrado(self):

        self.acompanhamentoRepository.buscar_processos.return_value = None

        self.service.criar_atualizar_processo({'id_usuario': 'U12345', 'processo': 'recepcao', 'nome_arquivo': 'Arquivo1', 'status': 'ok'})

        self.acompanhamentoRepository.criar_usuario.assert_called_once()

    def testInserirNovoProcessoParaUsuarioCadastrado(self):
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

        self.acompanhamentoRepository.buscar_processos.return_value = ProcessosUsuario(**data)

        self.service.criar_atualizar_processo({'id_usuario': 'U12345', 'processo': 'recepcao', 'nome_arquivo': 'Arquivo1', 'status': 'ok'})

        self.acompanhamentoRepository.adicionar_processo.assert_called_once()

    def testAtualizarProcessoParaUsuarioCadastrado(self):
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

        self.acompanhamentoRepository.buscar_processos.return_value = ProcessosUsuario(**data)

        self.service.criar_atualizar_processo({'id_usuario': 'U12345', 'processo': 'verificacao', 'nome_arquivo': 'Arquivo1', 'status': 'ok'})

        self.acompanhamentoRepository.atualizar_processo.assert_called_once()