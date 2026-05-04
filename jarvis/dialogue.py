from __future__ import annotations

from dataclasses import dataclass, field


Message = dict[str, str]


@dataclass
class DialogueManager:
    system_prompt: str
    history: list[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.history = [{"role": "system", "content": self.system_prompt}]

    def append_message(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def build_messages(self) -> list[Message]:
        return list(self.history)

    def build_messages_with_context(
        self,
        session_context: str = "",
        tool_result: str = "",
    ) -> list[Message]:
        messages = list(self.history)
        if not session_context and not tool_result:
            return messages

        insert_parts: list[str] = []
        if session_context:
            insert_parts.append(f"Short-term session context:\n{session_context}")
        if tool_result:
            insert_parts.append(f"Tool result:\n{tool_result}")

        messages.insert(
            1,
            {
                "role": "system",
                "content": "\n\n".join(insert_parts),
            },
        )
        return messages
