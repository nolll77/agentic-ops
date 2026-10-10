import os
from pathlib import Path
from agentic_ops.adapters.protocol import KnowledgeAdapter

class LocalRunbookRAG(KnowledgeAdapter):
    """
    Simule une VectorDB en lisant le Markdown correspondant au risk_id,
    ou en effectuant une recherche Full-Text naïve.
    En production : branché sur ChromaDB, Pinecone ou Qdrant.
    """
    def __init__(self, kb_dir: str = "agentic_ops/knowledge_base/runbooks"):
        self.kb_dir = Path(kb_dir)

    def search_runbooks(self, risk_id: str, query: str) -> str:
        # Recherche directe par ID (Mock de similarité sémantique à 100%)
        target_file = self.kb_dir / f"{risk_id}.md"
        if target_file.exists():
            with open(target_file, "r") as f:
                content = f.read()
            return f"--- KNOWLEDGE BASE MATCH (Score: 0.98) ---\n{content}\n--- END OF KNOWLEDGE ---"
        return "Aucun historique d'incident similaire trouvé dans la base de connaissance."
