"""Módulo principal da aplicação ImuneTrack."""
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from app.database import Base, engine
from app.Usuario.routes import router as usuario_router
from app.Vacina.routes import router as vacina_router
from app.HistoricoVacina.routes import router as historico_router
from app.Auth.routes import router as auth_router

def criar_tabelas_com_retry(retries=10, delay=3):
    """Cria tabelas no banco de dados com retry caso o banco ainda não esteja pronto."""
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas com sucesso!")
            break
        except OperationalError:
            print(f"[{i+1}/{retries}] Banco ainda não pronto, tentando novamente em {delay}s...")
            time.sleep(delay)
    else:
        raise RuntimeError("Não foi possível conectar ao banco de dados após várias tentativas.")

criar_tabelas_com_retry()

app = FastAPI(title="ImuneTrack API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(vacina_router)
app.include_router(historico_router, prefix="/usuarios")

@app.get("/")
async def root():
    """endpoint raiz"""
    return {"message": "Bem-vindo ao ImuneTrack!"}