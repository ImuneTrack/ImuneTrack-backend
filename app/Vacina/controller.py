"""Controlador para operações relacionadas a vacinas.

Este módulo contém a lógica de negócios para gerenciar vacinas no sistema,
incluindo criação, leitura, atualização e remoção de registros de vacinas.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.Vacina.model import Vacina


class VacinaValidator:
    """Classe auxiliar para validação de dados de vacina."""

    @staticmethod
    def validar_nome(nome: str) -> bool:
        """Valida o nome da vacina.
        
        Args:
            nome: Nome da vacina a ser validado
            
        Returns:
            bool: True se o nome for válido, False caso contrário
        """
        return bool(nome and 0 < len(nome.strip())) <= 100

    @staticmethod
    def validar_doses(doses: int) -> bool:
        """Valida o número de doses da vacina.
        
        Args:
            doses: Número de doses a ser validado
            
        Returns:
            bool: True se o número de doses for válido, False caso contrário
        """
        return 0 < doses <= 10


class VacinaController:
    """Controlador para operações CRUD de vacinas."""

    @staticmethod
    def listar_todas(db: Session) -> List[Vacina]:
        """Lista todas as vacinas cadastradas.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            List[Vacina]: Lista de todas as vacinas
        """
        return db.query(Vacina).all()

    @staticmethod
    def buscar_por_id(db: Session, vacina_id: int) -> Optional[Vacina]:
        """Busca uma vacina pelo ID.
        
        Args:
            db: Sessão do banco de dados
            vacina_id: ID da vacina a ser buscada
            
        Returns:
            Optional[Vacina]: A vacina encontrada ou None se não existir
        """
        return db.query(Vacina).filter(Vacina.id == vacina_id).first()

    @staticmethod
    def buscar_por_nome(db: Session, nome: str) -> Optional[Vacina]:
        """Busca uma vacina pelo nome.
        
        Args:
            db: Sessão do banco de dados
            nome: Nome da vacina a ser buscada
            
        Returns:
            Optional[Vacina]: A vacina encontrada ou None se não existir
        """
        return db.query(Vacina).filter(Vacina.nome == nome).first()

    @staticmethod
    def criar(db: Session, nome: str, doses: int) -> Vacina:
        """Cria uma nova vacina.
        
        Args:
            db: Sessão do banco de dados
            nome: Nome da vacina
            doses: Número de doses necessárias
            
        Returns:
            Vacina: A vacina criada
            
        Raises:
            HTTPException: Se os dados forem inválidos ou já existir uma vacina com o mesmo nome
        """
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
        """Atualiza os dados de uma vacina existente.
        
        Args:
            db: Sessão do banco de dados
            vacina_id: ID da vacina a ser atualizada
            nome: Novo nome da vacina (opcional)
            doses: Novo número de doses (opcional)
            
        Returns:
            Vacina: A vacina atualizada
            
        Raises:
            HTTPException: Se a vacina não for encontrada ou os dados forem inválidos
        """
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
        """Remove uma vacina do sistema.
        
        Args:
            db: Sessão do banco de dados
            vacina_id: ID da vacina a ser removida
            
        Returns:
            bool: True se a remoção foi bem-sucedida
            
        Raises:
            HTTPException: Se a vacina não for encontrada
        """
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
        """Busca vacinas pelo número de doses.
        
        Args:
            db: Sessão do banco de dados
            doses: Número de doses para filtrar
            
        Returns:
            List[Vacina]: Lista de vacinas com o número de doses especificado
        """
        return db.query(Vacina).filter(Vacina.doses == doses).all()
