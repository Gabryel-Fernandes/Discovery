# 🔍 dIscovery - Detecção de Golpes e Fraudes Digitais

[![Status](https://img.shields.io/badge/status-finalizado-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)]()

**Parceiro:** dAurora | Anatel  
**Residência:** BRISA - UFG (Turma 2)  
**Período:** 8 semanas  

---

## 📌 Sobre o Projeto

O **dIscovery** é uma plataforma automatizada para detecção e classificação de golpes e fraudes digitais em redes sociais, aplicativos de mensageria e páginas web. Desenvolvido em parceria com a **dAurora/Anatel**, o sistema auxilia na triagem de conteúdos suspeitos, permitindo que equipes humanas priorizem e atuem com mais eficiência.

**Diferenciais:**
- 🇧🇷 Focado no contexto brasileiro (PIX, "Urubu do Pix", Gov.br)
- 🤖 Abordagem híbrida (ML local + LLM + RAG)
- 🐳 100% containerizado com Docker
- ⚡ Análise em menos de 5 segundos

---

## 🏗️ Arquitetura da Solução

```
TEXTO / URL
     │
     ▼
┌─────────────────┐
│  ML Classifier  │ ← Naive Bayes (local, rápido)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Link Analyzer  │ ← Typosquatting, encurtadores, HTTPS
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAG Engine    │ ← FAISS + sentence-transformers
└────────┬────────┘
         │ contexto
         ▼
┌─────────────────┐
│   Sabiá-3 API   │ ← Maritaca AI (análise profunda)
└────────┬────────┘
         │
         ▼
   RESULTADO FINAL
  (risco + tipo + explicação)
```

**Por que essa arquitetura híbrida?**
- **ML Classifier** → resposta imediata (menos de 1s)
- **Link Analyzer** → verificação estrutural sem custo
- **RAG** → contexto rico sobre tipos de golpe
- **Sabiá-3** → profundidade e nuance quando necessário

---

## 🚀 Execução Rápida

### Pré-requisitos
- Docker e Docker Compose
- Git

### Com Docker (recomendado)

```bash
git clone https://github.com/Gabryel-Fernandes/S07-dAurora-Anatel.git
cd S07-dAurora-Anatel
docker-compose up --build
```

**Acesse:**
- 🌐 **Frontend:** http://localhost:3000
- 📡 **API IA:** http://localhost:8000/docs
- 🔌 **API Backend:** http://localhost:8001/docs

### Sem Docker (desenvolvimento)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Módulo de IA:**
```bash
cd IA
cp .env.example .env
# Edite .env com sua MARITACA_API_KEY
pip install -r requirements.txt
python scripts/setup_and_test.py
cd api && python main.py
```

---

## 📋 API - Endpoints Principais

### Módulo de IA (porta 8000)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/analyze` | Análise completa de texto |
| `POST` | `/api/analyze/url` | Análise de URL |
| `POST` | `/api/analyze/batch` | Análise em lote |
| `GET` | `/api/taxonomy` | Lista de tipos de golpes |
| `POST` | `/api/rag/rebuild` | Reconstrói índice RAG |

### Exemplo de Requisição

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Sua conta foi bloqueada. Clique em http://bit.ly/banco-seguro",
    "use_sabia": true,
    "source": "whatsapp"
  }'
```

### Exemplo de Resposta

```json
{
  "success": true,
  "data": {
    "is_suspicious": true,
    "risk_level": "ALTO",
    "fraud_type": "phishing",
    "confidence": 0.94,
    "explanation": "Mensagem contém encurtador de URL e senso de urgência...",
    "recommendations": ["Não clique no link", "Contate o banco oficialmente"],
    "analysis_time_ms": 1243
  }
}
```

---

## 📂 Estrutura do Repositório

```
S07-dAurora-Anatel/
├── frontend/              # Next.js (interface do usuário)
├── backend/               # FastAPI (lógica principal)
├── IA/                    # Módulo completo de IA
│   ├── api/               # Endpoints FastAPI
│   ├── rag/               # RAG Engine (FAISS + Sabiá)
│   ├── classifier/        # ML (Naive Bayes)
│   ├── analyzer/          # Link + orquestração
│   ├── data/              # Taxonomia em Markdown
│   └── scripts/           # Setup e testes
├── Documentacao/          # Pesquisas, protótipo, requisitos
├── Slides da Proposta/    # Apresentações
├── docker-compose.yaml
├── PRD-Avaliação Parcial-SO7.pdf
└── README.md
```

---

## 🧠 Taxonomia de Golpes Implementada

| Código | Tipo | Exemplo |
|--------|------|---------|
| `GOLPE_01` | Phishing | Link falso do banco/Gov.br |
| `GOLPE_02` | Golpe do PIX | "Urubu do Pix", Pix errado |
| `GOLPE_03` | Falso Investimento | Criptomoedas, day trade |
| `GOLPE_04` | Falsa Central | Atendimento falso |
| `GOLPE_05` | Roubo de Identidade | Clonagem WhatsApp |
| `GOLPE_06` | Falso Comércio | Loja falsa, leilão falso |
| `GOLPE_07` | Falso Benefício | Bolsa Família, FGTS |
| `GOLPE_08` | Pirâmide Financeira | Esquema Ponzi |
| `GOLPE_09` | Falso Sorteio | Promoção falsa |
| `GOLPE_10` | Engenharia Social | Urgência, autoridade |

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Custo |
|------------|------------|-------|
| **Frontend** | Next.js / React | Gratuito |
| **Backend** | FastAPI (Python) | Gratuito |
| **Container** | Docker + Compose | Gratuito |
| **ML Classifier** | scikit-learn (Naive Bayes) | Gratuito |
| **Embeddings** | sentence-transformers | Gratuito |
| **Vector DB** | FAISS (Meta) | Gratuito |
| **LLM** | Sabiá-3 (Maritaca AI) | Freemium |
| **Análise de Links** | Heurísticas + whois | Gratuito |

---

## 👥 Equipe

| Nome | Papel | GitHub |
|------|-------|--------|
| Gabryel Fernandes | Frontend / DevOps | @Gabryel-Fernandes |
| Fernando Assunção | Backend / Integração | @fdsassuncao |
| Vitória Sofia | IA / Modelos | @VitoriaSofiaa |
| Victor Alves | Documentação / Slides | @alves-gvictor |
| Thâmara Cordeiro | Gerência / Documentação | @thamaraprata |

---

## 📄 Documentação Adicional

- [Product Requirements Document (PRD)](./PRD-Avaliação%20Parcial-SO7.pdf)
- [Documentação Completa](./Documentacao/)
- [README do Módulo de IA](./IA/README.md)

---

## ✅ Status do Projeto

| Entregável | Status |
|------------|--------|
| Código funcional | ✅ Completo |
| Módulo de IA (RAG + Sabiá) | ✅ Completo |
| Frontend responsivo | ✅ Completo |
| API documentada | ✅ Completo |
| Dockerizado | ✅ Completo |
| PRD e documentação | ✅ Completo |
| Apresentação Demo Day | 🔄 Em produção |

---

## 📅 Demo Day

**Data:** 29/04/2026  
**Horário:** 18h - 22h  
**Local:** Sala 150 - INF/UFG  
**Tempo de apresentação:** 10 minutos

---

## 📝 Licença

Este projeto é desenvolvido no âmbito da **Residência em TIC - BRISA/UFG**, parceria com **dAurora** e **Anatel**.

---

**Desenvolvido para o Programa de Residência em TIC - MCTI/Softex**
