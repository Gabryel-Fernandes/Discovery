"""
api/main.py  v2 — dIscovery AI
"""
import os, sys
from datetime import datetime
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analyzer.detection_service import analyze_content, analyze_single_url, batch_analyze
from analyzer.situation_analyzer import analyze_situation
from classifier.ml_classifier import train as train_classifier
from rag.rag_engine import get_rag
from config import settings

app = FastAPI(title="dIscovery AI API", version="2.0.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

_session_stats = defaultdict(int)
_recent_detections = []

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    use_sabia: Optional[bool] = None
    mode: str = "completa"
    source: Optional[str] = None

class URLRequest(BaseModel):
    url: str
    use_sabia: Optional[bool] = None

class BatchRequest(BaseModel):
    texts: list[str]
    use_sabia: bool = False

class SituationRequest(BaseModel):
    situation: str = Field(..., min_length=10, max_length=5000,
        description="Descreva em linguagem natural o que aconteceu. Ex: 'Um site de compras pediu que eu lesse um QR code pela câmera'")
    use_sabia: Optional[bool] = None

class TrainRequest(BaseModel):
    model_type: str = "logreg"

def resolve_sabia(requested):
    if requested is not None:
        return requested
    return settings.get("modules", "use_sabia_by_default") or False

def register(result, source):
    _session_stats["total_analyzed"] += 1
    if result.get("is_suspicious"):
        _session_stats["total_suspicious"] += 1
        lvl = result.get("risk_level", "")
        if lvl: _session_stats[f"risk_{lvl.lower()}"] += 1
        ft = result.get("fraud_type")
        if ft: _session_stats[f"type_{ft}"] += 1
    _recent_detections.append({
        "timestamp": datetime.utcnow().isoformat(), "source": source,
        "risk_level": result.get("risk_level"), "fraud_type": result.get("fraud_type"),
        "is_suspicious": result.get("is_suspicious"),
    })
    if len(_recent_detections) > 200: _recent_detections.pop(0)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "dIscovery AI", "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "modules": ["ml_classifier","link_analyzer","rag","sabia","situation_analyzer"]}

@app.post("/api/analyze")
def analyze_text(req: AnalyzeRequest):
    """Análise completa de texto ou mensagem."""
    try:
        result = analyze_content(text=req.text, use_sabia=resolve_sabia(req.use_sabia), analysis_mode=req.mode)
        register(result, req.source)
        return {"success": True, "data": result, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/situation")
def analyze_situation_endpoint(req: SituationRequest):
    """
    Analisa uma SITUAÇÃO descrita pelo usuário em linguagem natural.
    O usuário não precisa ter a mensagem original — basta descrever o que aconteceu.
    Exemplos:
      - 'Fui a um site e ele pediu que eu lesse um QR code pela câmera'
      - 'Recebi ligação do banco dizendo que meu PIX foi comprometido'
      - 'Um desconhecido no WhatsApp disse ser meu filho e pediu PIX urgente'
    """
    try:
        result = analyze_situation(situation=req.situation, use_sabia=resolve_sabia(req.use_sabia))
        register(result, "situation_report")
        return {"success": True, "data": result, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/url")
def analyze_url_ep(req: URLRequest):
    """Análise de URL específica."""
    try:
        result = analyze_single_url(req.url, use_sabia=resolve_sabia(req.use_sabia))
        _session_stats["urls_analyzed"] += 1
        if result.get("is_suspicious"): _session_stats["suspicious_urls"] += 1
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/batch")
def analyze_batch(req: BatchRequest):
    """Análise em lote (ML local por padrão, sem custo de API)."""
    try:
        results = batch_analyze(req.texts, use_sabia=req.use_sabia)
        suspicious = sum(1 for r in results if r["is_suspicious"])
        _session_stats["total_analyzed"] += len(req.texts)
        _session_stats["total_suspicious"] += suspicious
        return {"success": True, "total": len(results), "suspicious_count": suspicious, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
def get_config():
    """Retorna configurações atuais do sistema."""
    import json
    from config.settings import CONFIG_PATH
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return {"success": True, "config": json.load(f)}

@app.post("/api/config/reload")
def reload_config():
    """Recarrega config.json sem reiniciar a API."""
    try:
        cfg = settings.reload()
        return {"success": True, "message": "Configurações recarregadas.", "config": cfg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/taxonomy")
def get_taxonomy():
    """Lista todos os tipos de golpe cadastrados."""
    return {"fraud_types": settings.all_fraud_types(), "total": len(settings.all_fraud_types())}

@app.get("/api/stats")
def get_stats():
    total = _session_stats.get("total_analyzed", 0)
    suspicious = _session_stats.get("total_suspicious", 0)
    return {
        "session_stats": dict(_session_stats),
        "summary": {"total_analyzed": total, "total_suspicious": suspicious,
                    "detection_rate": round(suspicious / total, 4) if total > 0 else 0},
        "recent_detections": _recent_detections[-20:],
    }

@app.get("/api/evaluation")
def get_evaluation(model: str = "logreg"):
    """Gera relatório de avaliação com precision, recall e F1 por classe."""
    try:
        from scripts.evaluation_report import run_evaluation
        report = run_evaluation(model)
        return {"success": True, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/rebuild")
def rebuild_rag():
    try:
        get_rag().rebuild()
        return {"success": True, "message": "Índice RAG reconstruído."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/classifier/retrain")
def retrain(req: TrainRequest):
    try:
        metrics = train_classifier(req.model_type)
        return {"success": True, "message": "Modelo retreinado.", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("API_HOST","0.0.0.0"), port=int(os.getenv("API_PORT",8000)), reload=True)