from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    HistoricoVacinalCreate,
    HistoricoVacinalUpdate,
    HistoricoVacinalResponse,
    HistoricoVacinalCompleto,
    EstatisticasHistorico,
    ErrorResponse,
    StatusDoseEnum
)
from app.HistoricoVacina.controller import HistoricoVacinalController
from app.HistoricoVacina.model import StatusDose
from datetime import date

router = APIRouter(prefix="/{usuario_id}/historico", tags=["Histórico Vacinal"])

# Listar histórico vacinal com filtros
@router.get(
    "/",
    response_model=List[HistoricoVacinalCompleto],
    status_code=status.HTTP_200_OK,
    summary="Listar histórico vacinal do usuário",
    description="Retorna o histórico vacinal completo do usuário com filtros opcionais"
)
async def listar_historico(
    usuario_id: int = Path(..., description="ID do usuário"),
    ano: Optional[int] = Query(None, ge=1900, le=2100),
    mes: Optional[int] = Query(None, ge=1, le=12),
    vacina_id: Optional[int] = Query(None),
    status_filtro: Optional[StatusDoseEnum] = Query(None),
    db: Session = Depends(get_db)
):    
    # Converte string do enum para o enum do modelo
    status_model = None
    if status_filtro:
        status_model = StatusDose(status_filtro.value)
    
    historico = HistoricoVacinalController.listar_por_usuario(
        db=db,
        usuario_id=usuario_id,
        ano=ano,
        mes=mes,
        vacina_id=vacina_id,
        status_filtro=status_model
    )
    
    # Converte para o formato de resposta completo
    resultado = []
    for h in historico:
        resultado.append({
            "id": h.id,
            "usuario_id": h.usuario_id,
            "vacina_id": h.vacina_id,
            "vacina_nome": h.vacina.nome,
            "vacina_doses_totais": h.vacina.doses,
            "numero_dose": h.numero_dose,
            "status": h.status,
            "data_aplicacao": h.data_aplicacao,
            "data_prevista": h.data_prevista,
            "lote": h.lote,
            "local_aplicacao": h.local_aplicacao,
            "profissional": h.profissional,
            "observacoes": h.observacoes,
            "created_at": h.created_at,
            "updated_at": h.updated_at
        })
    
    return resultado


@router.get(
    "/estatisticas",
    response_model=EstatisticasHistorico,
    status_code=status.HTTP_200_OK,
    summary="Obter estatísticas do histórico vacinal",
    description="Retorna estatísticas e resumo do histórico vacinal do usuário"
)
async def obter_estatisticas(
    usuario_id: int,
    db: Session = Depends(get_db)
):    
    estatisticas = HistoricoVacinalController.obter_estatisticas(db, usuario_id)
    return estatisticas


@router.get(
    "/{historico_id}",
    response_model=HistoricoVacinalCompleto,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}},
    summary="Buscar registro específico do histórico",
    description="Retorna detalhes de um registro específico do histórico vacinal"
)
async def buscar_registro(
    usuario_id: int,
    historico_id: int,
    db: Session = Depends(get_db)
):
    historico = HistoricoVacinalController.buscar_por_id(db, historico_id, usuario_id)
    if not historico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro com ID {historico_id} não encontrado"
        )
    
    return {
        "id": historico.id,
        "usuario_id": historico.usuario_id,
        "vacina_id": historico.vacina_id,
        "vacina_nome": historico.vacina.nome,
        "vacina_doses_totais": historico.vacina.doses,
        "numero_dose": historico.numero_dose,
        "status": historico.status,
        "data_aplicacao": historico.data_aplicacao,
        "data_prevista": historico.data_prevista,
        "lote": historico.lote,
        "local_aplicacao": historico.local_aplicacao,
        "profissional": historico.profissional,
        "observacoes": historico.observacoes,
        "created_at": historico.created_at,
        "updated_at": historico.updated_at
    }


