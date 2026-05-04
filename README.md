# ML2 Jarvis

ML2 Jarvis is a minimal Python voice assistant skeleton designed for the "Build Your Own Jarvis" basic solution. It provides a clean starting point for:

- local LLM chat through Ollama,
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
- Ollama installed and running locally for LLM responses
- A local Ollama model, for example `llama3.2:3b` or another small chat model

Optional voice dependencies:
- A working microphone for voice mode
- `ffplay`, `mpv`, or another supported local audio player for Edge TTS playback

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment template:

```bash
cp .env.example .env
```

4. Start Ollama and make sure the configured model is available:

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
- `JARVIS_OLLAMA_URL`
- `JARVIS_OLLAMA_MODEL`
- `JARVIS_STT_MODEL`
- `JARVIS_TTS_VOICE`
- `JARVIS_RECORD_SECONDS`
- `JARVIS_SAMPLE_RATE`
- `JARVIS_LANGUAGE`
- `JARVIS_AUDIO_DIR`

## Notes

- Text mode is the easiest way to verify the LLM and dialogue stack first.
- Voice mode records a short clip, transcribes it, then synthesizes the assistant reply.
- If speech recognition or synthesis dependencies are not installed correctly, the program will report a clear error instead of crashing without context.
