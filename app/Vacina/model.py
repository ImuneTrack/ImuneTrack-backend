from sqlalchemy import Column, Integer, String
from app.database import Base

class Vacina(Base):
    """Modelo ORM para a tabela de vacinas."""
    __tablename__ = "vacinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    doses = Column(Integer, nullable=False)
