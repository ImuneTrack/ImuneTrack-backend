from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

# ==================== SCHEMAS DE VACINA ====================

class VacinaBase(BaseModel):
    """Schema base para Vacina."""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da vacina")
    doses: int = Field(..., gt=0, le=10, description="Número de doses necessárias")


class VacinaCreate(VacinaBase):
    """Schema para criação de Vacina."""
    pass


class VacinaUpdate(BaseModel):
    """Schema para atualização de Vacina."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    doses: Optional[int] = Field(None, gt=0, le=10)


class VacinaResponse(VacinaBase):
    """Schema para resposta de Vacina."""
    id: int

    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    """Schema base para Usuario."""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome completo", example="Alice Silva")
    email: EmailStr = Field(..., description="Email válido", example="alice@teste.com")

    def nome_nao_vazio(cls, v):
        """Valida que nome não é apenas espaços."""
        if not v or not v.strip():
            raise ValueError('Nome não pode ser vazio')
        return v.strip()

    def email_lowercase(cls, v):
        """Converte email para minúsculas."""
        return v.lower()


class UsuarioCreate(UsuarioBase):
    """Schema para criação de Usuario."""
    senha: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Senha com no mínimo 6 caracteres"
    )

    def senha_forte(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve conter ao menos um número')
        if not any(c.isalpha() for c in v):
            raise ValueError('Senha deve conter ao menos uma letra')
        return v


class UsuarioUpdate(BaseModel):
    """Schema para atualização de Usuario."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(None, min_length=6, max_length=100)

    def nome_nao_vazio(cls, v):
        """Valida que nome não é apenas espaços."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Nome não pode ser vazio')
        return v.strip() if v else v
    
    def email_lowercase(cls, v):
        """Converte email para minúsculas."""
        return v.lower() if v else v


class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


# ==================== SCHEMAS DE ERRO ====================

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Descrição do erro")


class MessageResponse(BaseModel):
    message: str = Field(..., description="Mensagem de sucesso")


# ==================== TESTES UNITÁRIOS ====================
import pytest
from pydantic import ValidationError


class TestVacinaSchemas:

    def test_vacina_create_valido(self):
        vacina = VacinaCreate(nome="BCG", doses=1)
        assert vacina.nome == "BCG"
        assert vacina.doses == 1

    def test_vacina_create_nome_vazio(self):
        with pytest.raises(ValidationError) as exc_info:
            VacinaCreate(nome="", doses=1)
        assert "nome" in str(exc_info.value).lower()

    def test_vacina_create_doses_zero(self):
        with pytest.raises(ValidationError) as exc_info:
            VacinaCreate(nome="BCG", doses=0)
        assert "doses" in str(exc_info.value).lower()

    def test_vacina_create_doses_negativa(self):
        with pytest.raises(ValidationError) as exc_info:
            VacinaCreate(nome="BCG", doses=-1)
        assert "doses" in str(exc_info.value).lower()

    def test_vacina_create_doses_acima_limite(self):
        with pytest.raises(ValidationError) as exc_info:
            VacinaCreate(nome="BCG", doses=11)
        assert "doses" in str(exc_info.value).lower()

    def test_vacina_update_campos_opcionais(self):
        vacina = VacinaUpdate(nome="Nova BCG")
        assert vacina.nome == "Nova BCG"
        assert vacina.doses is None

        vacina2 = VacinaUpdate(doses=2)
        assert vacina2.nome is None
        assert vacina2.doses == 2

    @pytest.mark.parametrize("nome,doses,valido", [
        ("BCG", 1, True),
        ("Hepatite B", 3, True),
        ("COVID-19", 2, True),
        ("Tríplice Viral", 10, True),
        ("", 1, False),
        ("BCG", 0, False),
        ("BCG", 11, False),
    ])
    def test_vacina_create_parametrizado(self, nome, doses, valido):
        if valido:
            vacina = VacinaCreate(nome=nome, doses=doses)
            assert vacina.nome == nome
            assert vacina.doses == doses
        else:
            with pytest.raises(ValidationError):
                VacinaCreate(nome=nome, doses=doses)


class TestUsuarioSchemas:

    def test_usuario_create_valido(self):
        usuario = UsuarioCreate(
            nome="Alice Silva",
            email="alice@test.com",
            senha="senha123"
        )
        assert usuario.nome == "Alice Silva"
        assert usuario.email == "alice@test.com"
        assert usuario.senha == "senha123"

    def test_usuario_create_email_lowercase(self):
        """Deve converter email para lowercase."""
        usuario = UsuarioCreate(
            nome="Alice",
            email="Alice@TEST.COM",
            senha="senha123"
        )
        assert usuario.email == "alice@test.com"

    def test_usuario_create_nome_com_espacos(self):
        usuario = UsuarioCreate(
            nome="  Alice Silva  ",
            email="alice@test.com",
            senha="senha123"
        )
        assert usuario.nome == "Alice Silva"

    def test_usuario_create_nome_vazio(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="", email="alice@test.com", senha="senha123")

    def test_usuario_create_nome_apenas_espacos(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="   ", email="alice@test.com", senha="senha123")

    def test_usuario_create_email_invalido(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="Alice", email="email_invalido", senha="senha123")

    def test_usuario_create_senha_curta(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="Alice", email="alice@test.com", senha="123")

    def test_usuario_update_campos_opcionais(self):
        usuario = UsuarioUpdate(nome="Alice Silva")
        assert usuario.nome == "Alice Silva"
        assert usuario.email is None
        assert usuario.senha is None

        usuario2 = UsuarioUpdate(email="alice@new.com")
        assert usuario2.nome is None
        assert usuario2.email == "alice@new.com"

        usuario3 = UsuarioUpdate(senha="nova_senha")
        assert usuario3.senha == "nova_senha"

    def test_usuario_response_sem_senha(self):
        usuario = UsuarioResponse(
            id=1,
            nome="Alice",
            email="alice@test.com"
        )
        assert hasattr(usuario, 'id')
        assert hasattr(usuario, 'nome')
        assert hasattr(usuario, 'email')
        assert not hasattr(usuario, 'senha')

    @pytest.mark.parametrize("nome,email,senha,valido", [
        ("Alice", "alice@test.com", "senha123", True),
        ("Bob Silva", "bob@empresa.com.br", "pass123456", True),
        ("", "alice@test.com", "senha123", False),
        ("Alice", "email_invalido", "senha123", False),
        ("Alice", "alice@test.com", "123", False),
        ("   ", "alice@test.com", "senha123", False),
    ])
    def test_usuario_create_parametrizado(self, nome, email, senha, valido):
        if valido:
            usuario = UsuarioCreate(nome=nome, email=email, senha=senha)
            assert usuario.nome.strip() == nome.strip()
            assert usuario.email == email.lower()
            assert usuario.senha == senha
        else:
            with pytest.raises(ValidationError):
                UsuarioCreate(nome=nome, email=email, senha=senha)


class TestErrorSchemas:

    def test_error_response(self):
        error = ErrorResponse(detail="Erro de teste")
        assert error.detail == "Erro de teste"

    def test_message_response(self):
        message = MessageResponse(message="Sucesso")
        assert message.message == "Sucesso"

    @pytest.mark.parametrize("detail", [
        "Usuário não encontrado",
        "Email já existe",
        "Senha inválida",
        "Token expirado",
    ])
    def test_error_response_parametrizado(self, detail):
        error = ErrorResponse(detail=detail)
        assert error.detail == detail