from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import ast
import operator
from pathlib import Path
import re
import subprocess

from jarvis.config import AppConfig


class ToolError(RuntimeError):
    """Raised when a tool cannot complete successfully."""


@dataclass(slots=True)
class ToolResult:
    tool_name: str
    output: str


class Tool(ABC):
    name: str
    description: str
    input_schema: dict[str, str]

    @abstractmethod
    def run(self, arguments: dict[str, object]) -> ToolResult:
        raise NotImplementedError


class TimeTool(Tool):
    name = "time"
    description = "Get the current local date and time."
    input_schema: dict[str, str] = {}

    def run(self, arguments: dict[str, object]) -> ToolResult:
        now = datetime.now().astimezone()
        return ToolResult(
            tool_name=self.name,
            output=(
                f"Current local time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')} "
                f"(UTC offset {now.strftime('%z')})."
            ),
        )


class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate a simple arithmetic expression safely."
    input_schema = {"expression": "string"}
    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def run(self, arguments: dict[str, object]) -> ToolResult:
        expression = str(arguments.get("expression", "")).strip()
        if not expression:
            raise ToolError("The calculator tool requires a non-empty expression.")
        try:
            result = self._evaluate(ast.parse(expression, mode="eval").body)
        except Exception as exc:
            raise ToolError("The calculator tool could not evaluate the expression.") from exc
        return ToolResult(
            tool_name=self.name,
            output=f"Expression: {expression}\nResult: {result}",
        )

    def _evaluate(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in self._operators:
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            return self._operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._operators:
            operand = self._evaluate(node.operand)
            return self._operators[type(node.op)](operand)
        raise ToolError("The calculator tool accepts numbers and arithmetic operators only.")


class SystemInfoTool(Tool):
    name = "system_info"
    description = "Return the current assistant mode and configuration summary."
    input_schema: dict[str, str] = {}

    def __init__(self, config: AppConfig, mode: str) -> None:
        self._config = config
        self._mode = mode

    def run(self, arguments: dict[str, object]) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            output=(
                f"Mode: {self._mode}\n"
                f"Model: {self._config.ollama_model}\n"
                f"Language: {self._config.language}\n"
                f"Record seconds: {self._config.record_seconds}\n"
                f"Sample rate: {self._config.sample_rate}"
            ),
        )


class FileSearchTool(Tool):
    name = "file_search"
    description = "Search the local repository for relevant file paths and matching lines."
    input_schema = {"query": "string"}

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def run(self, arguments: dict[str, object]) -> ToolResult:
        query = str(arguments.get("query", "")).strip()
        if not query:
            raise ToolError("The file search tool requires a non-empty query.")
        sanitized = self._sanitize_query(query)
        if not sanitized:
            raise ToolError("The file search query does not contain searchable text.")

        try:
            result = subprocess.run(
                ["rg", "-n", "--max-count", "5", sanitized, str(self._repo_root)],
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise ToolError("ripgrep is not installed, so file search is unavailable.") from exc

        output = result.stdout.strip()
        if not output:
            return ToolResult(
                tool_name=self.name,
                output=f"No file matches were found for query: {sanitized}",
            )
        return ToolResult(tool_name=self.name, output=output)

    @staticmethod
    def _sanitize_query(query: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\- ./]", " ", query).strip()


@dataclass(slots=True)
class ToolRegistry:
    tools: dict[str, Tool]

    def get(self, name: str) -> Tool:
        try:
            return self.tools[name]
        except KeyError as exc:
            raise ToolError(f"Unknown tool: {name}") from exc

    def list_for_prompt(self) -> list[dict[str, object]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self.tools.values()
        ]
