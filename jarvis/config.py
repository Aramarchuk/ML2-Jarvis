from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class AppConfig:
    system_prompt: str = os.getenv(
        "JARVIS_SYSTEM_PROMPT",
        "You are Jarvis, a concise and helpful voice assistant.",
    )
    llm_base_url: str = os.getenv(
        "JARVIS_LLM_BASE_URL",
        "https://hub.nhr.fau.de/api/llmgw/v1",
    )
    llm_api_key: str = os.getenv("JARVIS_LLM_API_KEY", "")
    assistant_model: str = os.getenv(
        "JARVIS_ASSISTANT_MODEL",
        "Qwen/Qwen3.5-35B-A3B-FP8",
    )
    router_model: str = os.getenv(
        "JARVIS_ROUTER_MODEL",
        "IBM/granite-4.0-micro",
    )
    llm_timeout_seconds: int = int(os.getenv("JARVIS_LLM_TIMEOUT_SECONDS", "120"))
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
