# dIscovery - Detecção de Golpes e Fraudes Digitais

## Sobre o Projeto

O **dIscovery** é uma solução para detecção automatizada de golpes e fraudes digitais em redes sociais, mensagerias e páginas web. O sistema utiliza técnicas de Processamento de Linguagem Natural (NLP), busca semântica (RAG) e modelos de linguagem para classificar conteúdos suspeitos.

**Contexto:** Projeto desenvolvido no âmbito do Programa de Residência em TIC do MCTI, em parceria com a UFG/INF e a Anatel (dAurora).

---

## Tecnologias Utilizadas

| Camada | Tecnologia |
|--------|------------|
| Frontend | Next.js (React) |
| Backend | FastAPI (Python 3.10+) |
| Banco de Dados | PostgreSQL (Neon) |
| IA/ML | Sabiá-3, RAG |
| Containerização | Docker / Docker Compose |
| Versionamento | Git + GitHub |

---

## Funcionalidades Principais

- Análise de textos e links suspeitos
- Classificação por tipo de golpe (phishing, pix falso, etc.)
- Score de risco e recomendações
- Dashboard com estatísticas e histórico
- API REST para consumo externo
- Relatórios em PDF

---

## Como Executar o Projeto

### Pré-requisitos
- Docker e Docker Compose
- Node.js 18+ (para desenvolvimento frontend)
- Python 3.10+ (para desenvolvimento backend)

### Execução com Docker (recomendado)

```bash
git clone [URL_DO_REPOSITORIO]
cd S07-dAurora-Anatel
docker-compose up --build
