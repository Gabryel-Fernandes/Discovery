"""
config/settings.py
Carrega e expõe as configurações centrais do dIscovery AI.
Todos os módulos importam daqui em vez de ter valores hardcoded.

Para alterar qualquer parâmetro, edite data/config.json — sem tocar no código.
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"


def load() -> dict:
    """Carrega o config.json e retorna como dicionário."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {CONFIG_PATH}")
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# Instância global carregada uma vez
_cfg = load()


def get(section: str, key: str = None):
    """
    Retorna uma seção ou valor específico do config.
    Exemplos:
        get("modules")                     → dict com todos os módulos
        get("risk_thresholds", "alto")     → dict do limiar alto
        get("rag", "top_k_chunks")         → 3
    """
    section_data = _cfg.get(section, {})
    if key is None:
        return section_data
    return section_data.get(key)


def fraud_label_to_code(label: str) -> str | None:
    """Converte label do ML (ex: 'phishing') para código da taxonomia (ex: 'GOLPE_01')."""
    for ft in _cfg.get("fraud_types", []):
        if ft["label"] == label:
            return ft["code"]
    return None


def fraud_code_to_name(code: str) -> str | None:
    """Converte código (ex: 'GOLPE_01') para nome legível (ex: 'Phishing')."""
    for ft in _cfg.get("fraud_types", []):
        if ft["code"] == code:
            return ft["name"]
    return None


def all_fraud_types() -> list[dict]:
    return _cfg.get("fraud_types", [])


def reload():
    """Recarrega o config do disco (útil após editar o JSON sem reiniciar)."""
    global _cfg
    _cfg = load()
    return _cfg
