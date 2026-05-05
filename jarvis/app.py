from __future__ import annotations

import argparse
from pathlib import Path

from jarvis.audio import AudioError, AudioRecorder
from jarvis.config import AppConfig
from jarvis.dialogue import DialogueManager
from jarvis.llm import ChatClient, LLMError, OllamaClient, OpenAICompatibleClient
from jarvis.router import LLMRouter, RouterError
from jarvis.session_memory import SessionMemory
from jarvis.stt import FasterWhisperTranscriber, SpeechToTextError
from jarvis.tools import (
    CalculatorTool,
    FileSearchTool,
    SystemInfoTool,
    TimeTool,
    ToolError,
    ToolRegistry,
)
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
    llm = _build_chat_client(config=config, for_router=False)
    router_llm = _build_chat_client(config=config, for_router=True)
    router = LLMRouter(
        llm_client=router_llm,
        confidence_threshold=config.router_confidence_threshold,
    )
    session_memory = SessionMemory(
        summary_interval=config.short_term_summary_interval,
        recent_turn_limit=config.short_term_recent_turns,
    )
    transcriber = FasterWhisperTranscriber(
        model_name=config.stt_model,
        device=config.stt_device,
        compute_type=config.stt_compute_type,
        language=config.language or None,
    )
    speaker = EdgeTTSPlayer(voice=config.tts_voice)
    recorder = AudioRecorder(sample_rate=config.sample_rate, audio_dir=config.audio_dir)
    tools = ToolRegistry(
        tools={
            "time": TimeTool(),
            "calculator": CalculatorTool(),
            "system_info": SystemInfoTool(config=config, mode=args.mode),
            "file_search": FileSearchTool(repo_root=Path.cwd()),
        }
    )

    print("Jarvis is ready.")
    print(f"Mode: {args.mode}")
    print(f"LLM backend: {config.llm_backend}")
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
        session_context = session_memory.build_context_block()
        tool_output = ""

        try:
            route = router.decide(
                user_text=user_text,
                session_context=session_context,
                tool_catalog=tools.list_for_prompt(),
            )
        except RouterError as exc:
            print(f"Router warning: {exc}")
            route = None

        if route and route.route == "tool":
            try:
                tool = tools.get(route.tool_name or "")
                tool_result = tool.run(route.arguments)
                tool_output = tool_result.output
                print(f"Tool [{tool_result.tool_name}] was used.")
            except ToolError as exc:
                tool_output = f"Tool error: {exc}"
                print(tool_output)

        try:
            reply = llm.generate_reply(
                dialogue.build_messages_with_context(
                    session_context=session_context,
                    tool_result=tool_output,
                )
            )
        except LLMError as exc:
            print(f"LLM error: {exc}")
            continue

        dialogue.append_message("assistant", reply)
        session_memory.update(user_text=user_text, assistant_text=reply)
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


def _build_chat_client(config: AppConfig, for_router: bool) -> ChatClient:
    if config.llm_backend == "ollama":
        return OllamaClient(
            base_url=config.ollama_url,
            model=config.router_ollama_model if for_router else config.ollama_model,
            timeout_seconds=(
                config.router_timeout_seconds
                if for_router
                else config.ollama_timeout_seconds
            ),
        )

    return OpenAICompatibleClient(
        base_url=config.llm_base_url.rstrip("/"),
        api_key=config.llm_api_key,
        model=config.router_llm_model if for_router else config.llm_model,
        timeout_seconds=(
            config.router_timeout_seconds
            if for_router
            else config.ollama_timeout_seconds
        ),
    )
