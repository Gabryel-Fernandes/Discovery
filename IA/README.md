# dIscovery AI — Módulo de Inteligência Artificial (v2)

> Detecção de golpes e fraudes digitais com RAG + Sabiá (Maritaca AI) + ML Clássico  
> Desenvolvido para apoiar a Anatel em educação digital e prevenção a crimes cibernéticos.

---

## Arquitetura geral

```
discovery_ai/
├── api/
│   └── main.py                    → API REST completa (FastAPI) — v2
├── rag/
│   ├── rag_engine.py              → Motor RAG: embeddings + FAISS
│   └── sabia_client.py            → Integração Maritaca AI (Sabiá-3)
├── classifier/
│   └── ml_classifier.py           → Classificador ML: TF-IDF + Regressão Logística
├── analyzer/
│   ├── link_analyzer.py           → Análise heurística de URLs
│   ├── detection_service.py       → Orquestrador do pipeline completo
│   └── situation_analyzer.py      → Análise de situações em linguagem natural
├── config/
│   └── settings.py                → Carregador de configurações centrais
├── data/
│   ├── config.json                → Parametrização central do sistema
│   ├── knowledge_base/
│   │   └── taxonomia_golpes.md    → Base de conhecimento RAG (11 tipos de golpe)
│   ├── vector_store/              → Índice FAISS (gerado automaticamente)
│   ├── classifier_model.joblib    → Modelo ML treinado (gerado automaticamente)
│   ├── evaluation_report.json     → Relatório de avaliação (gerado pelo script)
│   └── evaluation_report.txt      → Relatório legível (gerado pelo script)
└── scripts/
    ├── setup_and_test.py          → Setup inicial e smoke tests
    └── evaluation_report.py       → Relatório de acurácia: precision, recall, F1
```

---

## Pipeline de análise

Cada texto ou situação passa por 4 camadas em sequência:

```
Entrada (texto / URL / situação)
         │
         ▼
┌─────────────────────┐
│   ML Classifier     │  TF-IDF + Logistic Regression
│   (~5ms, local)     │  12 classes de golpe + legítimo
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Link Analyzer     │  Heurísticas: typosquatting, encurtadores,
│   (~2ms, local)     │  TLD suspeito, HTTPS, subdomínios
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   RAG Engine        │  sentence-transformers → FAISS
│   (~50ms, local)    │  Recupera trechos relevantes da taxonomia
└────────┬────────────┘
         │ contexto enriquecido
         ▼
┌─────────────────────┐
│   Sabiá-3 API       │  LLM em português (Maritaca AI)
│   (~1-2s, API)      │  Análise profunda + explicação + recomendações
└────────┬────────────┘
         │
         ▼
   Resultado unificado
   (risco + tipo + explicação + recomendações)
```

---

## Tipos de golpe detectados (12 classes)

| Código    | Label                  | Nome                          |
|-----------|------------------------|-------------------------------|
| GOLPE_01  | phishing               | Phishing                      |
| GOLPE_02  | golpe_pix              | Golpe do PIX                  |
| GOLPE_03  | falso_emprestimo       | Falso Empréstimo / FGTS       |
| GOLPE_04  | falsa_promocao         | Falsa Promoção / Sorteio      |
| GOLPE_05  | falso_servico          | Falso Serviço                 |
| GOLPE_06  | engenharia_social      | Engenharia Social             |
| GOLPE_07  | clonagem_conta         | Clonagem de Conta             |
| GOLPE_08  | falso_investimento     | Falso Investimento / Pirâmide |
| GOLPE_09  | golpe_suporte_tecnico  | Golpe de Suporte Técnico      |
| GOLPE_10  | golpe_qr_code          | Golpe do QR Code              |
| GOLPE_11  | golpe_delivery         | Golpe de Delivery / Compra    |
| —         | legitimo               | Conteúdo Legítimo             |

---

## Métricas de avaliação (v2)

| Avaliação                        | Resultado        |
|----------------------------------|------------------|
| Acurácia hold-out (20%)          | 72.22%           |
| F1 cross-validation 5-fold       | 76.75% ± 11.05%  |
| Acurácia conjunto manual         | 100% (19/19)     |
| Falsos positivos (conjunto manual)| 0               |
| Falsos negativos (conjunto manual)| 0               |

---

## Instalação

### 1. Clone e configure

```bash
cd discovery_ai
cp .env.example .env
# Edite o .env e adicione sua MARITACA_API_KEY
```

### 2. Obtenha sua API Key Maritaca (gratuita)

1. Acesse [plataforma.maritaca.ai](https://plataforma.maritaca.ai)
2. Crie conta e gere sua API Key
3. Adicione no `.env`: `MARITACA_API_KEY=sua_chave`

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Setup inicial

```bash
python scripts/setup_and_test.py
```

### 5. Suba a API

```bash
cd api && python main.py
# Documentação: http://localhost:8000/docs
```

### Com Docker

```bash
docker build -t discovery-ai .
docker run -p 8000:8000 --env-file .env discovery-ai
```

---

## Endpoints da API (v2)

### Análise

| Método | Rota                      | Descrição                                      |
|--------|---------------------------|------------------------------------------------|
| POST   | `/api/analyze`            | Análise completa de texto ou mensagem          |
| POST   | `/api/analyze/situation`  | Análise de situação descrita em linguagem natural |
| POST   | `/api/analyze/url`        | Análise de URL específica                      |
| POST   | `/api/analyze/batch`      | Análise em lote (ML local, sem custo de API)   |

### Informação

| Método | Rota            | Descrição                              |
|--------|-----------------|----------------------------------------|
| GET    | `/api/health`   | Health check                           |
| GET    | `/api/taxonomy` | Lista todos os tipos de golpe          |
| GET    | `/api/stats`    | Estatísticas da sessão                 |
| GET    | `/api/evaluation` | Relatório de acurácia (precision/recall/F1) |

### Administração

| Método | Rota                      | Descrição                              |
|--------|---------------------------|----------------------------------------|
| GET    | `/api/config`             | Lê configurações atuais                |
| POST   | `/api/config/reload`      | Recarrega config.json sem reiniciar    |
| POST   | `/api/rag/rebuild`        | Reconstrói índice FAISS                |
| POST   | `/api/classifier/retrain` | Re-treina o classificador ML           |

---

## Exemplos de uso

### Análise de texto/mensagem

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Sua conta foi bloqueada. Clique aqui para reativar urgente.",
    "use_sabia": false,
    "source": "whatsapp"
  }'
