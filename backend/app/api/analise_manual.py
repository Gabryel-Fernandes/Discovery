from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.services.ia_service import analisar_texto, analisar_url
from app.core.database import get_db
from app.models.models import Caso, Analise
from datetime import datetime

router = APIRouter(prefix="/analise-manual", tags=["analise-manual"])

class TextoRequest(BaseModel):
    text: str
    use_sabia: bool = True
    fonte: Optional[str] = "manual"

class URLRequest(BaseModel):
    url: str
    use_sabia: bool = True
    fonte: Optional[str] = "manual"

@router.post("/texto")
async def analisar_texto_endpoint(req: TextoRequest, db: Session = Depends(get_db)):
    try:
        resultado = await analisar_texto(
            text=req.text,
            use_sabia=req.use_sabia,
        )

        data = resultado.get("data", {})
        ml = data.get("ml_classification", {})

        confidence = data.get("confidence", 0)
        is_suspicious = data.get("is_suspicious", False)
        veracidade = confidence if is_suspicious else (1 - confidence)

        novo_caso = Caso(
            data_publicacao=datetime.utcnow(),
            fonte=req.fonte or "manual",
            titulo=data.get("fraud_type") or "Análise Manual",
            url="",
            legenda=req.text,
            situacao=data.get("risk_level", "INDEFINIDO"),
        )
        db.add(novo_caso)
        db.commit()
        db.refresh(novo_caso)

        nova_analise = Analise(
            caso_id=novo_caso.id,
            usuario_id=None,
            veracidade=veracidade,
            erros_ortograficos=round(ml.get("probabilities", {}).get("phishing", 0) * 100),
            uso_ia_generativa=round(ml.get("probabilities", {}).get("falso_investimento", 0) * 100),
            links_suspeitos=len(data.get("suspicious_links", [])),
            taxonomia_repetitiva=round(ml.get("confidence", 0) * 100),
            tipo="manual",
        )
        db.add(nova_analise)
        db.commit()

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar texto: {str(e)}")


@router.post("/url")
async def analisar_url_endpoint(req: URLRequest, db: Session = Depends(get_db)):
    try:
        resultado = await analisar_url(
            url=req.url,
            use_sabia=req.use_sabia,
        )

        data = resultado.get("data", {})
        veracidade = data.get("risk_score", 0) / 100

        novo_caso = Caso(
            data_publicacao=datetime.utcnow(),
            fonte=req.fonte or "manual",
            titulo="Análise de URL",
            url=req.url,
            legenda="",
            situacao=data.get("risk_level", "INDEFINIDO"),
        )
        db.add(novo_caso)
        db.commit()
        db.refresh(novo_caso)

        nova_analise = Analise(
            caso_id=novo_caso.id,
            usuario_id=None,
            veracidade=veracidade,
            erros_ortograficos=0,
            uso_ia_generativa=0,
            links_suspeitos=1 if data.get("is_suspicious") else 0,
            taxonomia_repetitiva=0,
            tipo="manual_url",
        )
        db.add(nova_analise)
        db.commit()

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar URL: {str(e)}")