# AGENTS.md — bark-with-voice-clone

## Project Overview

This is a fork of [Suno's BARK](https://github.com/suno-ai/bark) text-to-speech model with added voice cloning capabilities using HuBERT semantic token quantization. The project allows users to clone voices from short audio samples (5-12 seconds) and generate speech in that cloned voice.

## Project Structure

```
bark-with-voice-clone/
├── bark/                    # Core BARK TTS module (modified from suno-ai/bark)
│   ├── __init__.py          # Exports: generate_audio, SAMPLE_RATE, preload_models
│   ├── api.py               # High-level API: generate_audio(), text_to_semantic()
│   ├── generation.py        # Model loading, text/semantic/coarse/fine generation
│   ├── model.py             # GPT model architecture (base)
│   ├── model_fine.py        # FineGPT model architecture
│   └── assets/prompts/      # Pre-made voice prompts (.npz files)
│
├── hubert/                  # HuBERT voice cloning module (from gitmylo/bark-voice-cloning)
│   ├── __init__.py
│   ├── hubert_manager.py    # Downloads HuBERT models if missing
│   ├── pre_kmeans_hubert.py # CustomHubert model (modified from lucidrains/audiolm-pytorch)
│   └── customtokenizer.py   # CustomTokenizer for semantic token quantization
│
├── utils/                   # Utility modules
│   ├── lora.py              # LoRA adapter support
│   └── bitsandbytes.py      # Quantization utilities
│
├── app_clone_voice/         # Standalone CLI application (independent)
│   ├── voice_clone.py       # CLI: clone + generate commands
│   ├── requirements.txt     # App-specific dependencies
│   ├── bark/                # Local copy of bark module
│   └── hubert/              # Local copy of hubert module
│
├── notebooks/               # Jupyter notebooks for various tasks
├── clone_voice.ipynb        # Voice cloning notebook (source for app_clone_voice)
├── generate.ipynb           # Audio generation notebook
├── generate_chunked.ipynb   # Chunked generation for long text
├── rvc_infer.py             # RVC (Retrieval-based Voice Conversion) inference
├── rvc_test.ipynb           # RVC testing notebook
│
├── data/                    # Model data directory
│   └── models/hubert/       # HuBERT models (downloaded on first run)
│
├── models/                  # Bark model weights (downloaded on first run)
├── output/                  # Generated audio output directory
│
├── pyproject.toml           # Project config (suno-bark package)
├── setup.py                 # Legacy setup script
└── README.md                # Project documentation
```

## Key Architecture

### Voice Cloning Pipeline

1. **Audio Input** → Load reference audio (<13 seconds)
2. **HuBERT** → Extract semantic features from audio waveform
3. **CustomTokenizer** → Quantize features into semantic tokens (10,000 vocab)
4. **EnCodec** → Extract audio codec codes (8 codebooks)
5. **Save** → Store as `.npz` prompt file in `bark/assets/prompts/`

### Text-to-Speech Pipeline

1. **Text** → BERT tokenizer → Semantic token generation (GPT model)
2. **Semantic tokens** → Coarse audio codes (2 codebooks, GPT model)
3. **Coarse codes** → Fine audio codes (8 codebooks, FineGPT model)
4. **Fine codes** → Waveform (EnCodec decoder)
5. **Output** → 24kHz audio array

### Model Architecture

- **GPT models**: Transformer-based autoregressive models for text→semantic, semantic→coarse
- **FineGPT**: Non-causal transformer for coarse→fine refinement
- **EnCodec**: Neural audio codec for audio compression/decompression
- **HuBERT**: Self-supervised speech representation model (modified, no kmeans)

## Key Files to Modify

| Task | Files |
|------|-------|
| Change voice cloning logic | `hubert/pre_kmeans_hubert.py`, `hubert/customtokenizer.py` |
| Modify generation parameters | `bark/generation.py` (lines 44-55 for constants) |
| Add new voice prompts | `bark/assets/prompts/` (save as .npz) |
| Change CLI interface | `app_clone_voice/voice_clone.py` |
| Modify model architecture | `bark/model.py`, `bark/model_fine.py` |
| RVC integration | `rvc_infer.py` |

## Dependencies

### Core (bark)
- `torch`, `torchaudio` — PyTorch framework
- `encodec` — Neural audio codec
- `transformers` — BERT tokenizer
- `huggingface_hub` — Model downloads
- `numpy`, `scipy` — Numerical computation
- `funcy` — Functional utilities
- `tqdm` — Progress bars

### Voice Cloning (hubert)
- `fairseq` — HuBERT model loading
- `einops` — Tensor operations
- `audiolm_pytorch` — Audio utilities (curtail_to_multiple)

### Optional
- `RVC-GUI-pkg/` — RVC for voice conversion (separate clone)

## Conventions

- **Python version**: >=3.8 (per pyproject.toml)
- **Model caching**: `~/.cache/serp/bark_v0/` for Bark models
- **HuBERT models**: `data/models/hubert/` (relative to CWD)
- **Audio sample rate**: 24kHz (Bark output), 16kHz (HuBERT internal)
- **Device handling**: Auto-detect CUDA, fallback to CPU
- **Prompt format**: `.npz` files with `fine_prompt`, `coarse_prompt`, `semantic_prompt` arrays

## Running the App

```bash
# From project root
cd app_clone_voice

# Clone a voice
python voice_clone.py clone --audio ../reference.wav --name my_voice --device auto

# Generate speech
python voice_clone.py generate --text "Hello world" --voice my_voice --output output.wav

# Force CPU
python voice_clone.py generate --text "Hello" --voice my_voice --output out.wav --device cpu
```

## Common Tasks

### Adding a new voice prompt programmatically

```python
from bark.api import generate_audio, save_as_prompt

# Generate and save
full_gen, audio = generate_audio("Hello", output_full=True)
save_as_prompt("bark/assets/prompts/my_voice.npz", full_gen)
```

### Using a cloned voice

```python
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write

preload_models()
audio = generate_audio("Hello!", history_prompt="my_voice")
write("output.wav", SAMPLE_RATE, audio)
```

## Notes

- The `hubert/` module is a modified version from [gitmylo/bark-voice-cloning-HuBERT-quantizer](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer)
- The `bark/` module is modified from [suno-ai/bark](https://github.com/suno-ai/bark) to support voice cloning prompts
- Voice cloning works best with clear, noise-free audio samples of 5-12 seconds
- Generated audio is 24kHz, mono channel
