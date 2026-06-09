"""
rag/rag_engine.py
Motor RAG (Retrieval-Augmented Generation) do dIscovery.

Fluxo:
1. Carrega e chunca os documentos de taxonomia
2. Gera embeddings locais (sentence-transformers, gratuito)
3. Indexa no FAISS (vetorial, em memória ou disco)
4. Na consulta: busca chunks relevantes → monta prompt → chama Sabiá
"""

import os
import re
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
VECTOR_STORE_PATH = Path(os.getenv("RAG_VECTOR_STORE_PATH", "./data/vector_store"))
KNOWLEDGE_BASE_PATH = Path(os.getenv("RAG_KNOWLEDGE_BASE_PATH", "./data/knowledge_base"))
CHUNK_SIZE = 400        # caracteres por chunk
CHUNK_OVERLAP = 80      # sobreposição entre chunks
TOP_K = 3               # quantidade de chunks recuperados por consulta


class RAGEngine:
    """
    Motor RAG completo: indexação + recuperação + geração via Sabiá.
    """

    def __init__(self):
        print("[RAG] Carregando modelo de embeddings...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.index: Optional[faiss.IndexFlatL2] = None
        self.chunks: list[str] = []
        self.chunk_sources: list[str] = []
        VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

        # Tenta carregar índice salvo; caso contrário indexa do zero
        if self._index_exists():
            self._load_index()
        else:
            self.build_index()

    # ------------------------------------------------------------------
    # INDEXAÇÃO
    # ------------------------------------------------------------------

    def build_index(self):
        """Lê todos os .md/.txt da base de conhecimento e constrói o índice FAISS."""
        print("[RAG] Construindo índice vetorial...")
        docs = self._load_documents()
        if not docs:
            raise FileNotFoundError(f"Nenhum documento encontrado em {KNOWLEDGE_BASE_PATH}")

        self.chunks = []
        self.chunk_sources = []

        for source, text in docs.items():
            for chunk in self._split_chunks(text):
                self.chunks.append(chunk)
                self.chunk_sources.append(source)

        print(f"[RAG] {len(self.chunks)} chunks gerados. Gerando embeddings...")
        embeddings = self.embedder.encode(self.chunks, show_progress_bar=True, normalize_embeddings=True)
        embeddings = embeddings.astype(np.float32)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner Product (cosine após normalização)
        self.index.add(embeddings)

        self._save_index()
        print(f"[RAG] Índice construído com {self.index.ntotal} vetores.")

    def _load_documents(self) -> dict[str, str]:
        docs = {}
        for path in KNOWLEDGE_BASE_PATH.rglob("*"):
            if path.suffix in (".md", ".txt") and path.is_file():
                docs[path.name] = path.read_text(encoding="utf-8")
        return docs

    def _split_chunks(self, text: str) -> list[str]:
        """Divide texto em chunks com sobreposição, respeitando parágrafos quando possível."""
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        chunks = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) <= CHUNK_SIZE:
                current = (current + "\n\n" + para).strip()
            else:
                if current:
                    chunks.append(current)
                    # overlap: pega o final do chunk anterior
                    overlap_text = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else current
                    current = (overlap_text + "\n\n" + para).strip()
                else:
                    # parágrafo maior que CHUNK_SIZE: força corte
                    for i in range(0, len(para), CHUNK_SIZE - CHUNK_OVERLAP):
                        chunks.append(para[i: i + CHUNK_SIZE])
                    current = ""

        if current:
            chunks.append(current)
        return chunks

    # ------------------------------------------------------------------
    # RECUPERAÇÃO
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """Retorna os chunks mais relevantes para a query."""
        if self.index is None or self.index.ntotal == 0:
            return []

        query_vec = self.embedder.encode([query], normalize_embeddings=True).astype(np.float32)
        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append({
                    "chunk": self.chunks[idx],
                    "source": self.chunk_sources[idx],
                    "score": float(score),
                })
        return results

    def build_context(self, query: str) -> str:
        """Monta o contexto RAG para injetar no prompt do Sabiá."""
        retrieved = self.retrieve(query)
        if not retrieved:
            return "Nenhuma informação relevante encontrada na base de conhecimento."

        context_parts = []
        for i, r in enumerate(retrieved, 1):
            context_parts.append(
                f"[Trecho {i} - Fonte: {r['source']} | Relevância: {r['score']:.2f}]\n{r['chunk']}"
            )
        return "\n\n---\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # PERSISTÊNCIA DO ÍNDICE
    # ------------------------------------------------------------------

    def _index_exists(self) -> bool:
        return (VECTOR_STORE_PATH / "index.faiss").exists() and \
               (VECTOR_STORE_PATH / "chunks.pkl").exists()

    def _save_index(self):
        faiss.write_index(self.index, str(VECTOR_STORE_PATH / "index.faiss"))
        with open(VECTOR_STORE_PATH / "chunks.pkl", "wb") as f:
            pickle.dump({"chunks": self.chunks, "sources": self.chunk_sources}, f)
        print(f"[RAG] Índice salvo em {VECTOR_STORE_PATH}")

    def _load_index(self):
        self.index = faiss.read_index(str(VECTOR_STORE_PATH / "index.faiss"))
        with open(VECTOR_STORE_PATH / "chunks.pkl", "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.chunk_sources = data["sources"]
        print(f"[RAG] Índice carregado: {self.index.ntotal} vetores, {len(self.chunks)} chunks.")

    def rebuild(self):
        """Força reconstrução do índice (use quando adicionar documentos)."""
        if (VECTOR_STORE_PATH / "index.faiss").exists():
            (VECTOR_STORE_PATH / "index.faiss").unlink()
        if (VECTOR_STORE_PATH / "chunks.pkl").exists():
            (VECTOR_STORE_PATH / "chunks.pkl").unlink()
        self.build_index()


# Instância singleton (lazy)
_rag_instance: Optional[RAGEngine] = None


def get_rag() -> RAGEngine:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGEngine()
    return _rag_instance
