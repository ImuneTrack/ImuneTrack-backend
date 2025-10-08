from sqlalchemy.orm import Session
from app.Usuario.model import Usuario

def listar_usuarios(db: Session):
    return db.query(Usuario).all()

def buscar_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def adicionar_usuario(db: Session, nome: str, email: str, senha: str):
    novo_usuario = Usuario(nome=nome, email=email, senha=senha)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {
        "id": novo_usuario.id,
        "nome": novo_usuario.nome,
        "email": novo_usuario.email
    }

def atualizar_usuario(db: Session, usuario_id: int, nome: str = None, email: str = None, senha: str = None):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return None
    
    if nome:
        usuario.nome = nome
    if email:
        usuario.email = email
    if senha:
        usuario.senha = senha
    
    db.commit()
    db.refresh(usuario)
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    }

def deletar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        return None
    
    db.delete(usuario)
    db.commit()
    return {"mensagem": f"Usuário {usuario.nome} removido com sucesso"}
