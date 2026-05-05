from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


class AudioError(RuntimeError):
    """Raised when microphone recording fails."""


@dataclass(slots=True)
class AudioRecorder:
    sample_rate: int
    audio_dir: Path

    def record_audio(self, seconds: int) -> str:
        try:
            import sounddevice as sd
            import soundfile as sf
        except ImportError as exc:
            raise AudioError(
                "Voice mode dependencies are missing. Install requirements.txt first."
            ) from exc
        except OSError as exc:
            raise AudioError(
                "PortAudio is not available on this system. Install the PortAudio runtime "
                "or development package before using voice mode."
            ) from exc

        self.audio_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.audio_dir / f"recording-{self._timestamp()}.wav"

        try:
            recording = sd.rec(
                int(seconds * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            sf.write(output_path, recording, self.sample_rate)
        except Exception as exc:  # pragma: no cover
            raise AudioError("Microphone recording failed.") from exc

        return str(output_path)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
