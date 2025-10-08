from fastapi import FastAPI
from app.database import Base, engine
from app.Usuario import model as usuario_model
from app.Vacina import model as vacina_model
from app.Usuario.routes import router as usuario_router
from app.Vacina.routes import router as vacina_router

# Cria todas as tabelas no banco (se não existirem)
Base.metadata.create_all(bind=engine)

# Cria a aplicação FastAPI
app = FastAPI(title="ImuneTrack API")

# Inclui as rotas
app.include_router(usuario_router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(vacina_router, prefix="/vacinas", tags=["Vacinas"])

# Endpoint raiz
@app.get("/")
async def root():
    return {"message": "Bem-vindo ao ImuneTrack!"}
