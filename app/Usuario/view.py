from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def listar_usuarios():
    """Endpoint para listar usuários disponíveis (mock)."""
    return {"usuarios": ["Alice", "Bob", "Carlos"]}

@router.post("/")
async def cadastrar_usuario(nome: str):
    """Endpoint para cadastrar um novo usuário (mock)."""
    return {"message": f"Usuário {nome} cadastrado com sucesso!"}
