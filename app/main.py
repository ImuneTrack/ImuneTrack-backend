"""Módulo principal que inicializa a aplicação FastAPI e inclui os routers de Vacinas e Usuários."""

from fastapi import FastAPI
from routes import vacina_router, usuario_router

app = FastAPI(title="ImuneTrack API")

# Inclui as rotas de vacinas e usuários
app.include_router(vacina_router, prefix="/vacinas", tags=["Vacinas"])
app.include_router(usuario_router, prefix="/usuarios", tags=["Usuarios"])

@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {"message": "Bem-vindo ao ImuneTrack!"}
