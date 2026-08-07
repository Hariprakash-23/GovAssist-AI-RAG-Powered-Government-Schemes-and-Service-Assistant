"""
GovernmentRAG: retrieval-augmented generation using
ChromaDB (retrieval) + Groq (generation). Replaces the old
FAISS + langchain_ollama version.
"""

from app.embeddings.vector_store import VectorStore
from app.models.groq_client import GroqModel
from app.chatbot.prompts import RAG_PROMPT
from app.chatbot.memory import ChatMemory


class GovernmentRAG:

    def ask(self, question, session_id="default", k=4):
        results = VectorStore.similarity_search(question, k=k)

        context = "\n\n".join(r["text"] for r in results) or "(no matching documents found)"
        history = ChatMemory.get_history_text(session_id)

        prompt = RAG_PROMPT.format(
            context=context,
            history=history,
            question=question
        )

        answer = GroqModel.chat(prompt, temperature=0.2, max_tokens=512)

        ChatMemory.add_turn(session_id, "user", question)
        ChatMemory.add_turn(session_id, "assistant", answer)

        return {
            "answer": answer,
            "sources": [r["metadata"] for r in results]
        }
