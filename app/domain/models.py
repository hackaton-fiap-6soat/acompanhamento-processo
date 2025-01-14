from datetime import datetime
from typing import Dict
from pydantic import BaseModel

class Processo(BaseModel):
    id_status: int
    status_processo: str
    timestamp_processo: datetime

class ProcessosUsuario(BaseModel):
    id_usuario: str
    processos: Dict[str, Processo]