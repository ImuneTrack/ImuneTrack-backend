from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com histórico vacinal
    historico_vacinal = relationship(
        "HistoricoVacinal", 
        back_populates="usuario", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email
        }

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email
        }

    @property
    def senha_hash(self):
        return self.senha