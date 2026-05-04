from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request


class LLMError(RuntimeError):
    """Raised when the LLM backend cannot produce a response."""


@dataclass(slots=True)
class OllamaClient:
    base_url: str
    model: str
    timeout_seconds: int = 120

    def generate_reply(self, history: list[dict[str, str]]) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": history,
                "stream": False,
            }
        ).encode("utf-8")
        http_request = request.Request(
            url=f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
        except (error.URLError, TimeoutError) as exc:
            raise LLMError(
                "Could not reach Ollama. Make sure Ollama is running and the model is available."
            ) from exc

        try:
            response_payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise LLMError("Ollama returned an invalid JSON response.") from exc

        try:
            content = response_payload["message"]["content"].strip()
        except (KeyError, TypeError) as exc:
            raise LLMError("Ollama returned an unexpected response payload.") from exc

        if not content:
            raise LLMError("Ollama returned an empty response.")

        return content
