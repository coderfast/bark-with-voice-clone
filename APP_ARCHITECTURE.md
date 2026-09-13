# APP_ARCHITECTURE.md — bark-with-voice-clone

## Project Overview

This is a fork of [Suno's BARK](https://github.com/suno-ai/bark) text-to-speech model with added voice cloning capabilities using HuBERT semantic token quantization. The project allows users to clone voices from short audio samples (5-12 seconds), generate speech in that cloned voice, fine-tune models on custom datasets, and optionally apply RVC (Retrieval-based Voice Conversion) post-processing.

## Project Structure

```
bark-with-voice-clone/
├── bark/                        # Core BARK TTS module (modified from suno-ai/bark)
│   ├── __init__.py              # Exports: generate_audio, SAMPLE_RATE, preload_models
│   ├── api.py                   # High-level API with audio format options
│   ├── generation.py            # Model loading, text/semantic/coarse/fine generation
│   ├── model.py                 # GPT model architecture (CausalSelfAttention)
│   ├── model_fine.py            # FineGPT model architecture (NonCausalSelfAttention)
│   └── assets/prompts/          # Pre-made voice prompts (.npz files, 140+ voices)
│
├── hubert/                      # HuBERT voice cloning module
│   ├── __init__.py
│   ├── hubert_manager.py        # Downloads HuBERT models with verification
│   ├── pre_kmeans_hubert.py     # CustomHubert model
│   └── customtokenizer.py       # CustomTokenizer for semantic token quantization
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── lora.py                  # LoRA adapter support
│   ├── bitsandbytes.py          # Quantization utilities
│   ├── training.py              # Shared training utilities for notebooks
│   ├── generation.py            # Shared generation utilities
│   └── rvc_manager.py           # RVC automatic download manager
│
├── bark_cli.py                  # Command Line Interface for audio generation
├── bark_gui.py                  # Graphical User Interface for Bark
│
├── app_voice_filter/            # Voice filter application
│   ├── voice_filter.py          # Audio processing GUI (20+ effects)
│   ├── requirements.txt         # Dependencies
│   └── APP_ARCHITECTURE.md      # This file
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
├── rvc_infer.py                 # RVC inference with auto-download
│
├── data/models/hubert/          # HuBERT models (downloaded on first run)
│
├── semantic_output/             # Fine-tuned semantic model output
├── coarse_output/               # Fine-tuned coarse model output
├── fine_output/                 # Fine-tuned fine model output
├── output/                      # Generated audio output directory
│
├── pyproject.toml               # Project config (suno-bark package)
├── LICENSE.md                   # MIT License
├── README.md                    # Project documentation
├── QUICKUSAGE.md                # Quick usage guide with CLI examples
├── AUDIO_AND_FINETUNING.md      # Audio and fine-tuning guide
├── AUDIO_AND_RVC.md             # RVC usage guide
├── APP_ARCHITECTURE.md          # This file
└── APP_TECHNICALSTACK.md        # Technical stack documentation
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
5. **Output** → 24kHz audio (resampleable to 11025, 22050, 44100 Hz)

### Model Loading Priority

Models are loaded in this order:
1. Custom path (if provided via `text_model_path`, etc.)
2. Local output directories (`semantic_output/`, `coarse_output/`, `fine_output/`)
3. CACHE_DIR (`~/.cache/serp/bark_v0/`) - downloads if not found

### Model Architecture

| Model | Parameters | Attention | Output Vocab | Purpose |
|-------|-----------|-----------|--------------|---------|
| GPT (text) | 80M | Causal | 10,000 | Text → Semantic tokens |
| GPT (coarse) | 80M | Causal | 2×1,024 | Semantic → Coarse codes |
| FineGPT | 80M | Non-causal | 6×1,024 | Coarse → Fine codes |

## Applications

### 1. Bark CLI (`bark_cli.py`)

Command line interface for audio generation.

```bash
python bark_cli.py generate "Hello world" -o output.wav
python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o hola.wav
python bark_cli.py clone --audio reference.wav --name my_voice
python bark_cli.py voices
```

### 2. Bark GUI (`bark_gui.py`)

Graphical user interface for Bark text-to-speech.

Features:
- Text input for generation
- Voice selection (130+ voices)
- Audio format options
- Generate, Play, Stop buttons
- Log area with progress

### 3. Voice Filter (`app_voice_filter/voice_filter.py`)

Audio processing application with 20+ effects.

Features:
- Load WAV, MP3, AAC, OGG, FLAC, M4A
- Volume, Pitch, Speed adjustment
- 5-band Equalizer
- Modulation effects (Chorus, Flanger, Phaser, Tremolo, Vibrato)
- Distortion effects (Soft clip, Bitcrusher, Overdrive)
- Time-based effects (Reverb, Delay)
- Dynamics processing (Compression, Gate)
- Utility functions (Fade, Normalize, Trim, Reverse)
- Auto-preview mode
- Color-coded UI

## Key Files to Modify

| Task | Files |
|------|-------|
| Change voice cloning logic | `hubert/pre_kmeans_hubert.py`, `hubert/customtokenizer.py` |
| Modify generation parameters | `bark/generation.py` |
| Add new voice prompts | `bark/assets/prompts/` (save as .npz) |
| CLI interface | `bark_cli.py` |
| Bark GUI | `bark_gui.py` |
| Voice filter effects | `app_voice_filter/voice_filter.py` |
| Modify model architecture | `bark/model.py`, `bark/model_fine.py` |
| RVC integration | `rvc_infer.py`, `utils/rvc_manager.py` |
| Fine-tuning | `train_semantic.ipynb`, `train_coarse.ipynb`, `train_fine.ipynb` |
| Shared training utilities | `utils/training.py` |
| Shared generation utilities | `utils/generation.py` |

## Dependencies

### Core
- `torch`, `torchaudio` — PyTorch framework
- `encodec` — Neural audio codec
- `transformers` — BERT tokenizer
- `huggingface_hub` — Model downloads
- `numpy`, `scipy` — Numerical computation
- `funcy` — Functional utilities
- `tqdm` — Progress bars
- `boto3` — AWS S3 access
- `tokenizers` — Fast tokenizers

### Voice Cloning (hubert)
- `fairseq` — HuBERT model loading
- `einops` — Tensor operations
- `audiolm_pytorch` — Audio utilities

### Training (notebooks)
- `accelerate` — Distributed training, mixed precision
- `diffusers` — Learning rate schedulers
- `packaging` — Version parsing
- `wandb` — Experiment logging (optional)
- `bitsandbytes` — 4-bit/8-bit quantization (optional)

### Voice Filter
- `numpy` — Numerical computation
- `scipy` — Signal processing
- `soundfile` — Audio I/O
- `sounddevice` — Audio playback
- `tkinter` — GUI (included with Python)

### Optional
- `RVC-GUI-pkg/` — RVC for voice conversion
- `ffmpeg-python` — Audio loading for RVC

## Notes

- Models are automatically downloaded from HuggingFace Hub on first run
- Local fine-tuned models in `semantic_output/`, `coarse_output/`, `fine_output/` are used automatically
- Voice cloning works best with clear, noise-free audio samples of 5-12 seconds
- Generated audio is 24kHz by default, can be resampled to 11025, 22050, or 44100 Hz
- Training notebooks support LoRA fine-tuning with optional 4-bit/8-bit quantization
- RVC repository is automatically cloned if not present when using `rvc_infer.py`
- Voice filter supports Windows, Linux, and macOS
