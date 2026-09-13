# Bark with Voice Clone

Forked from [serp-ai/bark-with-voice-clone](https://github.com/serp-ai/bark-with-voice-clone), which is itself a fork of [Suno's BARK](https://github.com/suno-ai/bark) text-to-speech model with added voice cloning capabilities using HuBERT semantic token quantization. Clone voices from short audio samples, generate speech in that cloned voice, fine-tune models on custom datasets, and optionally apply RVC post-processing.

## Features

- **Voice Cloning**: Clone any voice from 5-12 second audio samples using HuBERT
- **Text-to-Speech**: Generate natural-sounding speech in 13 languages
- **CLI & GUI Interfaces**: Command-line tool (`bark_cli.py`) and graphical interface (`bark_gui.py`)
- **Voice Cloning App**: Standalone CLI for voice cloning (`app_clone_voice/`)
- **Audio Filter App**: GUI with 20+ audio effects (`app_voice_filter/`)
- **Custom Audio Format**: Output at 11025, 22050, or 44100 Hz with 8 or 16 bits
- **Audio Visualizations**: 19 types of analysis plots (waveform, spectrogram, MFCC, etc.)
- **Fine-tuning**: Fine-tune semantic, coarse, and fine models with LoRA and quantization
- **RVC Integration**: Optional Retrieval-based Voice Conversion post-processing
- **Multi-language**: English, German, Spanish, French, Hindi, Italian, Japanese, Korean, Polish, Portuguese, Russian, Turkish, and Chinese

## Installation

### Windows

```cmd
git clone https://github.com/coderfast/bark-with-voice-clone
cd bark-with-voice-clone
python -m venv venv
venv\Scripts\activate
pip install .
```

### Linux / Mac

```bash
git clone https://github.com/coderfast/bark-with-voice-clone
cd bark-with-voice-clone
python3 -m venv venv
source venv/bin/activate
pip install .
```

## Quick Start

### Using CLI (Recommended)

```bash
# Generate basic audio
python bark_cli.py generate "Hello world" -o output.wav

# Generate with specific voice
python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o hola.wav

# Generate with custom audio settings
python bark_cli.py generate "Hello" -v en_speaker_0 -o output.wav --sample-rate 44100 --bits 16 --channels mono

# Generate with full visualizations
python bark_cli.py generate "Hello" -o output.wav --viz-level full

# List available voices
python bark_cli.py voices

# Clone a voice
python bark_cli.py clone --audio reference.wav --name my_voice
```

### Using GUI

```bash
python bark_gui.py
```

A Tkinter-based graphical interface with voice selection, audio format options, and real-time generation.

### Using Python API

```python
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write

preload_models()
audio = generate_audio("Hello, my name is Serpy. And, uh — and I like pizza. [laughs]")
write("output.wav", SAMPLE_RATE, audio)
```

### Voice Cloning

```python
from bark import generate_audio, preload_models
from bark.api import save_audio

preload_models()

# Generate with cloned voice and custom format
audio = generate_audio(
    "Hello world!",
    history_prompt="my_voice",
    sample_rate=44100,
    bits_per_sample=16,
    channels="mono"
)

save_audio("output.wav", audio, sample_rate=44100)
```

## Standalone Applications

### Voice Cloning App (`app_clone_voice/`)

A standalone CLI application for voice cloning from audio samples. Completely independent of the main project.

```bash
cd app_clone_voice
pip install -r requirements.txt

# Clone from source_voice_input/ folder (auto-detect)
python voice_clone.py --name my_voice

# Clone from specific audio file
python voice_clone.py --audio reference.wav --name my_voice

# List available voices
python voice_clone.py --list

# Show voice info
python voice_clone.py --info en_speaker_0
```

| Flag | Description |
|------|-------------|
| `--audio PATH` | Reference audio file (<13s) |
| `--name NAME` | Voice name (required) |
| `--output PATH` | Custom output path for .npz |
| `--force` | Overwrite existing voice |
| `--device {auto,cuda,cpu,mps}` | Device selection |
| `--device-info` | Show available devices |
| `--verbose` | Detailed output with timing |
| `--quiet` | Silent mode |
| `--version` | Show version (1.1.0) |
| `--list` | List available voices |
| `--info VOICE` | Show voice metadata |

Features: Cross-platform (Windows/Linux/macOS), auto device detection, Docker support, PyInstaller portable builds. See [app_clone_voice/README.md](app_clone_voice/README.md) for full documentation.

### Audio Filter App (`app_voice_filter/`)

A GUI application for loading and modifying audio files with 20+ effects. Built with Tkinter.

```bash
cd app_voice_filter
pip install -r requirements.txt
python voice_filter.py
```

**Effects organized in 8 tabs:**
- **Basic**: Volume, Pitch, Speed
- **EQ**: 5-band equalizer (100Hz - 6kHz)
- **Filters**: Low-pass, High-pass
- **Modulation**: Chorus, Flanger, Phaser, Tremolo, Vibrato
- **Distortion**: Distortion, Bitcrusher, Overdrive
- **Time**: Reverb, Delay
- **Dynamics**: Compression, Noise Gate
- **Utility**: Fade In/Out, Normalize, Trim, Reverse

**Additional features:** Analog VU meter with needle physics, mixer-style faders with LED meters, waveform and spectrogram visualization, auto-preview on slider release, preset save/load, 19 visualization plots on save.

**Supported formats:** WAV, FLAC, OGG, MP3, AAC, M4A, WMA

**Standalone tool:** `app_voice_filter/NORMALIZE_AUDIO_VOLUME/normalize_audio.py` — LUFS loudness normalizer CLI with presets for mobile (-14 LUFS), games (-16), dialogue (-12), and more.

## CLI Reference

### Generate Command

```bash
python bark_cli.py generate "text" [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output file path (.wav) | Required |
| `-v, --voice` | Voice prompt name | None |
| `--sample-rate` | 11025, 22050, 44100 Hz | 24000 |
| `--bits` | 8 or 16 bits | float32 |
| `--channels` | mono or stereo | mono |
| `--text-temp` | Text temperature | 0.7 |
| `--waveform-temp` | Waveform temperature | 0.7 |
| `--small` | Use small models (faster) | False |
| `--no-viz` | Skip visualization plots | False |
| `--viz-level` | basic (4), speech (11), full (19) | basic |

### Clone Command

```bash
python bark_cli.py clone --audio reference.wav --name my_voice [--output-dir dir]
```

### Voices Command

```bash
python bark_cli.py voices
```

## Audio Visualizations

The project includes 19 types of audio analysis visualizations:

| Category | Visualizations |
|----------|----------------|
| **Core** | Waveform, Pitch (F0), Spectral Sweep, Spectrogram |
| **Extended** | Spectral Flatness, Zero Crossing Rate, CQT, Chromagram, Self-Similarity, LPC, Wide/Narrow Band |
| **Speech** | Mel Spectrogram, MFCC, Formants, Pitch+Voicing, Intensity, Jitter/Shimmer, HNR |
| **Bark** | EnCodec Codebook, Attention Matrix, Waveform Comparison |
| **Embedding** | UMAP Projection, Similarity Heatmap |

Use `--viz-level basic` (default), `--viz-level speech`, or `--viz-level full` with the CLI.

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

### 1. Dataset Preparation

Create a dataset with:
- `train.txt` and `valid.txt` containing `path|text` lines
- Audio files in `.wav` format
- Run `train_semantic.ipynb` to extract tokens

### 2. Training

```bash
jupyter notebook train_semantic.ipynb
jupyter notebook train_coarse.ipynb
jupyter notebook train_fine.ipynb
```

Features: LoRA adapters, 4-bit/8-bit quantization, distributed training via Accelerate, W&B logging.

### 3. Output

Fine-tuned models are saved to:
- `semantic_output/pytorch_model.bin`
- `coarse_output/pytorch_model.bin`
- `fine_output/pytorch_model.bin`

Local models in these directories are used automatically during generation.

See [AUDIO_AND_FINETUNING.md](AUDIO_AND_FINETUNING.md) for a detailed guide.

## RVC Integration

```bash
# RVC is automatically downloaded when needed
# Or manually clone:
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
```

```python
from rvc_infer import get_vc, vc_single

get_vc("path/to/model.pth", "cuda:0", True)
audio = vc_single(0, "input.wav", f0_up_key=-6, ...)
```

See [AUDIO_AND_RVC.md](AUDIO_AND_RVC.md) for a complete guide on when to use RVC vs fine-tuning.

## Model Architecture

| Model | Parameters | Attention | Output Vocab | Purpose |
|-------|-----------|-----------|--------------|---------|
| GPT (text) | 80M | Causal | 10,000 | Text → Semantic tokens |
| GPT (coarse) | 80M | Causal | 2×1,024 | Semantic → Coarse codes |
| FineGPT | 80M | Non-causal | 6×1,024 | Coarse → Fine codes |

### Audio Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `SAMPLE_RATE` | 24,000 Hz | Default output sample rate |
| `SEMANTIC_RATE_HZ` | 49.9 Hz | One token per ~20ms |
| `SEMANTIC_VOCAB_SIZE` | 10,000 | Semantic token vocabulary |
| `CODEBOOK_SIZE` | 1,024 | Audio codebook entries |
| `N_COARSE_CODEBOOKS` | 2 | Coarse model output |
| `N_FINE_CODEBOOKS` | 8 | Fine model output |

## Non-speech Sounds

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

## Project Structure

```
bark-with-voice-clone/
├── bark/                        # Core BARK TTS module
│   ├── api.py                   # High-level API with audio format options
│   ├── generation.py            # Model loading, text/semantic/coarse/fine generation
│   ├── model.py                 # GPT model architecture
│   ├── model_fine.py            # FineGPT model architecture
│   └── assets/prompts/          # 141+ pre-made voice prompts (.npz)
│
├── hubert/                      # HuBERT voice cloning module
│   ├── hubert_manager.py        # Downloads HuBERT models with verification
│   ├── pre_kmeans_hubert.py     # CustomHubert model
│   └── customtokenizer.py       # Semantic token quantizer (10K vocab)
│
├── utils/                       # Utilities
│   ├── lora.py                  # LoRA adapter support
│   ├── bitsandbytes.py          # 4-bit/8-bit quantization
│   ├── training.py              # Shared training utilities
│   ├── generation.py            # Shared generation utilities
│   ├── rvc_manager.py           # RVC auto-download manager
│   ├── audio_visualizer.py      # 11 core/extended visualizations
│   ├── speech_analyzer.py       # 7 speech-specific visualizations
│   ├── bark_analyzer.py         # 3 Bark-specific visualizations
│   └── embedding_analyzer.py    # 2 speaker embedding visualizations
│
├── app_clone_voice/             # Standalone voice cloning CLI (v1.1.0)
│   ├── voice_clone.py           # Main CLI script
│   ├── requirements.txt         # Dependencies
│   ├── Dockerfile               # Docker support
│   ├── build.py                 # PyInstaller build script
│   ├── tests/                   # 20 unit tests
│   ├── bark/                    # Local copy of bark module
│   └── hubert/                  # Local copy of hubert module
│
├── app_voice_filter/            # Audio processing GUI app
│   ├── voice_filter.py          # Entry point
│   ├── gui/app.py               # Main GUI class (~1029 lines)
│   ├── audio/processor.py       # 20+ audio effects
│   ├── widgets/                 # VU meter, mixer faders
│   ├── NORMALIZE_AUDIO_VOLUME/  # LUFS loudness normalizer CLI
│   ├── ffmpeg/                  # FFmpeg binaries for MP3/AAC/M4A/WMA
│   └── MANUALS/                 # 20 visualization manuals
│
├── bark_cli.py                  # Command Line Interface
├── bark_gui.py                  # Tkinter GUI for TTS generation
├── rvc_infer.py                 # RVC inference with auto-download
│
├── notebooks/                   # Additional notebooks
│   └── fake_classifier.ipynb    # Audio deepfake detection
│
├── *.ipynb                      # Jupyter notebooks (clone, generate, train, test)
├── datasets/                    # Training datasets
├── data/models/hubert/          # HuBERT models (downloaded on first run)
├── models/                      # Bark model weights
├── semantic_output/             # Fine-tuned semantic model
├── coarse_output/               # Fine-tuned coarse model
├── fine_output/                 # Fine-tuned fine model
├── output/                      # Generated audio output
│
├── AUDIO_AND_RVC.md             # RVC integration guide
├── AUDIO_AND_FINETUNING.md      # Fine-tuning guide
├── pyproject.toml               # Project configuration
└── LICENSE.md                   # MIT License
```

## Additional Documentation

| File | Description |
|------|-------------|
| [QUICKUSAGE.md](QUICKUSAGE.md) | Quick usage guide with CLI examples |
| [AUDIO_AND_RVC.md](AUDIO_AND_RVC.md) | Complete guide on RVC vs fine-tuning |
| [AUDIO_AND_FINETUNING.md](AUDIO_AND_FINETUNING.md) | Audio generation pipeline explained |
| [model-card.md](model-card.md) | Model card with architecture details |
| [ROADMAP.md](ROADMAP.md) | Development roadmap (all phases complete) |

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
