"""In-memory vector and semantic chunk retrieval store."""

from content_agent.tools.embeddings import TextSimilarity


class InMemoryVectorStore:
    """Simple in-memory vector index for semantic chunk matching without external database."""

    def __init__(self):
        self._documents: list[dict[str, str]] = []

    def add_texts(self, texts: list[str], metadatas: list[dict[str, str]] | None = None) -> None:
        for idx, text in enumerate(texts):
            meta = metadatas[idx] if metadatas and idx < len(metadatas) else {}
            self._documents.append({"text": text, "metadata": meta})

    def similarity_search(self, query: str, top_k: int = 3) -> list[dict[str, str]]:
        scored = []
        for doc in self._documents:
            score = TextSimilarity.cosine_similarity(query, doc["text"])
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k]]
