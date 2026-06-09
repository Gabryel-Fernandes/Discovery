"""
analyzer/link_analyzer.py
Análise de URLs suspeitas (RF04).

Verifica:
- Estrutura do domínio (typosquatting, subdomínios excessivos)
- Encurtadores conhecidos
- Protocolo HTTP vs HTTPS
- Domínios de phishing conhecidos
- Heurísticas gerais de suspeita
"""

import re
from urllib.parse import urlparse
from typing import Optional

import tldextract
import validators

# Encurtadores de URL conhecidos (podem esconder destino malicioso)
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "cutt.ly", "rebrand.ly", "short.io", "rb.gy", "is.gd",
    "buff.ly", "adf.ly", "bc.vc", "ouo.io", "shrinkme.io",
}

# Domínios legítimos frequentemente imitados
LEGITIMATE_BRANDS = [
    "bradesco", "itau", "santander", "caixa", "bancodobrasil", "nubank",
    "mercadolivre", "mercadopago", "paypal", "americanas", "shopee",
    "ifood", "uber", "rappi", "correios", "receita", "serpro",
    "gov", "anatel", "anatel", "vivo", "claro", "tim", "oi",
]

# TLDs suspeitos frequentemente usados em phishing
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq",  # Freenom (gratuitos)
    "xyz", "top", "click", "link", "online", "site", "website",
    "info", "biz",
}

# Padrões regex de domínio suspeito
SUSPICIOUS_PATTERNS = [
    r"secure[-_]?login",
    r"conta[-_]?banco",
    r"atualiz",
    r"verifi",
    r"bloqueio",
    r"free[-_]?prize",
    r"premi[uo]",
    r"click[-_]?here",
    r"\d{3,}[-_.]\w+",  # muitos números no domínio
    r"(paypal|bradesco|itau|caixa|nubank)\w+\.\w+\.\w+",  # marca + sufixo extra no mesmo domínio
]


def analyze_url(url: str) -> dict:
    """
    Analisa uma URL em busca de indicadores de fraude.
    
    Returns:
        {
            "url": str,
            "is_valid": bool,
            "is_suspicious": bool,
            "risk_level": "ALTO"|"MÉDIO"|"BAIXO"|"SEGURO",
            "risk_score": 0-100,
            "indicators": [str],
            "details": dict
        }
    """
    indicators = []
    risk_score = 0

    # Validação básica
    is_valid = bool(validators.url(url)) if url.startswith("http") else bool(validators.url("https://" + url))
    if not is_valid:
        return {
            "url": url,
            "is_valid": False,
            "is_suspicious": True,
            "risk_level": "ALTO",
            "risk_score": 80,
            "indicators": ["URL com formato inválido"],
            "details": {},
        }

    # Parseia a URL
    parsed = urlparse(url if url.startswith("http") else "https://" + url)
    extracted = tldextract.extract(url)

    domain = extracted.domain.lower()
    suffix = extracted.suffix.lower()
    subdomain = extracted.subdomain.lower()
    full_domain = parsed.netloc.lower()

    details = {
        "domain": domain,
        "tld": suffix,
        "subdomain": subdomain,
        "protocol": parsed.scheme,
        "path": parsed.path,
        "full_domain": full_domain,
    }

    # --- VERIFICAÇÕES ---

    # 1. HTTP (sem HTTPS)
    if parsed.scheme == "http":
        indicators.append("Sem criptografia HTTPS (HTTP puro)")
        risk_score += 20

    # 2. Encurtador de URL
    if full_domain in URL_SHORTENERS or domain in {s.split(".")[0] for s in URL_SHORTENERS}:
        indicators.append(f"Encurtador de URL detectado ({full_domain}) - destino real oculto")
        risk_score += 35

    # 3. TLD suspeito
    if suffix in SUSPICIOUS_TLDS:
        indicators.append(f"Domínio de nível superior suspeito (.{suffix})")
        risk_score += 25

    # 4. Typosquatting - marca legítima no domínio com desvio
    for brand in LEGITIMATE_BRANDS:
        if brand in domain and domain != brand:
            indicators.append(f"Possível typosquatting de '{brand}' (domínio: {domain})")
            risk_score += 40
            break
        # Marca no subdomínio mas domínio diferente (ex: bradesco.conta-segura.com)
        if brand in subdomain and brand not in domain:
            indicators.append(f"Marca '{brand}' usada em subdomínio de domínio diferente (phishing clássico)")
            risk_score += 50
            break
    # 5. Subdomínios excessivos (mais de 3 níveis)
    subdomain_count = len(subdomain.split(".")) if subdomain else 0
    if subdomain_count >= 3:
        indicators.append(f"Estrutura de subdomínios suspeita ({subdomain_count} níveis)")
        risk_score += 20
    elif subdomain_count == 2:
        risk_score += 5

    # 6. Domínio muito longo ou com caracteres especiais
    if len(domain) > 25:
        indicators.append("Domínio muito longo (comum em phishing)")
        risk_score += 10

    if re.search(r"[0-9]{4,}", domain):
        indicators.append("Sequência numérica longa no domínio")
        risk_score += 15

    # 7. Padrões suspeitos no domínio completo
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, full_domain):
            indicators.append(f"Padrão suspeito no endereço: '{pattern}'")
            risk_score += 20
            break

    # 8. URL com muitos parâmetros (comum em phishing por redirecionamento)
    query = parsed.query
    if query and len(query) > 100:
        indicators.append("Query string muito longa (possível redirecionamento malicioso)")
        risk_score += 10

    # 9. Palavras-chave suspeitas no path
    suspicious_path_keywords = ["login", "secure", "verify", "account", "update", "confirm", "senha", "conta", "acesso"]
    for kw in suspicious_path_keywords:
        if kw in parsed.path.lower():
            indicators.append(f"Palavra suspeita na URL: '{kw}'")
            risk_score += 10
            break

    # --- NORMALIZA SCORE E DEFINE NÍVEL ---
    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = "ALTO"
    elif risk_score >= 30:
        risk_level = "MÉDIO"
    elif risk_score >= 10:
        risk_level = "BAIXO"
    else:
        risk_level = "SEGURO"

    return {
        "url": url,
        "is_valid": is_valid,
        "is_suspicious": risk_score >= 30,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "indicators": indicators if indicators else ["Nenhum indicador de fraude detectado"],
        "details": details,
    }


def extract_urls(text: str) -> list[str]:
    """Extrai todas as URLs de um texto."""
    pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
    return re.findall(pattern, text)


def analyze_text_links(text: str) -> list[dict]:
    """Analisa todos os links encontrados em um texto."""
    urls = extract_urls(text)
    return [analyze_url(url) for url in urls]