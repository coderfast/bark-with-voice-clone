# AGENTS.md — bark-with-voice-clone

## Project Overview

This is a fork of [Suno's BARK](https://github.com/suno-ai/bark) text-to-speech model with added voice cloning capabilities using HuBERT semantic token quantization. The project allows users to clone voices from short audio samples (5-12 seconds), generate speech in that cloned voice, fine-tune models on custom datasets, and optionally apply RVC (Retrieval-based Voice Conversion) post-processing.

## Project Structure

```
bark-with-voice-clone/
├── bark/                        # Core BARK TTS module (modified from suno-ai/bark)
│   ├── __init__.py              # Exports: generate_audio, SAMPLE_RATE, preload_models, text_to_semantic, semantic_to_waveform, save_as_prompt
│   ├── api.py                   # High-level API: generate_audio(), text_to_semantic(), semantic_to_waveform(), save_as_prompt()
│   ├── generation.py            # Model loading, text/semantic/coarse/fine generation (885 lines)
│   ├── model.py                 # GPT model architecture (CausalSelfAttention, based on NanoGPT)
│   ├── model_fine.py            # FineGPT model architecture (NonCausalSelfAttention)
│   └── assets/prompts/          # Pre-made voice prompts (.npz files, 140+ voices)
│
├── hubert/                      # HuBERT voice cloning module (from gitmylo/bark-voice-cloning)
│   ├── __init__.py
│   ├── hubert_manager.py        # Downloads HuBERT models if missing
│   ├── pre_kmeans_hubert.py     # CustomHubert model (modified from lucidrains/audiolm-pytorch)
│   └── customtokenizer.py       # CustomTokenizer for semantic token quantization (10,000 vocab)
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── lora.py                  # LoRA adapter support (convert_linear_layer_to_lora, etc.)
│   └── bitsandbytes.py          # Quantization utilities (BitsAndBytesConfig, etc.)
│
├── app_clone_voice/             # Standalone CLI application (independent, not reviewed here)
│   ├── voice_clone.py           # CLI: clone + generate commands
│   ├── requirements.txt         # App-specific dependencies
│   ├── bark/                    # Local copy of bark module
│   └── hubert/                  # Local copy of hubert module
│
├── notebooks/                   # Jupyter notebooks
│   └── fake_classifier.ipynb    # Audio deepfake detection classifier
│
├── clone_voice.ipynb            # Voice cloning + generation notebook
├── generate.ipynb               # Audio generation with RVC support
├── generate_chunked.ipynb       # Chunked generation for long text with RVC
├── test_models.ipynb            # Test fine-tuned models with RVC
├── rvc_test.ipynb               # RVC inference testing
├── train_semantic.ipynb         # Fine-tune semantic (text→semantic) model
├── train_coarse.ipynb           # Fine-tune coarse (semantic→coarse) model
├── train_fine.ipynb             # Fine-tune fine (coarse→fine) model
├── rvc_infer.py                 # RVC (Retrieval-based Voice Conversion) inference
│
├── datasets/                    # Training datasets directory
│   └── .tmp                     # Temporary files
│
├── data/                        # Model data directory
│   └── models/hubert/           # HuBERT models (downloaded on first run)
│       ├── hubert.pt            # HuBERT base model
│       └── tokenizer.pth        # Custom tokenizer
│
├── models/                      # Bark model weights (downloaded on first run)
│   └── pytorch_model.bin        # Model checkpoint
│
├── semantic_output/             # Fine-tuned semantic model output
├── coarse_output/               # Fine-tuned coarse model output
├── fine_output/                 # Fine-tuned fine model output
├── output/                      # Generated audio output directory
│
├── __hugginface_downloads/      # HuggingFace model cache
├── build/                       # Build artifacts (setuptools)
├── suno_bark.egg-info/          # Package metadata
│
├── hubert_base.pt               # RVC HuBERT model (for rvc_infer.py)
├── RVC-GUI-pkg/                 # RVC package (empty)
│
├── pyproject.toml               # Project config (suno-bark package)
├── setup.py                     # Legacy setup script
├── LICENSE.md                   # MIT License
├── README.md                    # Project documentation
├── model-card.md                # Model card with architecture details
├── FUNDING.yml                  # GitHub sponsors (serp-ai)
└── .gitignore                   # Git ignore rules
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

### Fine-tuning Pipeline

The project supports fine-tuning all three model stages using LoRA and quantization:

1. **Dataset Prep** → Use HuBERT + EnCodec to extract semantic/coarse/fine tokens from audio
2. **Semantic Training** (`train_semantic.ipynb`) → Fine-tune text→semantic model
3. **Coarse Training** (`train_coarse.ipynb`) → Fine-tune semantic→coarse model
4. **Fine Training** (`train_fine.ipynb`) → Fine-tune coarse→fine model

### RVC Post-processing Pipeline

Optional RVC step after Bark generation for voice conversion:
1. **Bark Output** → Generate audio with Bark
2. **RVC** → Apply Retrieval-based Voice Conversion for pitch/timbre adjustment
3. **Output** → Final audio with target voice characteristics

### Model Architecture

| Model | Parameters | Attention | Output Vocab | Purpose |
|-------|-----------|-----------|--------------|---------|
| GPT (text) | 80M | Causal | 10,000 | Text → Semantic tokens |
| GPT (coarse) | 80M | Causal | 2×1,024 | Semantic → Coarse codes |
| FineGPT | 80M | Non-causal | 6×1,024 | Coarse → Fine codes |

- **EnCodec**: Neural audio codec for audio compression/decompression (24kHz, 8 codebooks)
- **HuBERT**: Self-supervised speech representation model (modified, no kmeans)
- **BERT tokenizer**: `bert-base-multilingual-cased` for text encoding

## Key Files to Modify

| Task | Files |
|------|-------|
| Change voice cloning logic | `hubert/pre_kmeans_hubert.py`, `hubert/customtokenizer.py` |
| Modify generation parameters | `bark/generation.py` (lines 44-55 for constants) |
| Add new voice prompts | `bark/assets/prompts/` (save as .npz) |
| Change CLI interface | `app_clone_voice/voice_clone.py` |
| Modify model architecture | `bark/model.py`, `bark/model_fine.py` |
| RVC integration | `rvc_infer.py` |
| Fine-tune semantic model | `train_semantic.ipynb` |
| Fine-tune coarse model | `train_coarse.ipynb` |
| Fine-tune fine model | `train_fine.ipynb` |
| Chunked long-text generation | `generate_chunked.ipynb` |

## Dependencies

### Core (bark)
- `torch`, `torchaudio` — PyTorch framework
- `encodec` — Neural audio codec
- `transformers` — BERT tokenizer
- `huggingface_hub` — Model downloads
- `numpy`, `scipy` — Numerical computation
- `funcy` — Functional utilities
- `tqdm` — Progress bars
- `boto3` — AWS S3 access (for model downloads)
- `tokenizers` — Fast tokenizers

### Voice Cloning (hubert)
- `fairseq` — HuBERT model loading
- `einops` — Tensor operations
- `audiolm_pytorch` — Audio utilities (curtail_to_multiple)

### Training (notebooks)
- `accelerate` — Distributed training, mixed precision
- `diffusers` — Learning rate schedulers
- `packaging` — Version parsing
- `wandb` — Experiment logging (optional)
- `bitsandbytes` — 4-bit/8-bit quantization (optional)
- `lora` — LoRA adapter support (via `utils/lora.py`)

### Optional
- `RVC-GUI-pkg/` — RVC for voice conversion (separate clone)
- `ffmpeg-python` — Audio loading for RVC (via `rvc_infer.py`)

## Conventions

- **Python version**: >=3.8 (per pyproject.toml)
- **Model caching**: `~/.cache/serp/bark_v0/` for Bark models
- **HuBERT models**: `data/models/hubert/` (relative to CWD)
- **Audio sample rate**: 24kHz (Bark output), 16kHz (HuBERT internal)
- **Device handling**: Auto-detect CUDA, fallback to CPU
- **Prompt format**: `.npz` files with `fine_prompt`, `coarse_prompt`, `semantic_prompt` arrays
- **Training format**: `.npz` files with `fine`, `coarse`, `semantic` arrays (different from prompts)
- **Dataset format**: `train.txt`/`valid.txt` with `path|text` lines, tokens in `tokens/` subdirectory

## Running the App

### Python API (recommended)

```python
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write

preload_models()
audio = generate_audio("Hello!", history_prompt="en_speaker_0")
write("output.wav", SAMPLE_RATE, audio)
```

### Jupyter Notebooks

```bash
# Voice cloning
jupyter notebook clone_voice.ipynb

# Generation with RVC
jupyter notebook generate.ipynb

# Long text generation
jupyter notebook generate_chunked.ipynb

# Fine-tuning
jupyter notebook train_semantic.ipynb
jupyter notebook train_coarse.ipynb
jupyter notebook train_fine.ipynb
```

### CLI (app_clone_voice)

```bash
cd app_clone_voice
python voice_clone.py clone --audio ../reference.wav --name my_voice --device auto
python voice_clone.py generate --text "Hello world" --voice my_voice --output output.wav
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

### Fine-tuning on a custom dataset

1. Prepare dataset with `train.txt` and `valid.txt` (format: `path|text`)
2. Run `train_semantic.ipynb` to extract tokens and train semantic model
3. Run `train_coarse.ipynb` to train coarse model
4. Run `train_fine.ipynb` to train fine model
5. Use fine-tuned models in `generate.ipynb` by setting paths

### Using RVC post-processing

```python
from rvc_infer import get_vc, vc_single

get_vc("path/to/model.pth", "cuda:0", True)
audio = vc_single(0, "input.wav", f0_up_key=-6, ...)
```

## Voice Prompts

The `bark/assets/prompts/` directory contains 140+ pre-made voice prompts:
- **Multi-language**: `en_*`, `de_*`, `es_*`, `fr_*`, `hi_*`, `it_*`, `ja_*`, `ko_*`, `pl_*`, `pt_*`, `ru_*`, `tr_*`, `zh_*`
- **Custom**: `mi_voz.npz` (user-created voice)
- **Special**: `announcer.npz`, `speaker_*.npz`

## Notes

- The `hubert/` module is a modified version from [gitmylo/bark-voice-cloning-HuBERT-quantizer](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer)
- The `bark/` module is modified from [suno-ai/bark](https://github.com/suno-ai/bark) to support voice cloning prompts
- Voice cloning works best with clear, noise-free audio samples of 5-12 seconds
- Generated audio is 24kHz, mono channel
- Training notebooks support LoRA fine-tuning with optional 4-bit/8-bit quantization
- RVC integration requires the [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) repository
- The project uses `wandb` for experiment tracking during training (optional)
- Fine-tuned model outputs are saved to `semantic_output/`, `coarse_output/`, `fine_output/` directories
