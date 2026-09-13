# TECHNICALSTACK.md — app_clone_voice

## Runtime

| Component | Version/Detail |
|-----------|----------------|
| Python | >=3.8 |
| OS | Cross-platform (Linux, Windows, macOS) |
| GPU Support | CUDA (NVIDIA), MPS (Apple Silicon), CPU fallback |

## Core ML Framework

| Library | Purpose |
|---------|---------|
| **PyTorch** (`torch`) | Deep learning framework, model inference |
| **soundfile** | Audio loading (replaces `torchaudio` for load/info) |
| **torchaudio** | Audio resampling (via `torchaudio.functional.resample`) |
| **transformers** | HuBERT model loading |
| **encodec** | Neural audio codec (EnCodec) for audio encoding |

## Audio Processing

| Library | Purpose |
|---------|---------|
| **soundfile** | Audio loading, format detection, duration/sample rate info |
| **torchaudio** | Resampling to 16kHz (via `torchaudio.functional.resample`) |
| **numpy** | Array manipulation for audio data |

## Model Libraries

| Library | Purpose |
|---------|---------|
| **einops** | Tensor reshaping operations |
| **huggingface_hub** | Model downloads from Hugging Face Hub |
| **tqdm** | Progress bars |

## Models Used

| Model | Source | Purpose |
|-------|--------|---------|
| **EnCodec** | facebook/encodec | Audio codec (encode only) |
| **HuBERT Base** | facebook/hubert | Speech representation extraction |
| **CustomTokenizer** | GitMylo/bark-voice-cloning | Semantic token quantization (10K vocab) |

## Model Sizes

| Model | Size | Cache Location |
|-------|------|----------------|
| EnCodec | ~50MB | `~/.cache/serp/bark_v0/` |
| HuBERT base | ~390MB | `data/models/hubert/` |
| CustomTokenizer | ~30MB | `data/models/hubert/` |

## Audio Specifications

| Parameter | Value |
|-----------|-------|
| Input formats | WAV, MP3, OGG, FLAC, M4A, WMA |
| Input duration | 5-13 seconds |
| Input sample rate | Min 8kHz, recommended 44.1kHz+ |
| HuBERT input rate | 16,000 Hz (resampled internally) |
| Semantic token rate | 49.9 Hz |
| Semantic vocab size | 10,000 tokens |
| Codebook size | 1,024 codes |
| Coarse codebooks | 2 |
| Fine codebooks | 8 |

## Data Flow

```
Audio Input (any format)
    ↓ soundfile.read()
Resample to 16kHz
    ↓
HuBERT → semantic features (768-dim)
    ↓
CustomTokenizer → semantic tokens (10K vocab)
    ↓
EnCodec → 8 codebook codes
    ↓
Save as .npz {semantic_prompt, coarse_prompt, fine_prompt}
```

## File Formats

| Format | Extension | Content |
|--------|-----------|---------|
| Voice prompt | `.npz` | Compressed numpy arrays: `semantic_prompt`, `coarse_prompt`, `fine_prompt` |
| Model weights | `.pt` | PyTorch state dict |

## Dependencies Tree

```
voice_clone.py
├── torch (core)
├── soundfile (audio loading + format detection)
├── torchaudio (resampling only)
├── numpy (arrays)
├── encodec (audio codec - encode only)
│   └── torch
├── transformers (HuBERT model)
│   └── torch
├── einops (tensors)
├── huggingface_hub (model downloads)
└── tqdm (progress bars)
```
