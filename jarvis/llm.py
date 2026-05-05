from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib import error, request


class LLMError(RuntimeError):
    """Raised when the LLM backend cannot produce a response."""


class ChatClient(Protocol):
    def generate_reply(self, history: list[dict[str, str]]) -> str:
        ...


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


@dataclass(slots=True)
class OpenAICompatibleClient:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: int = 120

    def generate_reply(self, history: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise LLMError(
                "No API key is configured for the OpenAI-compatible backend. "
                "Set JARVIS_LLM_API_KEY or provide API_KEY in .env."
            )

        payload = json.dumps(
            {
                "model": self.model,
                "messages": history,
            }
        ).encode("utf-8")
        http_request = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            details = OllamaClient._read_http_error(exc)
            raise LLMError(
                f"OpenAI-compatible request failed with HTTP {exc.code} at "
                f"{self.base_url}/chat/completions. Model: {self.model}. Details: {details}"
            ) from exc
        except error.URLError as exc:
            raise LLMError(
                f"Could not reach the OpenAI-compatible endpoint at {self.base_url}. "
                f"Model: {self.model}. Reason: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise LLMError(
                f"OpenAI-compatible request timed out after {self.timeout_seconds} seconds at "
                f"{self.base_url}/chat/completions. Model: {self.model}."
            ) from exc

        try:
            response_payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise LLMError(
                "The OpenAI-compatible endpoint returned invalid JSON. "
                f"Response preview: {OllamaClient._preview(raw_body)}"
            ) from exc

        try:
            content = response_payload["choices"][0]["message"]["content"].strip()
        except (KeyError, TypeError, IndexError, AttributeError) as exc:
            raise LLMError(
                "The OpenAI-compatible endpoint returned an unexpected response payload. "
                f"Payload preview: {OllamaClient._preview(raw_body)}"
            ) from exc

        if not content:
            raise LLMError(
                "The OpenAI-compatible endpoint returned an empty response for model "
                f"{self.model}. Payload preview: {OllamaClient._preview(raw_body)}"
            )

        return content
