from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    nome: str
    funcao: str

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


class CasoBase(BaseModel):
    fonte: str
    titulo: str
    url: str
    legenda: str
    situacao: str

class CasoCreate(CasoBase):
    pass

class CasoResponse(CasoBase):
    id: int
    data_publicacao: datetime

    class Config:
        from_attributes = True

class AnaliseBase(BaseModel):
    caso_id: int
    usuario_id: Optional[int] = None
    veracidade: float
    erros_ortograficos: int
    uso_ia_generativa: int
    links_suspeitos: int
    taxonomia_repetitiva: int
    tipo: str

class AnaliseCreate(AnaliseBase):
    pass

class AnaliseResponse(AnaliseBase):
    id: int

    class Config:
        from_attributes = True


class ExportacaoBase(BaseModel):
    caso_id: int
    usuario_id: int

class ExportacaoCreate(ExportacaoBase):
    pass

class ExportacaoResponse(ExportacaoBase):
    id: int
    data_exportacao: datetime

    class Config:
        from_attributes = True