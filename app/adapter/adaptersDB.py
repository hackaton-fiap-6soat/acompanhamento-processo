import datetime
import logging

import boto3
import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from app.adapter.exceptions import DynamoDBException
from app.domain.models import ProcessosUsuario
from app.port.repositories import AcompanhamentoRepository

os.environ.pop("AWS_ACCESS_KEY_ID", None)
os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
os.environ.pop("AWS_SESSION_TOKEN", None)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DynamoDBAdapter")

load_dotenv(dotenv_path='app/.env')

class AcompanhamentoDB(AcompanhamentoRepository):
    def __init__(self, table_name: str):
        self.__table_name = table_name
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            region_name=os.getenv("region")
        )

        self.__dynamodb = session.resource('dynamodb')
        self.__table = self.__get_table()

    def __get_table(self):
        try:
            return self.__dynamodb.Table(self.__table_name)
        except Exception as e:
            raise DynamoDBException({
                "code": "dynamodb.error.table.unavailable",
                "message": f"Tabela DynamoDB não encontrada: {e}",
            })

    def criar_usuario(self, processosUsuario: ProcessosUsuario):
        self.__table.put_item(Item=processosUsuario.model_dump(mode="json"))

    def adicionar_processo(self, processosUsuario: ProcessosUsuario):
        try:
            for arquivo, processo in processosUsuario.processos.items():
                response = self.__table.update_item(
                    Key={
                        "id_usuario": processosUsuario.id_usuario
                    },
                    UpdateExpression=f"""
                        SET processos.#arquivo = if_not_exists(processos.#arquivo, :novo_processo)
                    """,
                    ExpressionAttributeNames={
                        "#arquivo": arquivo
                    },
                    ExpressionAttributeValues={
                        ":novo_processo": {
                            "id_status": processo.id_status,
                            "status_processo": processo.status_processo,
                            "timestamp_processo": processo.timestamp_processo.isoformat()
                        }
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print(f"Processo {arquivo} atualizado com sucesso:", response)
        except Exception as e:
            print("Erro ao atualizar processos:", e)

        return response

    def atualizar_processo(self, id_usuario: str, nome_processo: str, status, id_status: int):
        try:
            timestamp_atual = datetime.datetime.now().isoformat()
            response = self.__table.update_item(
                Key={
                    "id_usuario": id_usuario
                },
                UpdateExpression=(
                    "SET processos.#nome.id_status = :novo_id_status "
                    ", processos.#nome.status_processo = :novo_status "
                    ", processos.#nome.timestamp_processo = :novo_timestamp"
                ),
                ConditionExpression="attribute_exists(processos.#nome) AND processos.#nome.id_status < :novo_id_status",
                ExpressionAttributeNames={
                    "#nome": nome_processo
                },
                ExpressionAttributeValues={
                    ":novo_id_status": id_status,
                    ":novo_status": status,
                    ":novo_timestamp": timestamp_atual
                },
                ReturnValues="UPDATED_NEW"
            )

            print(f"Processo '{nome_processo}' atualizado com sucesso.")
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(
                    f"Status do processo {nome_processo} está obsoleto. "
                    f"ID Usuário: {id_usuario}, Novo ID Status: {id_status}, Status Atual: '{status}'"
                )

                return None
            else:
                logger.error(f"Erro inesperado ao atualizar o processo '{nome_processo}': {e}")
                raise

        except Exception as e:
            print(f"Erro ao atualizar o processo '{nome_processo}': {e}")
            raise

    def buscar_processos(self, user_id: str):
        try:
            response = self.__table.get_item( Key={"id_usuario": user_id })
            if 'Item' in response:
                return ProcessosUsuario(**response['Item'])
            else:
                None
        except Exception as e:
            raise ValueError("Erro ao buscar processos do usuário!")