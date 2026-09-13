# Bark with Voice Clone

A fork of [Suno's BARK](https://github.com/suno-ai/bark) text-to-speech model with added voice cloning capabilities using HuBERT semantic token quantization. Clone voices from short audio samples, generate speech in that cloned voice, fine-tune models on custom datasets, and optionally apply RVC post-processing.

## Features

- **Voice Cloning**: Clone any voice from 5-12 second audio samples using HuBERT
- **Text-to-Speech**: Generate natural-sounding speech in multiple languages
- **CLI Interface**: Generate audio directly from command line
- **Custom Audio Format**: Output at 11025, 22050, or 44100 Hz with 8 or 16 bits
- **Fine-tuning**: Fine-tune semantic, coarse, and fine models with LoRA and quantization
- **RVC Integration**: Optional Retrieval-based Voice Conversion post-processing
- **Multi-language**: Supports English, German, Spanish, French, Hindi, Italian, Japanese, Korean, Polish, Portuguese, Russian, Turkish, and Chinese

## Installation

### Windows

```cmd
git clone https://github.com/your-username/bark-with-voice-clone
cd bark-with-voice-clone
python -m venv venv
venv\Scripts\activate
pip install .
```

### Linux / Mac

```bash
git clone https://github.com/your-username/bark-with-voice-clone
cd bark-with-voice-clone
python3 -m venv venv
source venv/bin/activate
pip install .
```

Eduardo remember the next:
https://github.com/Tiger14n/RVC-GUI/blob/main/README.md
https://github.com/Tiger14n/RVC-GUI/releases/tag/Windows-pkg
and put in a folder named RVC-GUI-pkg

## Quick Start

### Using CLI (Recommended)

```bash
# Generate basic audio
python bark_cli.py generate "Hello world" -o output.wav

# Generate with specific voice
python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o hola.wav

# Generate with custom audio settings
python bark_cli.py generate "Hello" -v en_speaker_0 -o output.wav --sample-rate 44100 --bits 16 --channels mono

# List available voices
python bark_cli.py voices

# Clone a voice
python bark_cli.py clone --audio reference.wav --name my_voice
```

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

### Clone Command

```bash
python bark_cli.py clone --audio reference.wav --name my_voice
```

### Voices Command

```bash
python bark_cli.py voices
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

### 3. Output

Fine-tuned models are saved to:
- `semantic_output/pytorch_model.bin`
- `coarse_output/pytorch_model.bin`
- `fine_output/pytorch_model.bin`

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

## Model Architecture

| Model | Parameters | Attention | Output Vocab | Purpose |
|-------|-----------|-----------|--------------|---------|
| GPT (text) | 80M | Causal | 10,000 | Text → Semantic tokens |
| GPT (coarse) | 80M | Causal | 2×1,024 | Semantic → Coarse codes |
| FineGPT | 80M | Non-causal | 6×1,024 | Coarse → Fine codes |

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
├── bark/                    # Core BARK TTS module
├── hubert/                  # HuBERT voice cloning module
├── utils/                   # Utilities (LoRA, training, RVC manager)
├── bark_cli.py              # Command Line Interface
├── notebooks/               # Additional notebooks
├── datasets/                # Training datasets
├── data/models/hubert/      # HuBERT models
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
