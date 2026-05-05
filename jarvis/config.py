from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re


def _read_local_env_text() -> str:
    env_path = Path(".env")
    if not env_path.exists():
        return ""
    return env_path.read_text(encoding="utf-8")


def _load_simple_env_file() -> None:
    for line in _read_local_env_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not re.fullmatch(r"[A-Z0-9_]+", key):
            continue
        if key in os.environ:
            continue

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        ):
            value = value[1:-1]

        os.environ[key] = value


_load_simple_env_file()


def _extract_legacy_assignment(name: str, default: str = "") -> str:
    text = _read_local_env_text()
    pattern = rf'^\s*{re.escape(name)}\s*=\s*"([^"]+)"\s*$'
    match = re.search(pattern, text, flags=re.MULTILINE)
    if match:
        return match.group(1)
    return default


@dataclass(slots=True)
class AppConfig:
    system_prompt: str = os.getenv(
        "JARVIS_SYSTEM_PROMPT",
        "You are Jarvis, a concise and helpful voice assistant.",
    )
    llm_backend: str = os.getenv("JARVIS_LLM_BACKEND", "openai_compatible")
    llm_base_url: str = os.getenv(
        "JARVIS_LLM_BASE_URL",
        _extract_legacy_assignment("base_url", "https://hub.nhr.fau.de/api/llmgw/v1"),
    )
    llm_api_key: str = os.getenv(
        "JARVIS_LLM_API_KEY",
        _extract_legacy_assignment("API_KEY", ""),
    )
    assistant_model: str = os.getenv(
        "JARVIS_ASSISTANT_MODEL",
        os.getenv("JARVIS_LLM_MODEL", "Qwen/Qwen3.5-35B-A3B-FP8"),
    )
    router_model: str = os.getenv(
        "JARVIS_ROUTER_MODEL",
        os.getenv(
            "JARVIS_ROUTER_LLM_MODEL",
            os.getenv("JARVIS_ROUTER_OLLAMA_MODEL", "IBM/granite-4.0-micro"),
        ),
    )
    ollama_url: str = os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_timeout_seconds: int = int(os.getenv("JARVIS_OLLAMA_TIMEOUT_SECONDS", "120"))
    router_timeout_seconds: int = int(os.getenv("JARVIS_ROUTER_TIMEOUT_SECONDS", "30"))
    stt_model: str = os.getenv("JARVIS_STT_MODEL", "base")
    stt_device: str = os.getenv("JARVIS_STT_DEVICE", "cpu")
    stt_compute_type: str = os.getenv("JARVIS_STT_COMPUTE_TYPE", "int8")
    tts_voice: str = os.getenv("JARVIS_TTS_VOICE", "en-US-AriaNeural")
    record_seconds: int = int(os.getenv("JARVIS_RECORD_SECONDS", "5"))
    sample_rate: int = int(os.getenv("JARVIS_SAMPLE_RATE", "16000"))
    language: str = os.getenv("JARVIS_LANGUAGE", "en")
    audio_dir: Path = Path(os.getenv("JARVIS_AUDIO_DIR", ".jarvis_audio"))
    router_confidence_threshold: float = float(
        os.getenv("JARVIS_ROUTER_CONFIDENCE_THRESHOLD", "0.75")
    )
    short_term_summary_interval: int = int(
        os.getenv("JARVIS_SHORT_TERM_SUMMARY_INTERVAL", "4")
    )
    short_term_recent_turns: int = int(os.getenv("JARVIS_SHORT_TERM_RECENT_TURNS", "4"))

    # Legacy aliases kept for backward compatibility with older local configs.
    llm_model: str = os.getenv(
        "JARVIS_LLM_MODEL",
        os.getenv("JARVIS_ASSISTANT_MODEL", "Qwen/Qwen3.5-35B-A3B-FP8"),
    )
    router_llm_model: str = os.getenv(
        "JARVIS_ROUTER_LLM_MODEL",
        os.getenv("JARVIS_ROUTER_MODEL", "IBM/granite-4.0-micro"),
    )
    ollama_model: str = os.getenv(
        "JARVIS_OLLAMA_MODEL",
        os.getenv("JARVIS_ASSISTANT_MODEL", "llama3.2:3b"),
    )
    router_ollama_model: str = os.getenv(
        "JARVIS_ROUTER_OLLAMA_MODEL",
        os.getenv("JARVIS_ROUTER_MODEL", "tinyllama"),
    )
