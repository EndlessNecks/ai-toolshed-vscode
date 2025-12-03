# orchestration/codestral_orchestrator.py

from typing import Any, Callable, Dict, List, Optional
from orchestration.codestral_client import CodestralClient

# Type aliases for clarity
Document = Dict[str, Any]
RetrieveFn = Callable[[str, int], List[Document]]


class CodestralOrchestrator:
    """
    Sits between the RAG stack and the Codestral model.

    Responsibilities:
      - Take user queries
      - Retrieve relevant context using RAG
      - Construct the system + user prompt
      - Send to CodestralClient
      - Return the model's response

    This orchestrator is model-agnostic and editor-agnostic.
    Continue / VS Code integrations live elsewhere.
    """

    def __init__(
        self,
        retriever_fn: RetrieveFn,
        client: CodestralClient,
        top_k: int = 12,
        max_context_chars: int = 12_000,
    ) -> None:
        """
        :param retriever_fn: callable(query: str, top_k: int) -> List[Document]
                             Each Document should include:
                               - "content": str
                               - "metadata": dict (optional)
        :param client: Required CodestralClient instance
        :param top_k: number of retrieved chunks
        :param max_context_chars: soft limit on context block size
        """
        if client is None:
            raise ValueError("CodestralClient must be explicitly provided.")

        self.retriever_fn = retriever_fn
        self.client = client
        self.top_k = top_k
        self.max_context_chars = max_context_chars

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def answer_with_rag(self, query: str, role: str = "technical engineer") -> str:
        """
        Return a Codestral response enriched with retrieved context.
        """
        query = query.strip()
        if not query:
            return "No query provided."

        docs = self.retriever_fn(query, self.top_k)
        context_block = self._format_context(docs)

        messages = [
            {"role": "system", "content": self._build_system_prompt(role)},
            {"role": "user", "content": self._build_user_prompt(query, context_block)},
        ]

        return self.client.simple_answer(messages)

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_system_prompt(self, role: str) -> str:
        """
        How Codestral should behave inside the AI Tool Shed environment.
        """
        return f"""You are Codestral, operating inside an AI development environment known as the AI Tool Shed.

High-level responsibilities:
- Act as a senior engineer integrated with VS Code.
- Read, analyze, and generate code with high precision.
- Use provided context instead of making assumptions.
- Clearly state when required information is missing.

Environment:
- The project uses a modular architecture for local LLM orchestration and RAG:
  - configs/ contains JSON configurations (paths, RAG settings, model parameters).
  - rag_engine/ contains the chunker, embedder, indexer, and retriever.
  - vector_db/ includes ChromaDB storage and a vector_store abstraction.
  - glue_continue/ provides integration with the Continue extension and VS Code.
  - project_watchers/ observes file changes and triggers reindexing.
  - logs/ contains RAG and indexing logs.
  - tests/ provides basic RAG regression tests.

Constraints:
- Retrieved context may be incomplete or slightly outdated.
- Prefer concrete evidence from retrieved context over assumptions.
- When proposing changes, reference specific filenames and relevant functions/classes.

Style guidelines:
- Be direct and practical.
- Provide fully copy-pastable code when suggesting changes.
- If a request is ambiguous, state the assumptions being made.

Role hint: operate primarily in the "{role}" role for this session."""

    def _build_user_prompt(self, query: str, context_block: str) -> str:
        """
        Combine the user question with retrieved contextual snippets.
        """
        return f"""User request:
{query}

Retrieved project context (read-only):
{context_block}

Instructions:
1. FIRST: use the retrieved context.
2. If context contradicts general assumptions, trust the context.
3. When suggesting edits, specify:
   - which file(s) to modify,
   - which function(s) or class(es) to change,
   - and provide the complete patched code blocks.

Now respond to the user request."""

    # ------------------------------------------------------------------
    # Context formatting
    # ------------------------------------------------------------------

    def _format_context(self, docs: List[Document]) -> str:
        """
        Convert retrieved documents into a single formatted block.
        """
        if not docs:
            return "(no context snippets retrieved)"

        parts: List[str] = []
        total_chars = 0

        for i, doc in enumerate(docs, start=1):
            content = str(doc.get("content", "")).strip()
            metadata = doc.get("metadata", {}) or {}

            source = metadata.get("source") or metadata.get("path") or "unknown"
            start_line = metadata.get("start_line")
            end_line = metadata.get("end_line")

            header = f"[{i}] Source: {source}"
            if isinstance(start_line, int) and isinstance(end_line, int):
                header += f" (lines {start_line}-{end_line})"

            chunk = f"{header}\n{content}\n"

            # respect context size limit
            if total_chars + len(chunk) > self.max_context_chars:
                break

            parts.append(chunk)
            total_chars += len(chunk)

        return "\n---\n".join(parts)
