from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Caso
from app.schemas.schemas import CasoCreate, CasoResponse
from typing import List, Optional

router = APIRouter(prefix="/casos", tags=["casos"])

@router.get("/", response_model=List[CasoResponse])
def listar_casos(
    titulo: Optional[str] = None,
    fonte: Optional[str] = None,
    tipo_golpe: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from datetime import datetime
    query = db.query(Caso)

    if titulo:
        query = query.filter(Caso.titulo.ilike(f"%{titulo}%"))
    if fonte:
        query = query.filter(Caso.fonte == fonte)
    if tipo_golpe:
        query = query.filter(Caso.titulo == tipo_golpe)
    if data_inicio:
        try:
            data = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Caso.data_publicacao >= data)
        except:
            pass
    if data_fim:
        try:
            data = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(Caso.data_publicacao <= data)
        except:
            pass

    return query.order_by(Caso.data_publicacao.desc()).all()

@router.get("/recentes", response_model=List[CasoResponse])
def casos_recentes(data_inicio: Optional[str] = None, db: Session = Depends(get_db)):
    from datetime import datetime
    query = db.query(Caso)
    if data_inicio:
        try:
            data = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Caso.data_publicacao >= data)
        except:
            pass
    return query.order_by(Caso.data_publicacao.desc()).limit(3).all() 

@router.get("/estatisticas")
def estatisticas_casos(
    fonte: Optional[str] = None,
    tipo_golpe: Optional[str] = None,
    data_inicio: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    from datetime import datetime

    query = db.query(Caso.situacao, func.count(Caso.id).label("total"))

    if fonte:
        query = query.filter(Caso.fonte == fonte)
    if tipo_golpe:
        query = query.filter(Caso.titulo == tipo_golpe)
    if data_inicio:
        try:
            data = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Caso.data_publicacao >= data)
        except:
            pass

    resultado = query.group_by(Caso.situacao).all()
    dados = {"ALTO": 0, "MÉDIO": 0, "INDEFINIDO": 0}
    for r in resultado:
        if r.situacao in dados:
            dados[r.situacao] = r.total
    return [
        {"situacao": "Alta chance de golpe", "total": dados["ALTO"], "cor": "#f44336"},
        {"situacao": "Baixa chance de golpe", "total": dados["MÉDIO"], "cor": "#4CAF50"},
        {"situacao": "Inconclusivo", "total": dados["INDEFINIDO"], "cor": "#41b8b5"},
    ]

@router.get("/tipos-golpe")
def tipos_golpe(db: Session = Depends(get_db)):
    from sqlalchemy import distinct
    tipos = db.query(distinct(Caso.titulo)).filter(Caso.titulo != None).all()
    return [t[0] for t in tipos]

@router.get("/{caso_id}", response_model=CasoResponse)
def buscar_caso(caso_id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    return caso

@router.post("/", response_model=CasoResponse)
def criar_caso(caso: CasoCreate, db: Session = Depends(get_db)):
    novo_caso = Caso(**caso.model_dump())
    db.add(novo_caso)
    db.commit()
    db.refresh(novo_caso)
    return novo_caso