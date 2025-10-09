import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# URL do banco de dados obtida de variável de ambiente ou valor padrão
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://imunetrack_user:imunetrack_pass@db:5432/imunetrack"
)

# Criação do engine e sessão do banco
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
