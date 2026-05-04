from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile


class TextToSpeechError(RuntimeError):
    """Raised when text-to-speech synthesis or playback fails."""


@dataclass(slots=True)
class EdgeTTSPlayer:
    voice: str

    def speak(self, text: str) -> None:
        if not text.strip():
            return

        output_path = Path(tempfile.gettempdir()) / "jarvis-response.mp3"
        asyncio.run(self._synthesize(text, output_path))
        self._play(output_path)

    async def _synthesize(self, text: str, output_path: Path) -> None:
        try:
            import edge_tts
        except ImportError as exc:
            raise TextToSpeechError(
                "Edge TTS is not installed. Install requirements.txt first."
            ) from exc

        try:
            communicate = edge_tts.Communicate(text=text, voice=self.voice)
            await communicate.save(str(output_path))
        except Exception as exc:  # pragma: no cover
            raise TextToSpeechError("Text-to-speech synthesis failed.") from exc

    def _play(self, output_path: Path) -> None:
        player = self._find_player()
        if player is None:
            raise TextToSpeechError(
                "No supported audio player was found. Install ffplay or mpv to hear responses."
            )

        command = [*player, str(output_path)]
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            raise TextToSpeechError("Audio playback failed.") from exc

    @staticmethod
    def _find_player() -> list[str] | None:
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit"]
        if shutil.which("mpv"):
            return ["mpv", "--no-video"]
        if shutil.which("afplay"):
            return ["afplay"]
        return None
