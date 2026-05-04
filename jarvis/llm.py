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
        except error.HTTPError as exc:
            details = self._read_http_error(exc)
            raise LLMError(
                f"Ollama request failed with HTTP {exc.code} at {self.base_url}/api/chat. "
                f"Model: {self.model}. Details: {details}"
            ) from exc
        except error.URLError as exc:
            raise LLMError(
                f"Could not reach Ollama at {self.base_url}. Model: {self.model}. "
                f"Reason: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise LLMError(
                f"Ollama request timed out after {self.timeout_seconds} seconds at "
                f"{self.base_url}/api/chat. Model: {self.model}."
            ) from exc

        try:
            response_payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise LLMError(
                "Ollama returned an invalid JSON response. "
                f"Response preview: {self._preview(raw_body)}"
            ) from exc

        try:
            content = response_payload["message"]["content"].strip()
        except (KeyError, TypeError) as exc:
            raise LLMError(
                "Ollama returned an unexpected response payload. "
                f"Payload preview: {self._preview(raw_body)}"
            ) from exc

        if not content:
            raise LLMError(
                f"Ollama returned an empty response for model {self.model}. "
                f"Payload preview: {self._preview(raw_body)}"
            )

        return content

    @staticmethod
    def _preview(text: str, limit: int = 300) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[:limit] + "..."

    @classmethod
    def _read_http_error(cls, exc: error.HTTPError) -> str:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            return "No response body available."
        return cls._preview(body)
