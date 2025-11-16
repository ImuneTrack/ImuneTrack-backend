"""Rotas de autenticação."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.Usuario.controller import UsuarioController
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Autenticação"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    password: str

@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registra um novo usuário."""
    usuario = UsuarioController.criar(
        db=db,
        nome=data.nome,
        email=data.email,
        senha=data.password
    )
    return {
        "message": "Usuário criado com sucesso",
        "user": usuario.to_dict()
    }

@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Faz login do usuário."""
    usuario = UsuarioController.autenticar(db, data.email, data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    return {
        "message": "Login realizado com sucesso",
        "user": usuario.to_dict()
    }
