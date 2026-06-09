from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Analise
from app.schemas.schemas import AnaliseCreate, AnaliseResponse
from typing import List

router = APIRouter(prefix="/analises", tags=["analises"])

@router.get("/", response_model=List[AnaliseResponse])
def listar_analises(db: Session = Depends(get_db)):
    return db.query(Analise).all()

@router.get("/caso/{caso_id}", response_model=List[AnaliseResponse])
def buscar_analise_por_caso(caso_id: int, db: Session = Depends(get_db)):
    analises = db.query(Analise).filter(Analise.caso_id == caso_id).all()
    return analises

@router.get("/{analise_id}", response_model=AnaliseResponse)
def buscar_analise(analise_id: int, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Analise não encontrada")
    return analise

@router.post("/", response_model=AnaliseResponse)
def criar_analise(analise: AnaliseCreate, db: Session = Depends(get_db)):
    nova_analise = Analise(**analise.model_dump())
    db.add(nova_analise)
    db.commit()
    db.refresh(nova_analise)
    return nova_analise