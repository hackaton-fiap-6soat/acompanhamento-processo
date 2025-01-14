import datetime
import json
import logging

from app.domain.models import ProcessosUsuario
from app.port.repositories import AcompanhamentoRepository

logger = logging.getLogger(name="sqs_handler")
logger.setLevel(logging.INFO)

# Cria o manipulador de logs para o CloudWatch
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Adiciona o manipulador ao logger
logger.addHandler(ch)

class AcompanhamentoService:

    def __init__(self, acompanhamentoRepository: AcompanhamentoRepository):
        caminho_arquivo = "app/data/maquina_estado.json"
        with open(caminho_arquivo, "r") as arquivo:
            self.__maquina_estado = json.load(arquivo)

        self.__repository = acompanhamentoRepository

    def criar_atualizar_processo(self, data: dict):
        try:
            data = json.loads(data)
            logger.info(f"Tipo do dado recebido: {type(data)}")
            logger.info(f"Inicio da inclusão do processo. {data}")
            logger.info(data["processo"] + "_" + data["status"])
            processo = self.__gerar_processo(data["id_usuario"], data["processo"] + "_" + data["status"], data["nome_arquivo"])

            processoUsuarioDTO = ProcessosUsuario(**processo)
            logger.info(processoUsuarioDTO)
            processosUsuario = self.__repository.buscar_processos(processoUsuarioDTO.id_usuario)

            nome_arquivo = data["nome_arquivo"]

            if processosUsuario is None:
                self.__repository.criar_usuario(processoUsuarioDTO)
            else:
                if nome_arquivo not in processosUsuario.processos:
                    self.__repository.adicionar_processo(processoUsuarioDTO)
                else:
                    self.__repository.atualizar_processo(processoUsuarioDTO.id_usuario,
                                                         nome_arquivo,
                                                         processoUsuarioDTO.processos[nome_arquivo].status_processo,
                                                         processoUsuarioDTO.processos[nome_arquivo].id_status)
        except Exception as e:
            raise ValueError(f"Erro ao criar processo do usuário: {e}")


    def __gerar_processo(self, id_usuario: str, processo: str, nome_arquivo: str):
         return {
              "id_usuario": id_usuario,
              "processos": {
                nome_arquivo: {
                    "id_status": self.__maquina_estado[processo]["id_status"],
                    "status_processo": self.__maquina_estado[processo]["status_processo"],
                    "timestamp_processo": datetime.datetime.now().isoformat()
                }
              }
         }

    def buscar_acompanhamento(self, id_usuario: str):
        return self.__repository.buscar_processos(id_usuario)