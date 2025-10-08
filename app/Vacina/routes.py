from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def listar_vacinas():
    """Endpoint para listar vacinas disponíveis (mock)."""
    return {"vacinas": ["BCG", "Hepatite B", "COVID-19"]}

@router.post("/")
async def cadastrar_vacina(nome: str):
    """Endpoint para cadastrar uma nova vacina (mock)."""
    return {"message": f"Vacina {nome} cadastrada com sucesso!"}
