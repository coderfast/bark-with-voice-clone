# Bark with Voice Clone

A fork of [Suno's BARK](https://github.com/suno-ai/bark) text-to-speech model with added voice cloning capabilities using HuBERT semantic token quantization. Clone voices from short audio samples, generate speech in that cloned voice, fine-tune models on custom datasets, and optionally apply RVC post-processing.

## Features

- **Voice Cloning**: Clone any voice from 5-12 second audio samples using HuBERT
- **Text-to-Speech**: Generate natural-sounding speech in multiple languages
- **Fine-tuning**: Fine-tune semantic, coarse, and fine models with LoRA and quantization
- **RVC Integration**: Optional Retrieval-based Voice Conversion post-processing
- **Multi-language**: Supports English, German, Spanish, French, Hindi, Italian, Japanese, Korean, Polish, Portuguese, Russian, Turkish, and Chinese

## Installation

```bash
git clone https://github.com/your-username/bark-with-voice-clone
cd bark-with-voice-clone
pip install .
```

### Optional: RVC for Voice Conversion

```bash
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
```

Eduardo remember the next:
https://github.com/Tiger14n/RVC-GUI/blob/main/README.md
https://github.com/Tiger14n/RVC-GUI/releases/tag/Windows-pkg
and put in a folder named RVC-GUI-pkg

## Quick Start

### Basic Text-to-Speech

```python
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write

preload_models()
audio = generate_audio("Hello, my name is Serpy. And, uh — and I like pizza. [laughs]")
write("output.wav", SAMPLE_RATE, audio)
```

### Voice Cloning

1. Clone a voice from an audio sample:

```python
from bark.generation import load_codec_model, generate_text_semantic
from encodec.utils import convert_audio
import torchaudio
import torch

device = 'cuda'
model = load_codec_model(use_gpu=True)

# Load HuBERT for voice cloning
from hubert.hubert_manager import HuBERTManager
from hubert.pre_kmeans_hubert import CustomHubert
from hubert.customtokenizer import CustomTokenizer

hubert_manager = HuBERTManager()
hubert_manager.make_sure_hubert_installed()
hubert_manager.make_sure_tokenizer_installed()

hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)
tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)

# Load and process reference audio
wav, sr = torchaudio.load('reference.wav')
wav = convert_audio(wav, sr, model.sample_rate, model.channels)
wav = wav.to(device)

# Extract semantic tokens
semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
semantic_tokens = tokenizer.get_token(semantic_vectors)

# Extract audio codes
with torch.no_grad():
    encoded_frames = model.encode(wav.unsqueeze(0))
codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()

# Save as voice prompt
import numpy as np
np.savez('bark/assets/prompts/my_voice.npz', 
         fine_prompt=codes.cpu().numpy(), 
         coarse_prompt=codes[:2, :].cpu().numpy(), 
         semantic_prompt=semantic_tokens.cpu().numpy())
```

2. Generate speech with cloned voice:

```python
audio = generate_audio("Hello world!", history_prompt="my_voice")
write("output.wav", SAMPLE_RATE, audio)
```

### Using Fine-tuned Models

```python
preload_models(
    text_model_path="semantic_output/pytorch_model.bin",
    coarse_model_path="coarse_output/pytorch_model.bin",
    fine_model_path="fine_output/pytorch_model.bin",
)

audio = generate_audio("Hello!", history_prompt="my_voice")
```

## Jupyter Notebooks

| Notebook | Description |
|----------|-------------|
| `clone_voice.ipynb` | Voice cloning + generation workflow |
| `generate.ipynb` | Audio generation with RVC support |
| `generate_chunked.ipynb` | Long text generation with chunking and RVC |
| `train_semantic.ipynb` | Fine-tune text-to-semantic model |
| `train_coarse.ipynb` | Fine-tune semantic-to-coarse model |
| `train_fine.ipynb` | Fine-tune coarse-to-fine model |
| `test_models.ipynb` | Test fine-tuned models with RVC |
| `rvc_test.ipynb` | RVC inference testing |
| `notebooks/fake_classifier.ipynb` | Audio deepfake detection classifier |

## Fine-tuning

The project supports fine-tuning all three model stages using LoRA and optional quantization:

### 1. Dataset Preparation

Create a dataset with:
- `train.txt` and `valid.txt` containing `path|text` lines
- Audio files in `.wav` format
- Run `train_semantic.ipynb` to extract tokens (creates `tokens/` subdirectory)

### 2. Training

```bash
# Fine-tune semantic model
jupyter notebook train_semantic.ipynb

# Fine-tune coarse model
jupyter notebook train_coarse.ipynb

# Fine-tune fine model
jupyter notebook train_fine.ipynb
```

Training features:
- LoRA adapters (configurable dimension, scaling, dropout)
- Mixed precision (bf16)
- Gradient accumulation
- Checkpoint resumption
- W&B logging (optional)

### 3. Output

Fine-tuned models are saved to:
- `semantic_output/pytorch_model.bin`
- `coarse_output/pytorch_model.bin`
- `fine_output/pytorch_model.bin`

## RVC Integration

Optional RVC post-processing for voice conversion:

```python
from rvc_infer import get_vc, vc_single

# Load RVC model
get_vc("path/to/model.pth", "cuda:0", True)

# Convert audio
audio = vc_single(
    sid=0,
    input_audio="input.wav",
    f0_up_key=-6,
    f0_file=None,
    f0_method="harvest",
    file_index="path/to/index",
    index_rate=0.75,
    filter_radius=3,
    resample_sr=24000,
    rms_mix_rate=0.25,
    protect=0.33
)
```

## Model Architecture

| Model | Parameters | Attention | Output Vocab | Purpose |
|-------|-----------|-----------|--------------|---------|
| GPT (text) | 80M | Causal | 10,000 | Text → Semantic tokens |
| GPT (coarse) | 80M | Causal | 2×1,024 | Semantic → Coarse codes |
| FineGPT | 80M | Non-causal | 6×1,024 | Coarse → Fine codes |

- **EnCodec**: Neural audio codec (24kHz, 8 codebooks)
- **HuBERT**: Self-supervised speech representation (modified, no kmeans)
- **BERT tokenizer**: `bert-base-multilingual-cased`

## Non-speech Sounds

Bark can generate various non-speech sounds:

- `[laughter]` or `[laughs]`
- `[sighs]`
- `[music]`
- `[gasps]`
- `[clears throat]`
- `[takes breath]`
- `—` or `...` for hesitations
- `♪` for song lyrics
- CAPITALIZATION for emphasis
- `MAN/WOMAN:` for speaker bias

## Supported Languages

| Language | Code | Status |
|----------|------|--------|
| English | en | Supported |
| German | de | Supported |
| Spanish | es | Supported |
| French | fr | Supported |
| Hindi | hi | Supported |
| Italian | it | Supported |
| Japanese | ja | Supported |
| Korean | ko | Supported |
| Polish | pl | Supported |
| Portuguese | pt | Supported |
| Russian | ru | Supported |
| Turkish | tr | Supported |
| Chinese (simplified) | zh | Supported |

## Hardware Requirements

- **GPU**: Recommended for reasonable inference speed
- **PyTorch**: 2.0+ with CUDA 11.7 or CUDA 12.0
- **VRAM**: 4GB+ for small models, 8GB+ for full models
- **RAM**: 8GB+ recommended

On modern GPUs with PyTorch nightly, Bark can generate audio in roughly realtime. On older GPUs or CPU, inference may be 10-100x slower.

## Project Structure

```
bark-with-voice-clone/
├── bark/                    # Core BARK TTS module
├── hubert/                  # HuBERT voice cloning module
├── utils/                   # LoRA and quantization utilities
├── notebooks/               # Additional notebooks
├── datasets/                # Training datasets
├── data/models/hubert/      # HuBERT models (downloaded on first run)
├── models/                  # Bark model weights
├── semantic_output/         # Fine-tuned semantic model
├── coarse_output/           # Fine-tuned coarse model
├── fine_output/             # Fine-tuned fine model
├── *.ipynb                  # Jupyter notebooks
└── rvc_infer.py             # RVC inference
```

## Contributors

Huge shoutout & thank you to:

[gitmylo](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer/) 
for the solution to the semantic token generation for better voice clones and finetunes (HuBERT, etc.)

***

<div style="display: flex; flex-wrap: wrap;">
  <a href="https://github.com/francislabountyjr" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/73464335?v=4" alt="francislabountyjr" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/gkucsko" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/5068315?v=4" alt="gkucsko" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/kmfreyberg" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/32879321?v=4" alt="kmfreyberg" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/Vaibhavs10" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/18682411?v=4" alt="Vaibhavs10" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/devinschumacher" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/45643901?v=4" alt="devinschumacher" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/mcamac" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/461009?v=4" alt="mcamac" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/fiq" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/236293?v=4" alt="fiq" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/zygi" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/2059901?v=4" alt="zygi" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/jn-jairo" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/5104869?v=4" alt="jn-jairo" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/gitmylo" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/36931363?v=4" alt="gitmylo" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/alyxdow" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/84633629?v=4" alt="alyxdow" style="border-radius: 50%; width: 75px; height: 75px;"></a>
  <a href="https://github.com/mikeyshulman" target="_blank" style="margin: 5px; display: inline-block;"><img src="https://avatars.githubusercontent.com/u/2565833?v=4" alt="mikeyshulman" style="border-radius: 50%; width: 75px; height: 75px;"></a>
</div>

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.
