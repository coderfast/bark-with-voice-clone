# AGENTS.md — app_clone_voice

## Overview

Standalone CLI application for voice cloning from audio samples. Extracts voice features and saves them as `.npz` prompts compatible with Bark TTS.

**Cross-platform**: Works on Windows, Linux, and macOS (including Apple Silicon via MPS).

## Structure

```
app_clone_voice/
├── voice_clone.py       # Main CLI script
├── requirements.txt     # pip dependencies
├── bark/                # Local copy of bark TTS module
│   ├── __init__.py
│   ├── api.py           # generate_audio(), save_as_prompt()
│   ├── generation.py    # Model loading, generation functions
│   ├── model.py         # GPT architecture
│   ├── model_fine.py    # FineGPT architecture
│   └── assets/prompts/  # Voice prompts (.npz)
└── hubert/              # Local copy of HuBERT voice cloning module
    ├── __init__.py
    ├── hubert_manager.py    # Downloads HuBERT models (via HuggingFace)
    ├── pre_kmeans_hubert.py # CustomHubert model (uses transformers, not fairseq)
    └── customtokenizer.py   # Semantic token quantizer
```

## How It Works

1. Load reference audio (<13 seconds)
2. Resample to 16kHz for HuBERT
3. Extract semantic features via HuBERT (768 dimensions)
4. Quantize to tokens via CustomTokenizer (10,000 vocab)
5. Extract audio codes via EnCodec (8 codebooks)
6. Save as `.npz` in `bark/assets/prompts/`

## CLI Usage

```bash
# Clone a voice (auto-detect from source_voice_input/)
python voice_clone.py --name my_voice

# Clone from specific audio file
python voice_clone.py --audio reference.wav --name my_voice

# Overwrite existing voice
python voice_clone.py --audio reference.wav --name my_voice --force

# Device options (auto/cuda/cpu/mps)
python voice_clone.py --audio ref.wav --name voice --device mps  # Apple Silicon

# Verbose output (timing info)
python voice_clone.py --verbose --audio ref.wav --name voice

# List available voices
python voice_clone.py --list

# Show voice info
python voice_clone.py --info en_speaker_0

# Device info
python voice_clone.py --device-info

# Version
python voice_clone.py --version
```

## Key Files to Modify

| Task | File |
|------|------|
| Change CLI arguments | `voice_clone.py` (argparse section) |
| Modify cloning logic | `hubert/pre_kmeans_hubert.py`, `hubert/customtokenizer.py` |
| Change generation defaults | `bark/generation.py` (lines 44-55) |
| Add voice prompts | `bark/assets/prompts/` (save as .npz) |
| Change model architecture | `bark/model.py`, `bark/model_fine.py` |

## Dependencies

From `requirements.txt`:
```
torch, torchaudio, encodec, transformers,
einops, scipy, numpy, huggingface_hub, tqdm, soundfile
```

No `fairseq` required — HuBERT is loaded via `transformers`.
`soundfile` is used for audio loading/info (replaces `torchaudio` which dropped these APIs in 2.11+).

## Paths and Caching

- **HuBERT models**: `data/models/hubert/` (relative to CWD, not this directory)
- **EnCodec models**: `~/.cache/serp/bark_v0/` (user cache)
- **Voice prompts**: `bark/assets/prompts/` (relative to this directory)

## Error Handling

- Audio validation: duration < 13s, sample rate >= 8kHz
- Voice name validation: alphanumeric, underscore, hyphen only
- `--force` flag to overwrite existing voices
- `--verbose` flag shows full tracebacks on error

## Notes

- `sys.path` is modified to import local `bark/` and `hubert/` from this directory
- This app does NOT depend on the parent project's modules
- Models are downloaded on first run if not present
- Best results with clear, noise-free reference audio (5-13 seconds)
