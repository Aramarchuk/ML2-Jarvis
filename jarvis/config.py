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
    ollama_url: str = os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("JARVIS_OLLAMA_MODEL", "llama3.2:3b")
    router_ollama_model: str = os.getenv("JARVIS_ROUTER_OLLAMA_MODEL", "tinyllama")
    ollama_timeout_seconds: int = int(os.getenv("JARVIS_OLLAMA_TIMEOUT_SECONDS", "120"))
    router_timeout_seconds: int = int(os.getenv("JARVIS_ROUTER_TIMEOUT_SECONDS", "30"))
    stt_model: str = os.getenv("JARVIS_STT_MODEL", "base")
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
