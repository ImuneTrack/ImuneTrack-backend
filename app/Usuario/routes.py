from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.Usuario.controller import adicionar_usuario

router = APIRouter()

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/usuarios/")
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    novo_usuario = adicionar_usuario(db, usuario.nome, usuario.email, usuario.senha)
    return {
        "id": novo_usuario.id,
        "nome": novo_usuario.nome,
        "email": novo_usuario.email
    }