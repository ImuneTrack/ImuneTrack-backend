"""Módulo de modelo de dados para a entidade Usuário.

Este módulo define a estrutura da tabela de usuários no banco de dados,
bem como métodos auxiliares para manipulação de senhas.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Usuario(Base):
    """Modelo de dados para a entidade Usuário.
    
    Representa um usuário do sistema com suas informações básicas e métodos
    para manipulação de senhas.
    """
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
        """Retorna uma representação em string do objeto Usuário.
        
        Returns:
            str: Representação do usuário no formato <Usuario(id=X, nome='...', email='...')>
        """
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"

    def to_dict(self) -> dict:
        """Converte o objeto Usuário para um dicionário.
        
        Returns:
            dict: Dicionário contendo os atributos do usuário
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email
        }
    @property
    def senha_hash(self):
        """Getter para a senha do usuário.
        
        Returns:
            str: Hash da senha do usuário
        """
        return self.senha
