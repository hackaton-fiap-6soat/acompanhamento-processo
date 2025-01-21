import json
import logging
from app.adapter.adapters_out import AcompanhamentoDB
from app.domain.services import AcompanhamentoService

logger = logging.getLogger(name="sqs_handler")
logger.setLevel(logging.INFO)

# Cria o manipulador de logs para o CloudWatch
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Adiciona o manipulador ao logger
logger.addHandler(ch)

def handler(event, context):
    logger.info(f"Recebido evento do SQS: {json.dumps(event)}")
    dynamodb = AcompanhamentoDB("AcompanhamentoProcesso")
    service = AcompanhamentoService(dynamodb)

    for record in event.get("Records", []):
        message = record["body"]
        logger.info(f"Processando mensagem: {message}")
        service.criar_atualizar_processo(message)

    return {"statusCode": 200, "body": "Mensagens processadas com sucesso"}
