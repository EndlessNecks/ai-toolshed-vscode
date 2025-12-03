#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
vscode_hooks.py — VS Code / Continue integration point.

This routes all logic through:
    • Codestral binding layer (creates orchestrator from Continue config)
    • RAG retriever
    • CodestralOrchestrator (final prompt assembly + model output)
"""

from typing import Dict, Any

from rag_engine.retriever import load_retriever
from glue_continue.codestral_binding import create_orchestrator_from_continue

# Global orchestrator instance (set when Continue loads a model)
_orchestrator = None


# =====================================================================
# CALLED BY CONTINUE WHEN A MODEL IS LOADED
# =====================================================================

def on_model_loaded(model_config: Dict[str, Any]) -> None:
    """
    Continue calls this after loading a model.

    model_config example:
        {
            "model": "codestral-latest",
            "api_base": "http://localhost:11434/v1",
            "api_key": "",
            "temperature": 0.2,
            "max_tokens": 4096
        }
    """
    global _orchestrator

    # Initialize retriever (RAG vector store)
    retriever = load_retriever()

    # Build orchestrator using binding layer
    _orchestrator = create_orchestrator_from_continue(
        model_config=model_config,
        retriever_fn=retriever.retrieve
    )


# =====================================================================
# CALLED BY CONTINUE WHEN USER SENDS A MESSAGE
# =====================================================================

def handle_user_query(query: str) -> str:
    """
    Continue forwards every user message to this handler.

    Returns final RAG-augmented Codestral response.
    """
    global _orchestrator

    if _orchestrator is None:
        return "Model not initialized. Load a model first."

    return _orchestrator.answer_with_rag(query)


# =====================================================================
# OPTIONAL CLI SUPPORT (useful for debugging)
# =====================================================================

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="VS Code → Tool Shed Orchestrator Hook")
    parser.add_argument("--query", required=True, help="User query text")

    args = parser.parse_args()

    if _orchestrator is None:
        print("Error: Orchestrator not initialized — this script is normally invoked by Continue.")
    else:
        output = _orchestrator.answer_with_rag(args.query)
        print(json.dumps({"response": output}, indent=2))
