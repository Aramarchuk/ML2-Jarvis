from __future__ import annotations

from dataclasses import dataclass, field
import re


@dataclass(slots=True)
class SessionTurn:
    user_text: str
    assistant_text: str


@dataclass(slots=True)
class SessionMemory:
    summary_interval: int = 4
    recent_turn_limit: int = 4
    summary: str = ""
    active_facts: list[str] = field(default_factory=list)
    last_topics: list[str] = field(default_factory=list)
    open_loops: list[str] = field(default_factory=list)
    turns: list[SessionTurn] = field(default_factory=list)

    def update(self, user_text: str, assistant_text: str) -> None:
        self.turns.append(SessionTurn(user_text=user_text, assistant_text=assistant_text))
        self._update_active_facts(user_text)
        self._update_topics(user_text)
        self._update_open_loops(user_text, assistant_text)
        self._refresh_summary_if_needed()

    def build_context_block(self) -> str:
        parts: list[str] = []

        if self.summary:
            parts.append(f"Session summary: {self.summary}")
        if self.active_facts:
            parts.append(
                "Active facts: " + "; ".join(self.active_facts[-self.recent_turn_limit :])
            )
        if self.last_topics:
            parts.append(
                "Recent topics: " + ", ".join(self.last_topics[-self.recent_turn_limit :])
            )
        if self.open_loops:
            parts.append(
                "Open loops: " + "; ".join(self.open_loops[-self.recent_turn_limit :])
            )

        return "\n".join(parts)

    def reset(self) -> None:
        self.summary = ""
        self.active_facts.clear()
        self.last_topics.clear()
        self.open_loops.clear()
        self.turns.clear()

    def get_recent_turns(self) -> list[SessionTurn]:
        return list(self.turns[-self.recent_turn_limit :])

    def _refresh_summary_if_needed(self) -> None:
        if len(self.turns) < self.summary_interval:
            return
        if len(self.turns) % self.summary_interval != 0:
            return

        slice_end = max(0, len(self.turns) - self.recent_turn_limit)
        older_turns = self.turns[:slice_end]
        if not older_turns:
            return

        summary_parts = [
            f"User: {turn.user_text} Assistant: {turn.assistant_text}"
            for turn in older_turns[-self.summary_interval :]
        ]
        self.summary = " | ".join(summary_parts)

    def _update_active_facts(self, user_text: str) -> None:
        patterns = [
            r"\bmy name is ([^.?!]+)",
            r"\bi prefer ([^.?!]+)",
            r"\bi am working on ([^.?!]+)",
            r"\bremember that ([^.?!]+)",
            r"\bmy goal is ([^.?!]+)",
        ]
        lowered = user_text.lower()
        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                fact = match.group(0).strip()
                if fact not in self.active_facts:
                    self.active_facts.append(fact)

    def _update_topics(self, user_text: str) -> None:
        cleaned = user_text.strip()
        if not cleaned:
            return
        topic = " ".join(cleaned.split()[:6])
        if not self.last_topics or self.last_topics[-1] != topic:
            self.last_topics.append(topic)

    def _update_open_loops(self, user_text: str, assistant_text: str) -> None:
        if "?" in user_text:
            prompt = user_text.strip()
            if prompt not in self.open_loops:
                self.open_loops.append(prompt)

        if self.open_loops and "?" not in assistant_text:
            self.open_loops = self.open_loops[-self.recent_turn_limit :]
