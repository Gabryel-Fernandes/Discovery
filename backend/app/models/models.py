from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    funcao = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    email_verificado = Column(Boolean, default=False)
    codigo_verificacao = Column(String, nullable=True)
    codigo_expira_em = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    analises = relationship("Analise", back_populates="usuario")
    exportacoes = relationship("Exportacao", back_populates="usuario")


class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    data_publicacao = Column(DateTime, default=datetime.utcnow)
    fonte = Column(String)
    titulo = Column(String)
    url = Column(String)
    legenda = Column(Text)
    situacao = Column(String)

    analises = relationship("Analise", back_populates="caso")
    exportacoes = relationship("Exportacao", back_populates="caso")


class Analise(Base):
    __tablename__ = "analises"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    veracidade = Column(Numeric)
    erros_ortograficos = Column(Integer)
    uso_ia_generativa = Column(Integer)
    links_suspeitos = Column(Integer)
    taxonomia_repetitiva = Column(Integer)
    tipo = Column(String)

    caso = relationship("Caso", back_populates="analises")
    usuario = relationship("Usuario", back_populates="analises")


class Exportacao(Base):
    __tablename__ = "exportacoes"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_exportacao = Column(DateTime, default=datetime.utcnow)

    caso = relationship("Caso", back_populates="exportacoes")
    usuario = relationship("Usuario", back_populates="exportacoes")