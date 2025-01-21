import logging
from fastapi import FastAPI
from mangum import Mangum

from app.adapter.api.api_v1.endpoints.adapters_in import router as api_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name="AcompanhamentoProcesso")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

app.include_router(api_router, prefix="/api/v1/")
handler = Mangum(app)