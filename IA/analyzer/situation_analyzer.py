"""
analyzer/situation_analyzer.py
Analisa situações descritas em linguagem natural pelo usuário (RF03 estendido).

Diferente de analisar uma mensagem pronta, aqui o usuário descreve o que aconteceu
com suas próprias palavras. Ex: "Fui a um site e ele pediu que eu lesse um QR code
pela câmera do celular, mas o site era de compras normais."

O módulo:
1. Classifica a situação com o ML
2. Busca contexto RAG relevante
3. Envia ao Sabiá com prompt especializado para análise de situação
4. Retorna: é golpe?, por que é suspeito?, o que fazer agora?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from classifier.ml_classifier import predict as ml_predict
from rag.rag_engine import get_rag
from rag.sabia_client import get_sabia_client, MARITACA_MODEL, SYSTEM_PROMPT
from config import settings

import json


SITUATION_PROMPT_TEMPLATE = """Um usuário descreveu a seguinte situação que vivenciou:

SITUAÇÃO RELATADA:
{situation}

CONTEXTO DA BASE DE CONHECIMENTO (tipos de golpes conhecidos):
{context}

CLASSIFICAÇÃO INICIAL DO SISTEMA:
- Tipo suspeito detectado: {ml_label}
- Confiança: {ml_confidence:.0%}

Analise esta situação e responda APENAS com JSON válido no formato abaixo.
Considere que o usuário pode não saber que foi vítima de golpe — explique de forma didática.

{{
  "is_suspicious": true/false,
  "risk_level": "ALTO|MÉDIO|BAIXO|SEGURO",
  "fraud_type": "nome do tipo de golpe ou null",
  "fraud_code": "GOLPE_XX ou null",
  "confidence": 0.0-1.0,
  "is_scam": true/false,
  "why_suspicious": "explicação clara de POR QUE essa situação é suspeita, em linguagem simples para leigos",
  "red_flags": ["sinal de alerta 1", "sinal de alerta 2"],
  "what_to_do_now": ["ação imediata 1", "ação imediata 2", "ação imediata 3"],
  "how_to_protect": ["dica de proteção 1", "dica de proteção 2"],
  "verdict": "Uma frase resumindo o veredicto para o usuário"
}}"""


def analyze_situation(situation: str, use_sabia: bool = True) -> dict:
    """
    Analisa uma situação descrita pelo usuário em linguagem natural.

    Args:
        situation: Texto descrevendo o que aconteceu
        use_sabia: Se True, usa o Sabiá para análise profunda

    Returns:
        Dicionário com veredicto, explicação e recomendações
    """
    # 1. ML local
    ml_result = ml_predict(situation)

    # 2. RAG
    rag = get_rag()
    top_k = settings.get("rag", "top_k_chunks") or 3
    context = rag.build_context(f"{situation} {ml_result['label']}")

    # 3. Sabiá
    sabia_result = None
    if use_sabia:
        try:
            client = get_sabia_client()
            prompt = SITUATION_PROMPT_TEMPLATE.format(
                situation=situation[:2000],
                context=context,
                ml_label=ml_result["label"],
                ml_confidence=ml_result["confidence"],
            )
            response = client.chat.completions.create(
                model=MARITACA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            sabia_result = json.loads(raw.strip())
        except Exception as e:
            sabia_result = {"error": str(e)}

    # 4. Monta resposta final
    if sabia_result and not sabia_result.get("error"):
        return {
            "input_situation": situation,
            "is_suspicious": sabia_result.get("is_suspicious", ml_result["is_suspicious"]),
            "is_scam": sabia_result.get("is_scam", ml_result["is_suspicious"]),
            "risk_level": sabia_result.get("risk_level", "BAIXO"),
            "fraud_type": sabia_result.get("fraud_type"),
            "fraud_code": sabia_result.get("fraud_code"),
            "confidence": sabia_result.get("confidence", ml_result["confidence"]),
            "verdict": sabia_result.get("verdict", ""),
            "why_suspicious": sabia_result.get("why_suspicious", ""),
            "red_flags": sabia_result.get("red_flags", []),
            "what_to_do_now": sabia_result.get("what_to_do_now", []),
            "how_to_protect": sabia_result.get("how_to_protect", []),
            "ml_classification": ml_result,
            "analysis_mode": "sabia+rag",
        }

    # Fallback sem Sabiá — usa só o ML
    cfg = settings.get("risk_thresholds")
    suspicious_prob = sum(v for k, v in ml_result["probabilities"].items() if k != "legitimo")
    if suspicious_prob >= cfg["alto"]["suspicious_prob_min"]:
        risk = "ALTO"
    elif suspicious_prob >= cfg["medio"]["suspicious_prob_min"]:
        risk = "MÉDIO"
    elif ml_result["is_suspicious"]:
        risk = "BAIXO"
    else:
        risk = "SEGURO"

    fraud_code = settings.fraud_label_to_code(ml_result["label"])

    return {
        "input_situation": situation,
        "is_suspicious": ml_result["is_suspicious"],
        "is_scam": ml_result["is_suspicious"],
        "risk_level": risk,
        "fraud_type": ml_result["label"] if ml_result["is_suspicious"] else None,
        "fraud_code": fraud_code,
        "confidence": ml_result["confidence"],
        "verdict": f"Situação classificada como '{ml_result['label']}' pelo modelo local." if ml_result["is_suspicious"] else "Situação não apresenta padrões de golpe conhecidos.",
        "why_suspicious": "Análise baseada em padrões textuais (modelo ML local, sem Sabiá).",
        "red_flags": [],
        "what_to_do_now": ["Ative o Sabiá para análise mais detalhada."],
        "how_to_protect": [],
        "ml_classification": ml_result,
        "analysis_mode": "ml_only",
        "sabia_error": sabia_result.get("error") if sabia_result else "Sabiá desabilitado",
    }
