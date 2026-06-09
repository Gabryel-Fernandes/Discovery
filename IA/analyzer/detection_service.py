"""
analyzer/detection_service.py
Serviço central de detecção - orquestra todos os módulos de IA.

Pipeline de análise:
1. Classificador ML leve (rápido, sem API)  
2. Análise de links (sem API)
3. RAG: recupera contexto relevante da taxonomia
4. Sabiá (Maritaca): análise profunda com contexto RAG
5. Fusão dos resultados em resposta unificada
"""

import time
from typing import Optional

from classifier.ml_classifier import predict as ml_predict
from analyzer.link_analyzer import analyze_text_links, analyze_url
from rag.rag_engine import get_rag
from rag.sabia_client import analyze_with_rag


RISK_ORDER = {"ALTO": 4, "MÉDIO": 3, "BAIXO": 2, "SEGURO": 1, "ERRO": 0}


def analyze_content(
    text: str,
    use_sabia: bool = True,
    analysis_mode: str = "completa",
) -> dict:
    """
    Pipeline completo de análise de conteúdo suspeito.

    Args:
        text: Texto ou mensagem a analisar
        use_sabia: Se True, consulta a API Maritaca (Sabiá). False = apenas ML local
        analysis_mode: "completa" | "rapida"

    Returns:
        Dicionário com resultado consolidado da análise
    """
    start_time = time.time()

    # ── 1. Classificador ML local (sempre roda, sem API) ──────────────────
    ml_result = ml_predict(text)

    # ── 2. Análise de links no texto ──────────────────────────────────────
    link_results = analyze_text_links(text)
    suspicious_links = [l for l in link_results if l["is_suspicious"]]

    # ── 3. Determina risco preliminar (ML + links) ────────────────────────
    # Soma probabilidades de todas as classes suspeitas (tudo exceto "legitimo")
    suspicious_classes = [c for c in ml_result["probabilities"] if c != "legitimo"]
    suspicious_prob = sum(ml_result["probabilities"].get(c, 0) for c in suspicious_classes)
    legit_prob = ml_result["probabilities"].get("legitimo", 0)

    preliminary_risk = "SEGURO"
    if ml_result["is_suspicious"]:
        if suspicious_prob >= 0.80 or ml_result["confidence"] >= 0.60:
            preliminary_risk = "ALTO"
        elif suspicious_prob >= 0.60 or ml_result["confidence"] >= 0.30:
            preliminary_risk = "MÉDIO"
        else:
            preliminary_risk = "BAIXO"
    # Se prob de legítimo for muito baixa, marca como suspeito mesmo assim
    if preliminary_risk == "SEGURO" and legit_prob < 0.15:
        preliminary_risk = "BAIXO"

    if suspicious_links:
        max_link_risk = max(l["risk_level"] for l in suspicious_links)
        if RISK_ORDER.get(max_link_risk, 0) > RISK_ORDER.get(preliminary_risk, 0):
            preliminary_risk = max_link_risk

    # ── 4. RAG + Sabiá (se habilitado e conteúdo suspeito) ───────────────
    sabia_result = None
    rag_context = ""

    if use_sabia and (ml_result["is_suspicious"] or suspicious_links or analysis_mode == "completa"):
        try:
            rag = get_rag()
            # Enriquece a query com o tipo suspeito detectado pelo ML
            query = f"{text} {ml_result.get('label', '')}"
            rag_context = rag.build_context(query)
            sabia_result = analyze_with_rag(text, rag_context, analysis_type=analysis_mode)
        except Exception as e:
            sabia_result = {"error": str(e), "risk_level": "ERRO"}

    # ── 5. Consolida resultados ───────────────────────────────────────────
    final_risk = preliminary_risk
    if sabia_result and sabia_result.get("risk_level") not in ("ERRO", None):
        sabia_risk = sabia_result["risk_level"]
        if RISK_ORDER.get(sabia_risk, 0) > RISK_ORDER.get(final_risk, 0):
            final_risk = sabia_risk

    is_suspicious = final_risk in ("ALTO", "MÉDIO")

    # Determina tipo de fraude final (Sabiá tem precedência)
    fraud_type = None
    fraud_code = None
    if sabia_result:
        fraud_type = sabia_result.get("fraud_type")
        fraud_code = sabia_result.get("fraud_code")
    if not fraud_type and ml_result["is_suspicious"]:
        fraud_type = ml_result["label"]

    elapsed_ms = int((time.time() - start_time) * 1000)

    return {
        # Resultado principal
        "is_suspicious": is_suspicious,
        "risk_level": final_risk,
        "fraud_type": fraud_type,
        "fraud_code": fraud_code,
        "confidence": sabia_result.get("confidence", ml_result["confidence"]) if sabia_result else ml_result["confidence"],

        # Explicação e recomendações (do Sabiá se disponível)
        "explanation": sabia_result.get("explanation", f"Classificado como '{ml_result['label']}' pelo modelo local.") if sabia_result else f"Classificado como '{ml_result['label']}' pelo modelo local.",
        "recommendations": sabia_result.get("recommendations", []) if sabia_result else [],
        "indicators": (sabia_result.get("indicators", []) if sabia_result else []) + 
                       [i for link in suspicious_links for i in link["indicators"]],
        "keywords_found": sabia_result.get("keywords_found", []) if sabia_result else [],

        # Sub-resultados por módulo (transparência)
        "ml_classification": ml_result,
        "link_analysis": link_results,
        "suspicious_links": suspicious_links,
        "sabia_analysis": sabia_result,

        # Metadados
        "analysis_time_ms": elapsed_ms,
        "modules_used": [
            "ml_classifier",
            "link_analyzer",
            *(["rag", "sabia"] if sabia_result else []),
        ],
        "rag_context_used": bool(rag_context),
    }


def analyze_single_url(url: str, use_sabia: bool = True) -> dict:
    """Análise focada em uma única URL."""
    link_result = analyze_url(url)

    if use_sabia and link_result["is_suspicious"]:
        try:
            rag = get_rag()
            context = rag.build_context(f"URL suspeita link malicioso {url}")
            sabia_result = analyze_with_rag(url, context, analysis_type="link")
            link_result["sabia_analysis"] = sabia_result
            link_result["explanation"] = sabia_result.get("explanation", "")
        except Exception as e:
            link_result["sabia_error"] = str(e)

    return link_result


def batch_analyze(texts: list[str], use_sabia: bool = False) -> list[dict]:
    """
    Analisa múltiplos textos em lote.
    use_sabia=False por padrão no lote para economizar chamadas API.
    """
    return [analyze_content(t, use_sabia=use_sabia, analysis_mode="rapida") for t in texts]