from sqlalchemy.orm import Session
from app.Vacina.model import Vacina

def listar_vacinas(db: Session):
    """Retorna todas as vacinas cadastradas no banco de dados."""
    return db.query(Vacina).all()

def adicionar_vacina(db: Session, nome: str, doses: int):
    """Adiciona uma nova vacina ao banco de dados."""
    vacina = Vacina(nome=nome, doses=doses)
    db.add(vacina)
    db.commit()
    db.refresh(vacina)
    return vacina
