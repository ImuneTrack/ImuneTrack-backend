from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.Vacina.model import Vacina


class VacinaValidator:
    @staticmethod
    def validar_nome(nome: str) -> bool:
        return nome and len(nome.strip()) > 0 and len(nome) <= 100

    @staticmethod
    def validar_doses(doses: int) -> bool:
        return doses > 0 and doses <= 10


class VacinaController:
    @staticmethod
    def listar_todas(db: Session) -> List[Vacina]:
        return db.query(Vacina).all()

    @staticmethod
    def buscar_por_id(db: Session, vacina_id: int) -> Optional[Vacina]:
        return db.query(Vacina).filter(Vacina.id == vacina_id).first()

    @staticmethod
    def buscar_por_nome(db: Session, nome: str) -> Optional[Vacina]:
        return db.query(Vacina).filter(Vacina.nome == nome).first()

    @staticmethod
    def criar(db: Session, nome: str, doses: int) -> Vacina:
        # Validações
        if not VacinaValidator.validar_nome(nome):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome da vacina é obrigatório e deve ter no máximo 100 caracteres"
            )

        if not VacinaValidator.validar_doses(doses):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de doses deve ser entre 1 e 10"
            )

        # Verifica duplicidade
        if VacinaController.buscar_por_nome(db, nome):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vacina com nome '{nome}' já existe"
            )

        # Cria vacina
        vacina = Vacina(nome=nome.strip(), doses=doses)
        try:
            db.add(vacina)
            db.commit()
            db.refresh(vacina)
            return vacina
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar vacina"
            ) from e

    @staticmethod
    def atualizar(
        db: Session,
        vacina_id: int,
        nome: Optional[str] = None,
        doses: Optional[int] = None
    ) -> Vacina:
        vacina = VacinaController.buscar_por_id(db, vacina_id)
        if not vacina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vacina com ID {vacina_id} não encontrada"
            )

        # Valida e atualiza nome
        if nome is not None:
            if not VacinaValidator.validar_nome(nome):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome da vacina inválido"
                )
            # Verifica se nome já existe em outra vacina
            vacina_existente = VacinaController.buscar_por_nome(db, nome)
            if vacina_existente and vacina_existente.id != vacina_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe outra vacina com o nome '{nome}'"
                )
            vacina.nome = nome.strip()

        # Valida e atualiza doses
        if doses is not None:
            if not VacinaValidator.validar_doses(doses):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Número de doses deve ser entre 1 e 10"
                )
            vacina.doses = doses

        try:
            db.commit()
            db.refresh(vacina)
            return vacina
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao atualizar vacina"
            ) from e

    @staticmethod
    def deletar(db: Session, vacina_id: int) -> bool:
        vacina = VacinaController.buscar_por_id(db, vacina_id)
        if not vacina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vacina com ID {vacina_id} não encontrada"
            )

        db.delete(vacina)
        db.commit()
        return True

    @staticmethod
    def buscar_por_doses(db: Session, doses: int) -> List[Vacina]:
        return db.query(Vacina).filter(Vacina.doses == doses).all()

