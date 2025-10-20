from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class StatusDose(str, enum.Enum):
    PENDENTE = "pendente"
    APLICADA = "aplicada"
    ATRASADA = "atrasada"
    CANCELADA = "cancelada"

# Modelo de Histórico Vacinal
class HistoricoVacinal(Base):
    __tablename__ = "historico_vacinal"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    vacina_id = Column(Integer, ForeignKey("vacinas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informações da dose
    numero_dose = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    status = Column(Enum(StatusDose), default=StatusDose.PENDENTE, nullable=False, index=True)
    
    # Datas
    data_aplicacao = Column(Date, nullable=True, index=True)  # Data em que foi aplicada
    data_prevista = Column(Date, nullable=True)  # Data prevista para aplicação
    
    # Informações adicionais
    lote = Column(String(50), nullable=True)  # Lote da vacina
    local_aplicacao = Column(String(200), nullable=True)  # Local onde foi aplicada
    profissional = Column(String(200), nullable=True)  # Nome do profissional
    observacoes = Column(String(500), nullable=True)  # Observações gerais
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="historico_vacinal")
    vacina = relationship("Vacina", back_populates="historico_vacinal")

    def __repr__(self) -> str:
        return (f"<HistoricoVacinal(id={self.id}, usuario_id={self.usuario_id}, "
                f"vacina_id={self.vacina_id}, dose={self.numero_dose}, status='{self.status}')>")

    def to_dict(self) -> dict:
        """Converte o objeto para dicionário."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "vacina_id": self.vacina_id,
            "vacina_nome": self.vacina.nome if self.vacina else None,
            "numero_dose": self.numero_dose,
            "status": self.status.value,
            "data_aplicacao": self.data_aplicacao.isoformat() if self.data_aplicacao else None,
            "data_prevista": self.data_prevista.isoformat() if self.data_prevista else None,
            "lote": self.lote,
            "local_aplicacao": self.local_aplicacao,
            "profissional": self.profissional,
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }