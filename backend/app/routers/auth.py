from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import hash_senha, verificar_senha, criar_token_acesso
from app.core.email import gerar_codigo_verificacao, enviar_email_verificacao
from app.models.models import Usuario

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    confirmar_senha: str

    @field_validator("confirmar_senha")
    @classmethod
    def senhas_iguais(cls, v, info):
        if "senha" in info.data and v != info.data["senha"]:
            raise ValueError("As senhas não conferem")
        return v

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v):
        if len(v) < 8:
            raise ValueError("A senha precisa ter no mínimo 8 caracteres")
        return v


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    codigo: str


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class ReenviarCodigoRequest(BaseModel):
    email: EmailStr


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == req.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    codigo = gerar_codigo_verificacao()

    novo_usuario = Usuario(
        nome=req.nome,
        email=req.email,
        senha_hash=hash_senha(req.senha),
        email_verificado=False,
        codigo_verificacao=codigo,
        codigo_expira_em=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    try:
        enviar_email_verificacao(req.email, codigo)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Usuário criado, mas falha ao enviar email: {str(e)}",
        )

    return {"message": "Cadastro realizado. Verifique seu email para o código de confirmação."}


@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == req.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.email_verificado:
        return {"message": "Email já verificado"}

    if usuario.codigo_verificacao != req.codigo:
        raise HTTPException(status_code=400, detail="Código inválido")

    if usuario.codigo_expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado. Solicite um novo.")

    usuario.email_verificado = True
    usuario.codigo_verificacao = None
    usuario.codigo_expira_em = None
    db.commit()

    return {"message": "Email verificado com sucesso"}


@router.post("/resend-code")
def resend_code(req: ReenviarCodigoRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == req.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.email_verificado:
        return {"message": "Email já verificado"}

    codigo = gerar_codigo_verificacao()
    usuario.codigo_verificacao = codigo
    usuario.codigo_expira_em = datetime.utcnow() + timedelta(minutes=15)
    db.commit()

    enviar_email_verificacao(req.email, codigo)

    return {"message": "Novo código enviado"}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == req.email).first()
    if not usuario or not verificar_senha(req.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    if not usuario.email_verificado:
        raise HTTPException(status_code=403, detail="Email ainda não verificado")

    token = criar_token_acesso({"sub": str(usuario.id), "email": usuario.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {"id": usuario.id, "nome": usuario.nome, "email": usuario.email},
    }