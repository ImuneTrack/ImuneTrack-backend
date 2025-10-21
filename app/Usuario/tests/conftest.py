"""Configuração de fixtures para os testes do módulo de Usuário.

Este módulo contém fixtures que são compartilhadas entre os testes,
incluindo configuração do banco de dados e cliente de teste.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Cria todas as tabelas do banco de dados antes da execução dos testes.
    
    Esta fixture é executada uma única vez por sessão de teste e garante que
    todas as tabelas sejam criadas antes dos testes e removidas após.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """Fornece um cliente de teste para fazer requisições à API.
    
    Retorna:
        TestClient: Cliente para fazer requisições HTTP aos endpoints da API.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_session():
    """Fornece uma sessão do banco de dados para cada teste.
    
    A sessão é fechada automaticamente após o término do teste,
    garantindo que não haja vazamento de conexões.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
