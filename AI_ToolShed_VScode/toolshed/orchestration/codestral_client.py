# orchestration/codestral_client.py

import json
from typing import Any, Dict, List, Optional
import requests


class CodestralError(Exception):
    """Raised when the Codestral API call fails."""


class CodestralConfig:
    """
    Configuration container for Codestral model settings.
    Must be supplied by the hosting environment (e.g., Continue).
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @classmethod
    def from_dict(cls, cfg: Dict[str, Any]) -> "CodestralConfig":
        """
        Create a new config from a dict (directly from Continue's config.yaml).
        Only required keys must be present.
        """
        return cls(
            base_url=cfg.get("api_base") or cfg["base_url"],
            model=cfg.get("model"),
            api_key=cfg.get("api_key"),
            temperature=cfg.get("temperature", 0.2),
            max_tokens=cfg.get("max_tokens", 2048),
            timeout=cfg.get("timeout", 60),
        )


class CodestralClient:
    """
    Thin wrapper around an OpenAI-compatible /chat/completions endpoint.
    Does not build prompts—only sends and receives messages.
    """

    def __init__(self, config: CodestralConfig):
        if not isinstance(config, CodestralConfig):
            raise ValueError("CodestralClient requires a CodestralConfig instance.")
        self.config = config

    @property
    def _chat_url(self) -> str:
        # Expected: https://.../v1/chat/completions
        return f"{self.config.base_url}/chat/completions"

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous chat completion call.
        Returns raw JSON from the API.
        """
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        try:
            response = requests.post(
                self._chat_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=self.config.timeout,
            )
        except requests.RequestException as e:
            raise CodestralError(f"Request to Codestral failed: {e}") from e

        if response.status_code != 200:
            raise CodestralError(
                f"Codestral returned HTTP {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise CodestralError(f"Failed to decode JSON from Codestral: {e}") from e

        if "choices" not in data or not data["choices"]:
            raise CodestralError(f"No choices returned from Codestral: {data}")

        return data

    def simple_answer(self, messages: List[Dict[str, Any]]) -> str:
        """Convenience wrapper that returns only the assistant message content."""
        data = self.chat(messages)
        msg = data["choices"][0]["message"]
        return msg.get("content", "") or ""