```

### Análise de situação (linguagem natural)

```bash
curl -X POST http://localhost:8000/api/analyze/situation \
  -H "Content-Type: application/json" \
  -d '{
    "situation": "Fui a um site de compras e ele pediu que eu lesse um QR code pela câmera do celular para finalizar o pagamento. Nunca vi isso antes.",
    "use_sabia": false
  }'
```

### Relatório de avaliação

```bash
# Via terminal
python scripts/evaluation_report.py

# Via API
curl http://localhost:8000/api/evaluation
```

### Resposta típica

```json
{
  "success": true,
  "data": {
    "is_suspicious": true,
    "risk_level": "ALTO",
    "fraud_type": "phishing",
    "fraud_code": "GOLPE_01",
    "confidence": 0.89,
    "explanation": "Mensagem típica de phishing com urgência artificial...",
    "recommendations": ["Não clique no link", "Contate o banco pelo número oficial"],
    "indicators": ["Urgência artificial", "Solicitação de dados"],
    "analysis_time_ms": 12
  }
}
```

---

## Parametrização (config.json)

Edite `data/config.json` para ajustar o comportamento sem mexer no código:

```json
{
  "risk_thresholds": {
    "alto":  { "suspicious_prob_min": 0.80, "confidence_min": 0.60 },
    "medio": { "suspicious_prob_min": 0.60, "confidence_min": 0.30 }
  },
  "modules": {
    "use_sabia_by_default": false,
    "use_link_analyzer": true,
    "use_rag": true
  },
  "rag": {
    "top_k_chunks": 3,
    "chunk_size": 400
  }
}
```

Após editar, recarregue sem reiniciar:

```bash
curl -X POST http://localhost:8000/api/config/reload
```

---

## Expandindo a base de conhecimento

Para adicionar novos tipos de golpe ao RAG:

1. Edite `data/knowledge_base/taxonomia_golpes.md`
2. Reconstrua o índice:
```bash
curl -X POST http://localhost:8000/api/rag/rebuild
```

Para adicionar novos exemplos ao classificador ML:

1. Edite `TRAINING_DATA` em `classifier/ml_classifier.py`
2. Re-treine:
```bash
curl -X POST http://localhost:8000/api/classifier/retrain \
  -H "Content-Type: application/json" \
  -d '{"model_type": "logreg"}'
```

---

## Integração com o back-end Next.js

```javascript
// pages/api/analyze.js
export default async function handler(req, res) {
  const aiResponse = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: req.body.text,
      use_sabia: false,       // true quando quiser análise profunda
      source: req.body.source
    })
  });
  const data = await aiResponse.json();
  res.json(data);
}

// pages/api/analyze-situation.js
export default async function handler(req, res) {
  const aiResponse = await fetch('http://localhost:8000/api/analyze/situation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation: req.body.situation, use_sabia: false })
  });
  const data = await aiResponse.json();
  res.json(data);
}
```

---

## Tecnologias utilizadas

| Tecnologia              | Papel                                    | Custo           |
|-------------------------|------------------------------------------|-----------------|
| sentence-transformers   | Embeddings multilíngues para o RAG       | Gratuito (local)|
| FAISS (Meta AI)         | Banco vetorial para busca semântica      | Gratuito (local)|
| scikit-learn            | Pipeline ML: TF-IDF + LogReg             | Gratuito (local)|
| NLTK                    | Stopwords PT + stemmer RSLP              | Gratuito (local)|
| Maritaca AI (Sabiá-3)   | LLM em português para análise profunda   | ~R$0,01/mês     |
| FastAPI + uvicorn       | API REST com documentação automática     | Gratuito        |
| tldextract              | Análise de componentes de URL            | Gratuito (local)|
| joblib                  | Serialização do modelo ML em disco       | Gratuito (local)|

---

## Requisitos funcionais atendidos

| RF   | Descrição                              | Módulo/Arquivo                          |
|------|----------------------------------------|-----------------------------------------|
| RF02 | Taxonomia de 11 tipos de golpe         | `data/knowledge_base/taxonomia_golpes.md` |
| RF03 | Classificador ML leve                  | `classifier/ml_classifier.py`           |
| RF04 | Análise de links suspeitos             | `analyzer/link_analyzer.py`             |
| RF07 | API interna REST                       | `api/main.py`                           |
| —    | RAG + Sabiá                            | `rag/rag_engine.py` + `rag/sabia_client.py` |
| —    | Análise de situações                   | `analyzer/situation_analyzer.py`        |
| —    | Parametrização central                 | `config/settings.py` + `data/config.json` |
| —    | Relatório de avaliação (P/R/F1)        | `scripts/evaluation_report.py`          |
