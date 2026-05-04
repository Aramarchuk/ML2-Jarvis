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
