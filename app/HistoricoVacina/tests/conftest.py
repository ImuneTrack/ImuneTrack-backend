import os
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import SessionLocal, Base, engine

# Detecta ambiente (padrão = dev)
ENV = os.getenv("ENV", "dev")

# Define a URL de banco com base no ambiente
if ENV == "test":
    DATABASE_URL = "sqlite:///./test_imunetrack.db"
    connect_args = {"check_same_thread": False}
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://imunetrack_user:imunetrack_pass@db:5432/imunetrack_user"
    )
    connect_args = {}

# Cria engine e sessão
engine = create_engine(DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
# Cria o banco de dados para os testes
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
# Fornece uma sessão de banco de dados para cada teste
def db_session(db_engine: Engine):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)