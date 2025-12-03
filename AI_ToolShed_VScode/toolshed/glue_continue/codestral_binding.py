# glue_continue/codestral_binding.py

from typing import Dict, Callable
from orchestration.codestral_client import CodestralClient, CodestralConfig
from orchestration.codestral_orchestrator import CodestralOrchestrator


def create_orchestrator_from_continue(
    model_config: Dict,
    retriever_fn: Callable[[str, int], list],
) -> CodestralOrchestrator:
    """
    Convert Continue's model configuration dictionary into a
    CodestralConfig → CodestralClient → CodestralOrchestrator pipeline.

    Continue passes a model config dict shaped like:
      {
        "model": "codestral-latest",
        "api_base": "http://localhost:11434/v1",
        "api_key": "",
        "temperature": 0.2,
        "max_tokens": 4096,
        ...
      }

    This function standardizes the config and initializes the orchestrator.
    """

    # Convert Continue's config → our CodestralConfig
    cfg = CodestralConfig.from_dict(model_config)

    # Build client
    client = CodestralClient(cfg)

    # Build orchestrator
    orchestrator = CodestralOrchestrator(
        retriever_fn=retriever_fn,
        client=client,
    )

    return orchestrator
