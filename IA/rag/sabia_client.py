"""
rag/sabia_client.py
Cliente para a API Maritaca AI (modelo Sabiá-3).

A Maritaca oferece acesso gratuito via:
- Site: https://plataforma.maritaca.ai
- API compatível com OpenAI SDK
- Free tier: suficiente para desenvolvimento e prototipagem

Documentação: https://docs.maritaca.ai
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MARITACA_API_KEY = os.getenv("MARITACA_API_KEY", "")
MARITACA_MODEL = os.getenv("MARITACA_MODEL", "sabia-3")
MARITACA_BASE_URL = "https://chat.maritaca.ai/api"

# System prompt especializado em detecção de golpes
SYSTEM_PROMPT = """Você é o dIscovery, um sistema especializado em detecção de golpes e fraudes digitais no Brasil, desenvolvido para apoiar a Anatel na educação digital e prevenção a crimes cibernéticos.

Suas responsabilidades:
- Analisar textos, mensagens e URLs em busca de padrões de fraude
- Classificar o tipo de golpe com base na taxonomia estabelecida
- Avaliar o nível de risco (ALTO, MÉDIO, BAIXO, SEGURO)
- Fornecer explicações claras e didáticas sobre as ameaças encontradas
- Sugerir ações preventivas

Você tem acesso à base de conhecimento da Anatel sobre golpes digitais brasileiros e deve utilizá-la como referência primária.

Responda sempre em português brasileiro, de forma objetiva e clara.
"""


def get_sabia_client() -> OpenAI:
    """Retorna cliente configurado para a API Maritaca."""
    if not MARITACA_API_KEY:
        raise ValueError(
            "MARITACA_API_KEY não configurada. "
            "Crie sua conta gratuita em https://plataforma.maritaca.ai e adicione a chave no .env"
        )
    return OpenAI(
        api_key=MARITACA_API_KEY,
        base_url=MARITACA_BASE_URL,
    )


def analyze_with_rag(text: str, context: str, analysis_type: str = "completa") -> dict:
    """
    Envia texto + contexto RAG para o Sabiá e retorna análise estruturada.
    
    Args:
        text: Texto/URL a ser analisado
        context: Contexto recuperado pelo RAG
        analysis_type: "completa" | "rapida" | "link"
    
    Returns:
        dict com: classification, risk_level, explanation, indicators, recommendations
    """
    client = get_sabia_client()

    if analysis_type == "rapida":
        user_prompt = f"""Analise rapidamente este conteúdo e responda em JSON:

CONTEÚDO: {text[:1000]}

Responda APENAS com JSON válido neste formato:
{{
  "is_suspicious": true/false,
  "risk_level": "ALTO|MÉDIO|BAIXO|SEGURO",
  "fraud_type": "nome do tipo de golpe ou null",
  "confidence": 0.0-1.0,
  "brief_reason": "explicação em 1 frase"
}}"""

    elif analysis_type == "link":
        user_prompt = f"""Analise esta URL em busca de indicadores de fraude:

URL: {text}

BASE DE CONHECIMENTO RELEVANTE:
{context}

Responda APENAS com JSON válido:
{{
  "is_suspicious": true/false,
  "risk_level": "ALTO|MÉDIO|BAIXO|SEGURO",
  "indicators": ["lista de indicadores encontrados"],
  "fraud_type": "tipo de golpe ou null",
  "confidence": 0.0-1.0,
  "explanation": "explicação detalhada"
}}"""

    else:  # completa
        user_prompt = f"""Analise o seguinte conteúdo em busca de golpes e fraudes digitais:

CONTEÚDO A ANALISAR:
{text[:2000]}

CONTEXTO DA BASE DE CONHECIMENTO (taxonomia de golpes):
{context}

Com base no conteúdo e na base de conhecimento, responda APENAS com JSON válido:
{{
  "is_suspicious": true/false,
  "risk_level": "ALTO|MÉDIO|BAIXO|SEGURO",
  "fraud_type": "tipo específico de golpe conforme taxonomia ou null",
  "fraud_code": "GOLPE_01 a GOLPE_10 ou null",
  "confidence": 0.0-1.0,
  "indicators": ["indicador 1", "indicador 2"],
  "explanation": "explicação detalhada para o usuário",
  "recommendations": ["ação recomendada 1", "ação recomendada 2"],
  "keywords_found": ["palavra-chave suspeita 1", "palavra-chave suspeita 2"]
}}"""

    try:
        response = client.chat.completions.create(
            model=MARITACA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.1,  # baixa temperatura = mais determinístico para classificação
        )

        raw_text = response.choices[0].message.content.strip()

        # Limpa markdown se vier com ```json
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        
        import json
        result = json.loads(raw_text)
        result["model_used"] = MARITACA_MODEL
        result["raw_response"] = raw_text
        return result

    except Exception as e:
        return {
            "is_suspicious": None,
            "risk_level": "ERRO",
            "fraud_type": None,
            "confidence": 0.0,
            "explanation": f"Erro ao consultar Sabiá: {str(e)}",
            "error": str(e),
        }