@router.post(
    "/",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Adicionar registro ao histórico vacinal",
    description="Cria um novo registro de dose no histórico vacinal do usuário"
)
async def criar_registro(
    usuario_id: int,
    historico: HistoricoVacinalCreate,
    db: Session = Depends(get_db)
):
    
    status_model = StatusDose(historico.status.value)
    
    novo_registro = HistoricoVacinalController.criar_registro(
        db=db,
        usuario_id=usuario_id,
        vacina_id=historico.vacina_id,
        numero_dose=historico.numero_dose,
        status=status_model,
        data_aplicacao=historico.data_aplicacao,
        data_prevista=historico.data_prevista,
        lote=historico.lote,
        local_aplicacao=historico.local_aplicacao,
        profissional=historico.profissional,
        observacoes=historico.observacoes
    )
    
    return {
        "id": novo_registro.id,
        "usuario_id": novo_registro.usuario_id,
        "vacina_id": novo_registro.vacina_id,
        "vacina_nome": novo_registro.vacina.nome,
        "numero_dose": novo_registro.numero_dose,
        "status": novo_registro.status,
        "data_aplicacao": novo_registro.data_aplicacao,
        "data_prevista": novo_registro.data_prevista,
        "lote": novo_registro.lote,
        "local_aplicacao": novo_registro.local_aplicacao,
        "profissional": novo_registro.profissional,
        "observacoes": novo_registro.observacoes,
        "created_at": novo_registro.created_at,
        "updated_at": novo_registro.updated_at
    }


@router.put(
    "/{historico_id}",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Atualizar registro do histórico",
    description="Atualiza um registro existente no histórico vacinal"
)
async def atualizar_registro(
    usuario_id: int,
    historico_id: int,
    historico: HistoricoVacinalUpdate,
    db: Session = Depends(get_db)
):    
    status_model = None
    if historico.status:
        status_model = StatusDose(historico.status.value)
    
    registro_atualizado = HistoricoVacinalController.atualizar_registro(
        db=db,
        historico_id=historico_id,
        usuario_id=usuario_id,
        numero_dose=historico.numero_dose,
        status_novo=status_model,
        data_aplicacao=historico.data_aplicacao,
        data_prevista=historico.data_prevista,
        lote=historico.lote,
        local_aplicacao=historico.local_aplicacao,
        profissional=historico.profissional,
        observacoes=historico.observacoes
    )
    
    return {
        "id": registro_atualizado.id,
        "usuario_id": registro_atualizado.usuario_id,
        "vacina_id": registro_atualizado.vacina_id,
        "vacina_nome": registro_atualizado.vacina.nome,
        "numero_dose": registro_atualizado.numero_dose,
        "status": registro_atualizado.status,
        "data_aplicacao": registro_atualizado.data_aplicacao,
        "data_prevista": registro_atualizado.data_prevista,
        "lote": registro_atualizado.lote,
        "local_aplicacao": registro_atualizado.local_aplicacao,
        "profissional": registro_atualizado.profissional,
        "observacoes": registro_atualizado.observacoes,
        "created_at": registro_atualizado.created_at,
        "updated_at": registro_atualizado.updated_at
    }


@router.patch(
    "/{historico_id}/aplicar",
    response_model=HistoricoVacinalResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Marcar dose como aplicada",
    description="Marca uma dose pendente como aplicada com informações da aplicação"
)
async def marcar_como_aplicada(
    usuario_id: int,
    historico_id: int,
    data_aplicacao: date = Query(..., description="Data em que a dose foi aplicada"),
    lote: Optional[str] = Query(None, description="Lote da vacina"),
    local_aplicacao: Optional[str] = Query(None, description="Local onde foi aplicada"),
    profissional: Optional[str] = Query(None, description="Nome do profissional"),
    db: Session = Depends(get_db)
):    
    registro_atualizado = HistoricoVacinalController.marcar_dose_como_aplicada(
        db=db,
        historico_id=historico_id,
        usuario_id=usuario_id,
        data_aplicacao=data_aplicacao,
        lote=lote,
        local_aplicacao=local_aplicacao,
        profissional=profissional
    )
    
    return {
        "id": registro_atualizado.id,
        "usuario_id": registro_atualizado.usuario_id,
        "vacina_id": registro_atualizado.vacina_id,
        "vacina_nome": registro_atualizado.vacina.nome,
        "numero_dose": registro_atualizado.numero_dose,
        "status": registro_atualizado.status,
        "data_aplicacao": registro_atualizado.data_aplicacao,
        "data_prevista": registro_atualizado.data_prevista,
        "lote": registro_atualizado.lote,
        "local_aplicacao": registro_atualizado.local_aplicacao,
        "profissional": registro_atualizado.profissional,
        "observacoes": registro_atualizado.observacoes,
        "created_at": registro_atualizado.created_at,
        "updated_at": registro_atualizado.updated_at
    }


@router.delete(
    "/{historico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Deletar registro do histórico",
    description="Remove um registro do histórico vacinal"
)
async def deletar_registro(
    usuario_id: int,
    historico_id: int,
    db: Session = Depends(get_db)
):    
    HistoricoVacinalController.deletar_registro(db, historico_id, usuario_id)
    return None