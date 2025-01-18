import unittest
from app.domain.models import ProcessosUsuario, Processo
from datetime import datetime


class TestAcompanhamentoServices(unittest.TestCase):
    
    
    def test_processos_usuario_creation(self):
        processo = Processo(id_status=1, status_processo="recebido", timestamp_processo=datetime.now())
        processos_usuario = ProcessosUsuario(id_usuario="U12346", processos={"Arquivo1": processo})

        assert processos_usuario.id_usuario == "U12346"
        assert "Arquivo1" in processos_usuario.processos
        assert processos_usuario.processos["Arquivo1"].status_processo == "recebido"