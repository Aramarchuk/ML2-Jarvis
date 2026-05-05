from __future__ import annotations

from dataclasses import dataclass, field


class SpeechToTextError(RuntimeError):
    """Raised when speech transcription fails."""


@dataclass(slots=True)
class FasterWhisperTranscriber:
    model_name: str
    device: str = "cpu"
    compute_type: str = "int8"
    language: str | None = None
    _model: object | None = field(default=None, init=False, repr=False)

    def transcribe(self, audio_path: str) -> str:
        model = self._get_model()
        try:
            segments, _ = model.transcribe(
                audio_path,
                language=self.language,
                vad_filter=True,
            )
        except Exception as exc:  # pragma: no cover
            raise SpeechToTextError("Speech transcription failed.") from exc

        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise SpeechToTextError("No speech was detected in the recorded audio.")

        return text

    def _get_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise SpeechToTextError(
                    "Faster Whisper is not installed. Install requirements.txt first."
                ) from exc

            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )

        return self._model
