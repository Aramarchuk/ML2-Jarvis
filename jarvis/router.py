from __future__ import annotations

from dataclasses import dataclass
import json

from jarvis.llm import ChatClient, LLMError


@dataclass(slots=True)
class RouteDecision:
    route: str
    tool_name: str | None
    arguments: dict[str, object]
    reason: str
    confidence: float


class RouterError(RuntimeError):
    """Raised when the router cannot produce a usable decision."""


@dataclass(slots=True)
class LLMRouter:
    llm_client: ChatClient
    confidence_threshold: float

    def decide(
        self,
        user_text: str,
        session_context: str,
        tool_catalog: list[dict[str, object]],
    ) -> RouteDecision:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a routing model for Jarvis. "
                    "Return JSON only. Decide whether the request should use normal chat "
                    "or one tool from the provided catalog. "
                    "Be conservative. If unsure, choose chat."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Session context:\n{session_context or 'No prior session context.'}\n\n"
                    f"Available tools:\n{json.dumps(tool_catalog, indent=2)}\n\n"
                    "Return a JSON object with keys: route, tool_name, arguments, reason, confidence.\n"
                    "Allowed route values: chat, tool.\n"
                    f"Current user message:\n{user_text}"
                ),
            },
        ]

        try:
            raw_reply = self.llm_client.generate_reply(messages)
        except LLMError as exc:
            raise RouterError(f"The router could not get a response from the LLM: {exc}") from exc

        try:
            payload = self._parse_json_object(raw_reply)
            decision = RouteDecision(
                route=str(payload["route"]),
                tool_name=payload.get("tool_name"),
                arguments=payload.get("arguments") or {},
                reason=str(payload.get("reason", "")),
                confidence=float(payload.get("confidence", 0.0)),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RouterError(
                "The router returned invalid JSON. "
                f"Raw reply: {self._preview(raw_reply)}"
            ) from exc

        if decision.route not in {"chat", "tool"}:
            raise RouterError("The router returned an unsupported route.")
        if not isinstance(decision.arguments, dict):
            raise RouterError("The router returned invalid tool arguments.")
        if decision.route == "tool" and not decision.tool_name:
            raise RouterError("The router selected tool routing without a tool name.")
        if decision.confidence < self.confidence_threshold:
            return RouteDecision(
                route="chat",
                tool_name=None,
                arguments={},
                reason="Router confidence was below the configured threshold.",
                confidence=decision.confidence,
            )
        return decision

    @staticmethod
    def _parse_json_object(raw_reply: str) -> dict[str, object]:
        start = raw_reply.find("{")
        end = raw_reply.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise json.JSONDecodeError("No JSON object found.", raw_reply, 0)
        return json.loads(raw_reply[start : end + 1])

    @staticmethod
    def _preview(text: str, limit: int = 300) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[:limit] + "..."
