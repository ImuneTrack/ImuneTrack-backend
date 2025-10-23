"""Testes unitários para o modelo de Usuário."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.Usuario.model import Usuario


class TestUsuarioModel:
    """Testes para o modelo de Usuário."""

    @pytest.fixture
    def engine(self):
        """Configura um banco de dados SQLite em memória para os testes."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """Fornece uma sessão de banco de dados para cada teste."""
        session_factory = sessionmaker(bind=engine)
        db_session = session_factory()
        yield db_session
        db_session.close()

    def test_criar_usuario(self, session):
        """Deve criar um novo usuário com sucesso."""
        usuario = Usuario(
            nome="Alice Silva",
            email="alice@test.com",
            senha="hashed_password"
        )
        session.add(usuario)
        session.commit()

        assert usuario.id is not None
        assert usuario.nome == "Alice Silva"
        assert usuario.email == "alice@test.com"

    def test_usuario_repr(self):
        """Deve retornar uma representação em string do usuário."""
        usuario = Usuario(id=1, nome="Alice", email="alice@test.com", senha="hash")
        repr_str = repr(usuario)

        assert "Usuario" in repr_str
        assert "Alice" in repr_str
        assert "alice@test.com" in repr_str

    def test_usuario_to_dict(self):
        """Deve converter o usuário para dicionário corretamente."""
        usuario = Usuario(
            id=1,
            nome="Alice Silva",
            email="alice@test.com",
            senha="hashed_password"
        )
        user_dict = usuario.to_dict()

        assert user_dict["id"] == 1
        assert user_dict["nome"] == "Alice Silva"
        assert user_dict["email"] == "alice@test.com"
        assert "senha" not in user_dict  # Senha não deve aparecer

    def test_email_unico(self, session):
        """Deve garantir que o email seja único no sistema."""
        usuario1 = Usuario(nome="Alice", email="alice@test.com", senha="hash1")
        session.add(usuario1)
        session.commit()

        usuario2 = Usuario(nome="Bob", email="alice@test.com", senha="hash2")
        session.add(usuario2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_campos_obrigatorios(self, session):
        """Deve exigir nome e email para criar um usuário."""
        # Nome obrigatório
        usuario = Usuario(email="test@test.com", senha="hash")
        session.add(usuario)
        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

        # Email obrigatório
        usuario = Usuario(nome="Test", senha="hash")
        session.add(usuario)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_buscar_usuario_por_id(self, session):
        """Deve buscar um usuário pelo ID com sucesso."""
        usuario = Usuario(nome="Alice", email="alice@test.com", senha="hash")
        session.add(usuario)
        session.commit()

        usuario_encontrado = session.query(Usuario).filter(
            Usuario.id == usuario.id
        ).first()

        assert usuario_encontrado is not None
        assert usuario_encontrado.nome == "Alice"

    def test_buscar_usuario_por_email(self, session):
        """Deve buscar um usuário pelo email com sucesso."""
        usuario = Usuario(nome="Alice", email="alice@test.com", senha="hash")
        session.add(usuario)
        session.commit()

        usuario_encontrado = session.query(Usuario).filter(
            Usuario.email == "alice@test.com"
        ).first()

        assert usuario_encontrado is not None
        assert usuario_encontrado.nome == "Alice"

    def test_atualizar_usuario(self, session):
        """Deve atualizar os dados de um usuário existente."""
        usuario = Usuario(nome="Alice", email="alice@test.com", senha="hash")
        session.add(usuario)
        session.commit()

        usuario.nome = "Alice Silva"
        usuario.email = "alice.silva@test.com"
        session.commit()

        usuario_atualizado = session.query(Usuario).filter(
            Usuario.id == usuario.id
        ).first()

        assert usuario_atualizado.nome == "Alice Silva"
        assert usuario_atualizado.email == "alice.silva@test.com"

    def test_deletar_usuario(self, session):
        """Deve remover um usuário do banco de dados."""
        usuario = Usuario(nome="Alice", email="alice@test.com", senha="hash")
        session.add(usuario)
        session.commit()

        usuario_id = usuario.id
        session.delete(usuario)
        session.commit()

        usuario_deletado = session.query(Usuario).filter(
            Usuario.id == usuario_id
        ).first()

        assert usuario_deletado is None

    @pytest.mark.parametrize("nome,email,senha", [
        ("Alice", "alice@test.com", "hash123"),
        ("Bob Silva", "bob.silva@empresa.com.br", "hash456"),
        ("Carlos", "carlos+tag@domain.co", "hash789"),
    ])
    def test_criar_multiplos_usuarios(self, session, nome, email, senha):
        """Deve criar múltiplos usuários com dados diferentes."""
        usuario = Usuario(nome=nome, email=email, senha=senha)
        session.add(usuario)
        session.commit()

        assert usuario.id is not None
        assert usuario.email == email
