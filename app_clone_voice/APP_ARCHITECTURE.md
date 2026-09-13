# APP_ARCHITECTURE.md — app_clone_voice

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                            │
│                     voice_clone.py                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  --audio, --name, --device, --force, --verbose           │   │
│  └──────────────────────┬───────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Voice Cloning Module                          │
│                     clone_voice()                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Local Modules                              │
│  ┌─────────────────────────┐    ┌───────────────────────────┐   │
│  │        hubert/          │    │          bark/            │   │
│  │  ┌──────────────────┐   │    │  ┌─────────────────────┐  │   │
│  │  │  HuBERTManager   │   │    │  │   generation.py     │  │   │
│  │  │  CustomHubert    │   │    │  │  load_codec_model() │  │   │
│  │  │  CustomTokenizer │   │    │  └─────────────────────┘  │   │
│  │  └──────────────────┘   │    │  ┌─────────────────────┐  │   │
│  └─────────────────────────┘    │  │   model.py          │  │   │
│                                 │  │   model_fine.py     │  │   │
│                                 │  └─────────────────────┘  │   │
│                                 └───────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Models                              │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐              │
│  │   HuBERT   │  │  EnCodec   │  │    BERT      │              │
│  │  (390MB)   │  │   (50MB)   │  │   (440MB)    │              │
│  └────────────┘  └────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Diagram

### CLI Layer (`voice_clone.py`)

```
voice_clone.py
├── Monkey-patch: torch.nn.utils.weight_norm → parametrizations.weight_norm
├── resolve_device(choice)     # Device selection logic
├── clone_voice()              # Voice cloning pipeline
├── show_device_info()         # Display device information
├── list_voices()              # List available voices
├── show_voice_info()          # Show voice metadata
└── main()                     # Argument parsing, command dispatch
```

### Voice Cloning Pipeline

```
clone_voice(audio_path, voice_name, device)
│
├── Load EnCodec model
│   └── bark.generation.load_codec_model()
│
├── Setup HuBERT
│   ├── HuBERTManager.make_sure_hubert_installed()
│   └── HuBERTManager.make_sure_tokenizer_installed()
│
├── Load models to device
│   ├── CustomHubert(checkpoint_path)
│   └── CustomTokenizer.load_from_checkpoint()
│
├── Process audio
│   ├── soundfile.read(audio_path)
│   ├── convert_audio(wav, sr, target_sr, channels)
│   └── wav.to(device)
│
├── Extract features
│   ├── hubert_model.forward(wav)
│   ├── tokenizer.get_token(semantic_vectors)
│   └── model.encode(wav.unsqueeze(0))
│
└── Save prompt
    └── np.savez(output_path, fine_prompt, coarse_prompt, semantic_prompt)
```

## Data Flow

```
reference.wav (any format)
       │
       ▼
┌──────────────┐
│ soundfile    │ ──→ wav tensor [channels, samples]
│ .read()      │     sr: source sample rate
└──────────────┘
       │
       ▼
┌──────────────┐
│ encodec       │ ──→ wav tensor [1, channels, samples]
│ .convert()    │     sr: 24000 (model.sample_rate)
└──────────────┘
       │
       ├───────────────────────┐
       ▼                       ▼
┌──────────────┐      ┌──────────────┐
│   HuBERT     │      │   EnCodec    │
│  .forward()  │      │   .encode()  │
└──────────────┘      └──────────────┘
       │                       │
       ▼                       ▼
┌──────────────┐      ┌──────────────┐
│  Custom      │      │   codes      │
│  Tokenizer   │      │ [8, T]       │
│  .get_token()│      │              │
└──────────────┘      └──────────────┘
       │                       │
       ▼                       ▼
┌──────────────┐      ┌──────────────┐
│ semantic_    │      │ codes.npy    │
│ tokens.npy   │      │              │
│ [T_semantic] │      │              │
└──────────────┘      └──────────────┘
       │                       │
       └───────────┬───────────┘
                   ▼
          ┌──────────────┐
          │   np.savez   │
          │   .npz file  │
          └──────────────┘
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| Missing audio file | `validate_audio_file()` → clear error message |
| Audio too long (>13s) | `validate_audio_file()` → error with duration info |
| Sample rate too low (<8kHz) | `validate_audio_file()` → error with rate info |
| Invalid voice name | `validate_voice_name()` → error with allowed chars |
| Voice already exists | Check + `--force` flag to overwrite |
| Voice not found (info) | Error with message |
| GPU OOM | Falls back to CPU (if auto) or crashes |
| Missing models | Auto-downloaded via HuBERTManager / huggingface_hub |
| Invalid audio format | `soundfile` raises exception |
| CUDA not available | `resolve_device()` returns 'cpu' |
| KeyboardInterrupt | Clean "Aborted by user" message |
| Other exceptions | Message shown; traceback only with `--verbose` |

## File I/O

### Input

| File | Handler | Validation |
|------|---------|------------|
| `--audio` | `soundfile.read()` | `validate_audio_file()`: exists, duration <13s, rate >=8kHz |

### Output

| File | Handler | Validation |
|------|---------|------------|
| Voice prompt | `np.savez()` | `validate_voice_name()`: alphanumeric, underscore, hyphen |

### Cached Files

| Location | Content | Auto-created |
|----------|---------|--------------|
| `data/models/hubert/hubert.pt` | HuBERT weights | Yes |
| `data/models/hubert/tokenizer.pth` | Tokenizer weights | Yes |
| `~/.cache/serp/bark_v0/` | EnCodec model | Yes |

## Performance Characteristics

| Operation | Time (GPU) | Time (CPU) | Memory |
|-----------|-----------|-----------|--------|
| Clone voice | ~5-10s | ~30-60s | ~2GB |
| Model loading | ~5-10s | ~10-20s | ~2GB |

*Approximate, depends on hardware and audio length*
