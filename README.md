# ML2 Jarvis

ML2 Jarvis is a minimal Python voice assistant skeleton designed for the "Build Your Own Jarvis" basic solution. It provides a clean starting point for:

- local or external LLM chat,
- in-memory dialogue history,
- speech-to-text with Faster Whisper,
- text-to-speech with Edge TTS,
- microphone recording for voice turns.

## Features

- Text mode for quick debugging without microphone or TTS requirements
- Voice mode for the full `voice -> text -> LLM -> voice` flow
- Modular code layout that is ready for memory, tools, actions, and planning extensions
- English-only comments, documentation, prompts, and user-facing messages

## Project Layout

```text
.
├── jarvis
│   ├── app.py
│   ├── audio.py
│   ├── config.py
│   ├── dialogue.py
│   ├── llm.py
│   ├── stt.py
│   └── tts.py
├── tests
│   └── test_dialogue.py
├── .env.example
├── main.py
└── requirements.txt
```

## Requirements

- Python 3.12+
- Either an OpenAI-compatible API endpoint with an API key, or a local Ollama setup

Optional voice dependencies:
- A working microphone for voice mode
- PortAudio installed on the system for `sounddevice`
- `ffplay`, `mpv`, or another supported local audio player for Edge TTS playback

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

If voice mode fails with `PortAudio library not found`, install the system package first.
Examples:

```bash
sudo apt install portaudio19-dev
```

or on Fedora:

```bash
sudo dnf install portaudio-devel
```

3. Copy the environment template:

```bash
cp .env.example .env
```

4. If you use Ollama, start it and make sure the configured model is available:

```bash
ollama serve
ollama pull llama3.2:3b
```

## Usage

Text mode:

```bash
python main.py --mode text
```

Voice mode:

```bash
python main.py --mode voice
```

Show configuration help:

```bash
python main.py --help
```

## Environment Variables

The application reads configuration from `.env` or the process environment:

- `JARVIS_SYSTEM_PROMPT`
- `JARVIS_LLM_BACKEND`
- `JARVIS_LLM_BASE_URL`
- `JARVIS_LLM_API_KEY`
- `JARVIS_LLM_MODEL`
- `JARVIS_ROUTER_LLM_MODEL`
- `JARVIS_OLLAMA_URL`
- `JARVIS_OLLAMA_MODEL`
- `JARVIS_ROUTER_OLLAMA_MODEL`
- `JARVIS_OLLAMA_TIMEOUT_SECONDS`
- `JARVIS_ROUTER_TIMEOUT_SECONDS`
- `JARVIS_STT_MODEL`
- `JARVIS_STT_DEVICE`
- `JARVIS_STT_COMPUTE_TYPE`
- `JARVIS_TTS_VOICE`
- `JARVIS_RECORD_SECONDS`
- `JARVIS_SAMPLE_RATE`
- `JARVIS_LANGUAGE`
- `JARVIS_AUDIO_DIR`
- `JARVIS_ROUTER_CONFIDENCE_THRESHOLD`
- `JARVIS_SHORT_TERM_SUMMARY_INTERVAL`
- `JARVIS_SHORT_TERM_RECENT_TURNS`

## Notes

- Text mode is the easiest way to verify the LLM and dialogue stack first.
- Voice mode records a short clip, transcribes it, then synthesizes the assistant reply.
- The router can use a different model than the main assistant.
- The default external setup uses `Qwen/Qwen3.5-35B-A3B-FP8` for final responses and `IBM/granite-4.0-micro` for routing.
- STT now defaults to CPU execution with `JARVIS_STT_DEVICE=cpu` and `JARVIS_STT_COMPUTE_TYPE=int8` to avoid CUDA runtime issues on machines without a working GPU stack.
- If speech recognition or synthesis dependencies are not installed correctly, the program will report a clear error instead of crashing without context.
