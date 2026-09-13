# APP_TECHNICALSTACK.md — bark-with-voice-clone

## Technical Stack

### Programming Language

| Language | Version | Usage |
|----------|---------|-------|
| **Python** | 3.8+ | Main language for all modules |

### Core Frameworks

| Framework | Version | Purpose |
|-----------|---------|---------|
| **PyTorch** | 2.0+ | Deep learning framework for model inference |
| **Torchaudio** | 2.0+ | Audio processing and resampling |
| **Transformers** | 4.0+ | BERT tokenizer for text encoding |

### Audio Processing

| Library | Purpose |
|---------|---------|
| **EnCodec** | Neural audio codec for compression/decompression |
| **SciPy** | Signal processing (filters, resampling) |
| **NumPy** | Numerical computation |
| **SoundFile** | Audio file I/O (WAV, FLAC, etc.) |
| **SoundDevice** | Audio playback |
| **FFmpeg** | Audio format conversion (external) |

### Machine Learning

| Library | Purpose |
|---------|---------|
| **Fairseq** | HuBERT model loading |
| **HuggingFace Hub** | Model downloads and caching |
| **Accelerate** | Distributed training, mixed precision |
| **Diffusers** | Learning rate schedulers |
| **Weights & Biases** | Experiment logging (optional) |
| **BitsAndBytes** | 4-bit/8-bit quantization (optional) |

### GUI

| Library | Purpose |
|---------|---------|
| **Tkinter** | Graphical user interface (included with Python) |
| **ttk** | Themed widgets for modern look |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Jupyter** | Interactive notebooks for training and experimentation |
| **Pytest** | Unit testing |
| **Black** | Code formatting |
| **Flake8** | Linting |
| **MyPy** | Type checking |

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10+, Linux, macOS 10.15+ |
| **Python** | 3.8 or higher |
| **RAM** | 8 GB |
| **Storage** | 10 GB free space |
| **GPU** | Optional (CPU inference available) |

### Recommended Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 11, Ubuntu 20.04+, macOS 12+ |
| **Python** | 3.10 or higher |
| **RAM** | 16 GB or more |
| **Storage** | 50 GB free space (for models) |
| **GPU** | NVIDIA GPU with 8+ GB VRAM (CUDA 11.7+) |

## Model Architecture

### Bark Models

| Model | Parameters | Architecture | Purpose |
|-------|-----------|--------------|---------|
| **Text GPT** | 80M | Causal Transformer | Text → Semantic tokens |
| **Coarse GPT** | 80M | Causal Transformer | Semantic → Coarse codes |
| **FineGPT** | 80M | Non-causal Transformer | Coarse → Fine codes |
| **EnCodec** | ~15M | Neural Codec | Audio compression |

### Voice Cloning Models

| Model | Source | Purpose |
|-------|--------|---------|
| **HuBERT** | Facebook Research | Speech representation |
| **CustomTokenizer** | gitmylo | Semantic token quantization |

## Audio Specifications

### Input Formats

| Format | Extension | Support |
|--------|-----------|---------|
| WAV | `.wav` | Full |
| MP3 | `.mp3` | Full |
| AAC | `.aac` | Full |
| FLAC | `.flac` | Full |
| OGG | `.ogg` | Full |
| M4A | `.m4a` | Full |
| WMA | `.wma` | Full |

### Output Formats

| Format | Sample Rates | Bit Depths |
|--------|--------------|------------|
| WAV | 11025, 22050, 24000, 44100 Hz | 8, 16, 32-bit float |

### Audio Parameters

| Parameter | Range | Default |
|-----------|-------|---------|
| Sample Rate | 11025 - 44100 Hz | 24000 Hz |
| Bit Depth | 8, 16, 32-bit float | 32-bit float |
| Channels | Mono, Stereo | Mono |

## Voice Filter Effects

### Basic Effects

| Effect | Range | Description |
|--------|-------|-------------|
| Volume | 0.0 - 2.0 | Amplitude adjustment |
| Pitch | -12 - +12 semitones | Frequency shift |
| Speed | 0.5x - 2.0x | Playback speed |

