from sqlalchemy.orm import Session
from app.Usuario.model import Usuario

def listar_usuarios(db: Session):
    """Retorna todos os usuários cadastrados no banco de dados."""
    return db.query(Usuario).all()

def adicionar_usuario(db: Session, nome: str, email: str, senha: str):
    """Adiciona um novo usuário ao banco de dados."""
    usuario = Usuario(nome=nome, email=email, senha=senha)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
