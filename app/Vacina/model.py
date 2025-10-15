from sqlalchemy import Column, Integer, String
from app.database import Base


class Vacina(Base):
    __tablename__ = "vacinas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    doses = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Vacina(id={self.id}, nome='{self.nome}', doses={self.doses})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "doses": self.doses
        }