### EQ (5-Band)

| Band | Frequency | Range |
|------|-----------|-------|
| Bass | 100 Hz | -12 - +12 dB |
| Low Mid | 400 Hz | -12 - +12 dB |
| Mid | 1 kHz | -12 - +12 dB |
| High Mid | 2.5 kHz | -12 - +12 dB |
| Treble | 6 kHz | -12 - +12 dB |

### Filters

| Filter | Range | Description |
|--------|-------|-------------|
| Low Pass | 100 - 20000 Hz | Removes high frequencies |
| High Pass | 20 - 5000 Hz | Removes low frequencies |

### Modulation Effects

| Effect | Range | Description |
|--------|-------|-------------|
| Chorus | 0.0 - 1.0 | Doubling effect |
| Flanger | 0.0 - 1.0 | Sweeping delay effect |
| Phaser | 0.0 - 1.0 | Phase shifting effect |
| Tremolo | 0.0 - 1.0 | Amplitude modulation |
| Vibrato | 0.0 - 1.0 | Frequency modulation |

### Distortion Effects

| Effect | Range | Description |
|--------|-------|-------------|
| Distortion | 0.0 - 1.0 | Soft clipping |
| Bitcrusher | 4 - 32 bits | Bit reduction |
| Overdrive | 1.0 - 10.0x | Gain boost |

### Time-Based Effects

| Effect | Range | Description |
|--------|-------|-------------|
| Reverb | 0.0 - 1.0 | Room simulation |
| Delay | 0 - 500 ms | Echo effect |

### Dynamics

| Effect | Range | Description |
|--------|-------|-------------|
| Compressor Threshold | -40 - 0 dB | Compression trigger level |
| Compressor Ratio | 1:1 - 20:1 | Compression amount |
| Gate | -60 - 0 dB | Noise gate threshold |

### Utility

| Effect | Range | Description |
|--------|-------|-------------|
| Fade In | 0 - 5000 ms | Gradual volume increase |
| Fade Out | 0 - 5000 ms | Gradual volume decrease |
| Normalize | -24 - 0 dB | Level normalization |
| Trim Start | 0 - 100 s | Start point |
| Trim End | 0 - 100 s | End point |
| Reverse | On/Off | Reverse playback |

## Cross-Platform Support

### Windows

- **Audio Backend**: WASAPI, MME, DirectSound
- **GUI**: Native Tkinter
- **Installation**: `pip install -r requirements.txt`

### Linux

- **Audio Backend**: ALSA, PulseAudio
- **GUI**: Tkinter (may need `python3-tk`)
- **Installation**:
  ```bash
  sudo apt-get install python3-tk libportaudio2
  pip install -r requirements.txt
  ```

### macOS

- **Audio Backend**: CoreAudio
- **GUI**: Native Tkinter
- **Installation**:
  ```bash
  brew install python@3.10
  pip install -r requirements.txt
  ```

## Performance Considerations

### GPU Acceleration

- CUDA 11.7+ required for NVIDIA GPUs
- Automatic device detection (CUDA > MPS > CPU)
- Mixed precision training with bf16

### Memory Management

- Models cached in `~/.cache/serp/bark_v0/`
- Local fine-tuned models prioritized
- Automatic GPU memory cleanup

### Optimization

- KV caching for faster generation
- Flash attention support (PyTorch nightly)
- Configurable model sizes (small vs full)

## Security Considerations

### Model Downloads

- Models downloaded from HuggingFace Hub
- SHA256 verification available
- Local model priority (no download if present)

### Audio Processing

- Input validation on all parameters
- Clipping protection on all outputs
- Thread-safe audio playback

## Future Enhancements

### Planned Features

- Real-time audio streaming
- Multi-track editing
- VST plugin support
- Batch processing
- Cloud rendering

### Performance Improvements

- CUDA optimization for all effects
- WebAssembly compilation
- GPU-accelerated EQ and filters
- Parallel processing for multi-core CPUs
