""" Controlador para operações do histórico vacinal """
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, extract
from fastapi import HTTPException, status
from app.HistoricoVacina.model import HistoricoVacinal, StatusDose
from app.Vacina.model import Vacina
from app.Usuario.model import Usuario

class HistoricoVacinalController:
    """ Controlador para operações do histórico vacinal """

    @staticmethod
    def criar_registro(
        db: Session,
        usuario_id: int,
        vacina_id: int,
        numero_dose: int,
        status: StatusDose = StatusDose.PENDENTE,
        data_aplicacao: Optional[date] = None,
        data_prevista: Optional[date] = None,
        lote: Optional[str] = None,
        local_aplicacao: Optional[str] = None,
        profissional: Optional[str] = None,
        observacoes: Optional[str] = None
    ) -> HistoricoVacinal:

        # Verifica se usuário já existe
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {usuario_id} não encontrado"
            )

        # Verifica se vacina já existe
        vacina = db.query(Vacina).filter(Vacina.id == vacina_id).first()
        if not vacina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vacina com ID {vacina_id} não encontrada"
            )

        # Valida número da dose
        if numero_dose < 1 or numero_dose > vacina.doses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Número da dose deve estar entre 1 e {vacina.doses}"
            )

        # Verifica se já existe registro dessa dose
        registro_existente = db.query(HistoricoVacinal).filter(
            and_(
                HistoricoVacinal.usuario_id == usuario_id,
                HistoricoVacinal.vacina_id == vacina_id,
                HistoricoVacinal.numero_dose == numero_dose
            )
        ).first()

        # Caso exista, retorna erro
        if registro_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe registro da dose {numero_dose} para esta vacina"
            )

        # Valida data de aplicação
        if data_aplicacao and data_aplicacao > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de aplicação não pode ser no futuro"
            )

        # Cria o registro
        historico = HistoricoVacinal(
            usuario_id=usuario_id,
            vacina_id=vacina_id,
            numero_dose=numero_dose,
            status=status,
            data_aplicacao=data_aplicacao,
            data_prevista=data_prevista,
            lote=lote,
            local_aplicacao=local_aplicacao,
            profissional=profissional,
            observacoes=observacoes
        )

        db.add(historico)
        db.commit()
        db.refresh(historico)
        return historico

    #Lista o histórico vacinal de um usuário com filtros opcionais.
    @staticmethod
    def listar_por_usuario(
        db: Session,
        usuario_id: int,
        ano: Optional[int] = None,
        vacina_id: Optional[int] = None,
        status_filtro: Optional[StatusDose] = None,
        mes: Optional[int] = None
    ) -> List[HistoricoVacinal]:
        """ Lista o histórico vacinal de um usuário com filtros opcionais."""
        query = db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(HistoricoVacinal.usuario_id == usuario_id)

        # Aplica filtros para ano, mês, vacina e status
        if ano:
            query = query.filter(
                extract('year', HistoricoVacinal.data_aplicacao) == ano
            )

        if mes:
            query = query.filter(
                extract('month', HistoricoVacinal.data_aplicacao) == mes
            )

        if vacina_id:
            query = query.filter(HistoricoVacinal.vacina_id == vacina_id)

        if status_filtro:
            query = query.filter(HistoricoVacinal.status == status_filtro)

        return query.order_by(
            HistoricoVacinal.data_aplicacao.desc().nullslast(),
            HistoricoVacinal.created_at.desc()
        ).all()

    # Busca um registro específico do histórico vacinal por ID.
    @staticmethod
    def buscar_por_id(db: Session, historico_id: int, usuario_id: int) -> Optional[HistoricoVacinal]:
        """ Busca um registro específico do histórico vacinal por ID."""
        return db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(
            and_(
                HistoricoVacinal.id == historico_id,
                HistoricoVacinal.usuario_id == usuario_id
            )
        ).first()

    @staticmethod
    def atualizar_registro(
        db: Session,
        historico_id: int,
        usuario_id: int,
        numero_dose: Optional[int] = None,
        status_novo: Optional[StatusDose] = None,
        data_aplicacao: Optional[date] = None,
        data_prevista: Optional[date] = None,
        lote: Optional[str] = None,
        local_aplicacao: Optional[str] = None,
        profissional: Optional[str] = None,
        observacoes: Optional[str] = None
    ) -> HistoricoVacinal:
        """ Atualiza um registro do histórico vacinal."""
        historico = HistoricoVacinalController.buscar_por_id(db, historico_id, usuario_id)
        if not historico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro com ID {historico_id} não encontrado"
            )

        # Atualiza campos se fornecidos
        if numero_dose is not None:
            vacina = historico.vacina
            if numero_dose < 1 or numero_dose > vacina.doses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Número da dose deve estar entre 1 e {vacina.doses}"
                )
            historico.numero_dose = numero_dose

        if status_novo is not None:
            historico.status = status_novo

        if data_aplicacao is not None:
            if data_aplicacao > date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Data de aplicação não pode ser no futuro"
                )
            historico.data_aplicacao = data_aplicacao

        if data_prevista is not None:
            historico.data_prevista = data_prevista

        if lote is not None:
            historico.lote = lote

        if local_aplicacao is not None:
            historico.local_aplicacao = local_aplicacao

        if profissional is not None:
            historico.profissional = profissional

        if observacoes is not None:
            historico.observacoes = observacoes

        db.commit()
        db.refresh(historico)
        return historico

    @staticmethod
    def deletar_registro(db: Session, historico_id: int, usuario_id: int) -> bool:
        """ Deleta um registro do histórico vacinal."""
        historico = HistoricoVacinalController.buscar_por_id(db, historico_id, usuario_id)
        if not historico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro com ID {historico_id} não encontrado"
            )

        db.delete(historico)
        db.commit()
        return True

    @staticmethod
    def obter_estatisticas(db: Session, usuario_id: int) -> dict:
        """ Obtem estatísticas do histórico vacinal."""
        historico = db.query(HistoricoVacinal).filter(
            HistoricoVacinal.usuario_id == usuario_id
        ).all()

        total_doses = len(historico)
        doses_aplicadas = len([h for h in historico if h.status == StatusDose.APLICADA])
        doses_pendentes = len([h for h in historico if h.status == StatusDose.PENDENTE])
        doses_atrasadas = len([h for h in historico if h.status == StatusDose.ATRASADA])
        doses_canceladas = len([h for h in historico if h.status == StatusDose.CANCELADA])

        # Agrupa por vacina
        vacinas_dict = {}
        for h in historico:
            if h.vacina_id not in vacinas_dict:
                vacinas_dict[h.vacina_id] = {
                    'total_doses': h.vacina.doses,
                    'aplicadas': 0
                }
            if h.status == StatusDose.APLICADA:
                vacinas_dict[h.vacina_id]['aplicadas'] += 1

        vacinas_completas = sum(1 for v in vacinas_dict.values() if v['aplicadas'] >= v['total_doses'])
        vacinas_incompletas = len(vacinas_dict) - vacinas_completas

        # Próximas doses a serem aplicadas
        proximas = db.query(HistoricoVacinal).options(
            joinedload(HistoricoVacinal.vacina)
        ).filter(
            and_(
                HistoricoVacinal.usuario_id == usuario_id,
                HistoricoVacinal.status == StatusDose.PENDENTE,
                HistoricoVacinal.data_prevista.isnot(None)
            )
        ).order_by(HistoricoVacinal.data_prevista).limit(5).all()

        proximas_doses = [
            {
                "vacina": h.vacina.nome,
                "dose": h.numero_dose,
                "data_prevista": h.data_prevista.isoformat()
            }
            for h in proximas
        ]

        return {
            "total_doses": total_doses,
            "doses_aplicadas": doses_aplicadas,
            "doses_pendentes": doses_pendentes,
            "doses_atrasadas": doses_atrasadas,
            "doses_canceladas": doses_canceladas,
            "vacinas_completas": vacinas_completas,
            "vacinas_incompletas": vacinas_incompletas,
            "proximas_doses": proximas_doses
        }

    @staticmethod
    def marcar_dose_como_aplicada(
        db: Session,
        historico_id: int,
        usuario_id: int,
        data_aplicacao: date,
        lote: Optional[str] = None,
        local_aplicacao: Optional[str] = None,
        profissional: Optional[str] = None
    ) -> HistoricoVacinal:
        """ Marca uma dose como aplicada."""
        return HistoricoVacinalController.atualizar_registro(
            db=db,
            historico_id=historico_id,
            usuario_id=usuario_id,
            status_novo=StatusDose.APLICADA,
            data_aplicacao=data_aplicacao,
            lote=lote,
            local_aplicacao=local_aplicacao,
            profissional=profissional
        )
