from __future__ import annotations

import argparse

from jarvis.audio import AudioError, AudioRecorder
from jarvis.config import AppConfig
from jarvis.dialogue import DialogueManager
from jarvis.llm import LLMError, OllamaClient
from jarvis.stt import FasterWhisperTranscriber, SpeechToTextError
from jarvis.tts import EdgeTTSPlayer, TextToSpeechError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Jarvis CLI assistant.")
    parser.add_argument(
        "--mode",
        choices=("text", "voice"),
        default="text",
        help="Choose text mode for debugging or voice mode for microphone interaction.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=0,
        help="Stop after the given number of user turns. Use 0 for an open session.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config = AppConfig()
    dialogue = DialogueManager(system_prompt=config.system_prompt)
    llm = OllamaClient(base_url=config.ollama_url, model=config.ollama_model)
    transcriber = FasterWhisperTranscriber(
        model_name=config.stt_model,
        language=config.language or None,
    )
    speaker = EdgeTTSPlayer(voice=config.tts_voice)
    recorder = AudioRecorder(sample_rate=config.sample_rate, audio_dir=config.audio_dir)

    print("Jarvis is ready.")
    print(f"Mode: {args.mode}")
    print("Type 'exit' to leave the session in text mode.")

    turn_count = 0
    while args.turns == 0 or turn_count < args.turns:
        try:
            user_text = (
                _handle_text_turn()
                if args.mode == "text"
                else _handle_voice_turn(config, recorder, transcriber)
            )
        except (AudioError, SpeechToTextError) as exc:
            print(f"Input error: {exc}")
            continue

        if user_text is None:
            break
        if not user_text:
            continue

        dialogue.append_message("user", user_text)

        try:
            reply = llm.generate_reply(dialogue.build_messages())
        except LLMError as exc:
            print(f"LLM error: {exc}")
            continue

        dialogue.append_message("assistant", reply)
        print(f"Jarvis: {reply}")

        if args.mode == "voice":
            try:
                speaker.speak(reply)
            except TextToSpeechError as exc:
                print(f"TTS error: {exc}")

        turn_count += 1

    print("Session ended.")
    return 0


def _handle_text_turn() -> str | None:
    user_text = input("You: ").strip()
    if user_text.lower() in {"exit", "quit"}:
        return None
    if not user_text:
        print("Please enter a message.")
        return ""
    return user_text


def _handle_voice_turn(
    config: AppConfig,
    recorder: AudioRecorder,
    transcriber: FasterWhisperTranscriber,
) -> str:
    input("Press Enter to start recording.")
    print(f"Recording for {config.record_seconds} seconds...")
    audio_path = recorder.record_audio(config.record_seconds)
    print(f"Saved recording to {audio_path}")
    transcript = transcriber.transcribe(audio_path)
    print(f"You said: {transcript}")
    return transcript
