# ML2 Jarvis

ML2 Jarvis is a minimal Python voice assistant skeleton designed for the "Build Your Own Jarvis" basic solution. It provides a clean starting point for:

- external LLM chat through `https://hub.nhr.fau.de/api/llmgw/v1`,
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
- Access to `https://hub.nhr.fau.de/api/llmgw/v1` with a private API key

For the configured external endpoint at `https://hub.nhr.fau.de/api/llmgw/v1`, access requires a private API key.
Contact the project owner directly to obtain that key. Do not commit or publish it.

Optional voice dependencies:
- A working microphone for voice mode
- PortAudio installed on the system for `sounddevice`
- `ffplay`, `mpv`, or another supported local audio player for Edge TTS playback
- `ripgrep` for faster file-search tool execution

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

If you want the `file_search` tool to use `ripgrep` instead of the built-in Python fallback, install it as a system package.
Examples:

```bash
sudo apt install ripgrep
```

or on Fedora:

```bash
sudo dnf install ripgrep
```

3. Copy the environment template:

```bash
cp .env.example .env
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
- `JARVIS_LLM_BASE_URL`
- `JARVIS_LLM_API_KEY`
- `JARVIS_ASSISTANT_MODEL`
- `JARVIS_ROUTER_MODEL`
- `JARVIS_LLM_TIMEOUT_SECONDS`
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

## Task Coverage

Implemented from `task.md`:

- `Understanding Language Models Integration`
  - external LLM integration through `https://hub.nhr.fau.de/api/llmgw/v1`
  - separate assistant and router models

- `Handling Dialogue`
  - multi-turn dialogue history
  - short-term session context injection

- `Voice Recognition Integration`
  - microphone recording
  - speech-to-text with Faster Whisper

- `Voice Generation Integration`
  - speech synthesis with Edge TTS

- `Add Short-term Memory`
  - rolling session summary
  - active facts, recent topics, and open-loop tracking

- `Add Routing and Tools`
  - LLM-based router
  - built-in tools: `time`, `calculator`, `system_info`, `file_search`

## Notes

- Text mode is the easiest way to verify the LLM and dialogue stack first.
- Voice mode records a short clip, transcribes it, then synthesizes the assistant reply.
- The assistant and router each use one model setting:
  - `JARVIS_ASSISTANT_MODEL`
  - `JARVIS_ROUTER_MODEL`
- The default external setup uses `Qwen/Qwen3.5-35B-A3B-FP8` for final responses and `IBM/granite-4.0-micro` for routing.
- If you need access to the external endpoint, ask the project owner for the private API key.
- STT now defaults to CPU execution with `JARVIS_STT_DEVICE=cpu` and `JARVIS_STT_COMPUTE_TYPE=int8` to avoid CUDA runtime issues on machines without a working GPU stack.
- If speech recognition or synthesis dependencies are not installed correctly, the program will report a clear error instead of crashing without context.
