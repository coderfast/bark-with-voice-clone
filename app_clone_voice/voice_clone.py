#!/usr/bin/env python3
"""
Voice Clone — standalone CLI for voice cloning from audio samples.

Takes a short audio sample (5-13 seconds) of a person speaking and creates
a voice prompt (.npz) that can be used with Bark TTS for speech generation.

Usage:
  python voice_clone.py --audio reference.wav --name my_voice [--device auto]
  python voice_clone.py --name my_voice          # auto-detect from source_voice_input/
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import os
from pathlib import Path
from typing import Optional

# Patch deprecated torch.nn.utils.weight_norm before encodec imports it
import torch.nn.utils
import torch.nn.utils.parametrizations
torch.nn.utils.weight_norm = torch.nn.utils.parametrizations.weight_norm

# Add script directory to path to import local bark/ and hubert/ modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Constants
AUDIO_EXTENSIONS: tuple[str, ...] = ('.wav', '.mp3', '.ogg', '.flac', '.m4a', '.wma')
SOURCE_VOICE_DIR: str = 'source_voice_input'
PROMPTS_DIR: str = os.path.join('bark', 'assets', 'prompts')
VOICE_NAME_PATTERN: re.Pattern[str] = re.compile(r'^[a-zA-Z0-9_-]+$')
MAX_AUDIO_DURATION: int = 13  # seconds
MIN_SAMPLE_RATE: int = 8000  # Hz

# Logging setup
logger = logging.getLogger('voice_clone')


def _log(msg: str, level: int = logging.INFO) -> None:
    """Log message if not in quiet mode."""
    if not getattr(_log, '_quiet', False):
        logger.log(level, msg)


def find_source_audio() -> Optional[str]:
    """Auto-detect audio file from source_voice_input/ folder."""
    if not os.path.isdir(SOURCE_VOICE_DIR):
        return None
    audio_files = [
        f for f in os.listdir(SOURCE_VOICE_DIR)
        if f.lower().endswith(AUDIO_EXTENSIONS) and os.path.isfile(os.path.join(SOURCE_VOICE_DIR, f))
    ]
    if not audio_files:
        return None
    return os.path.join(SOURCE_VOICE_DIR, audio_files[0])


def resolve_device(choice: str) -> str:
    """Resolve device: 'auto' -> cuda > mps > cpu."""
    if choice == 'auto':
        import torch
        if torch.cuda.is_available():
            return 'cuda'
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        return 'cpu'
    if choice == 'mps':
        import torch
        if not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
            _log("Warning: MPS not available, falling back to CPU", logging.WARNING)
            return 'cpu'
    return choice


def show_device_info() -> None:
    """Display available devices and recommended settings."""
    import torch
    print("Device Information")
    print("=" * 40)
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"VRAM total: {props.total_mem / 1024**3:.1f} GB")
        free, total = torch.cuda.mem_get_info(0)
        print(f"VRAM free: {free / 1024**3:.1f} GB")
    mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
    print(f"MPS available: {mps}")
    recommended = 'cuda' if torch.cuda.is_available() else ('mps' if mps else 'cpu')
    print(f"Recommended device: {recommended}")


def validate_voice_name(name: str) -> bool:
    """Validate voice name contains only allowed characters."""
    if not VOICE_NAME_PATTERN.match(name):
        print(f"Error: Invalid voice name '{name}'")
        print("Voice names can only contain letters, numbers, underscores, and hyphens.")
        return False
    return True


def validate_audio_file(audio_path: str) -> Optional[tuple[float, int]]:
    """Validate audio file: exists, readable, duration < 13s, sample rate >= 8kHz.

    Returns:
        Tuple (duration_seconds, sample_rate) if valid, None otherwise.
    """
    if not os.path.isfile(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return None
    try:
        import soundfile as sf
        info = sf.info(audio_path)
    except Exception as e:
        print(f"Error: Cannot read audio file: {audio_path}")
        print(f"  {e}")
        return None
    duration = info.duration
    sample_rate = info.samplerate
    if sample_rate < MIN_SAMPLE_RATE:
        print(f"Error: Sample rate too low ({sample_rate} Hz)")
        print(f"  Minimum required: {MIN_SAMPLE_RATE} Hz")
        return None
    if duration > MAX_AUDIO_DURATION:
        print(f"Error: Audio too long ({duration:.1f} seconds)")
        print(f"  Maximum allowed: {MAX_AUDIO_DURATION} seconds")
        print("  Use a shorter audio clip or trim it.")
        return None
    return duration, sample_rate


def voice_exists(voice_name: str, prompts_dir: Optional[str] = None) -> bool:
    """Check if a voice prompt already exists."""
    d = prompts_dir or PROMPTS_DIR
    path = os.path.join(d, f'{voice_name}.npz')
    return os.path.isfile(path)


def validate_prompt_integrity(npz_path: str) -> bool:
    """Validate that a generated .npz prompt has the expected structure.

    Returns:
        True if valid, False otherwise.
    """
    import numpy as np
    try:
        data = np.load(npz_path)
    except Exception as e:
        print(f"Error: Cannot read prompt file: {npz_path}")
        print(f"  {e}")
        return False

    required_keys = {'fine_prompt', 'coarse_prompt', 'semantic_prompt'}
    missing = required_keys - set(data.files)
    if missing:
        print(f"Error: Prompt file is missing keys: {missing}")
        return False

    # Check shapes
    fine = data['fine_prompt']
    coarse = data['coarse_prompt']
    semantic = data['semantic_prompt']

    if fine.ndim != 2:
        print(f"Error: fine_prompt should be 2D, got {fine.ndim}D")
        return False
    if coarse.ndim != 2:
        print(f"Error: coarse_prompt should be 2D, got {coarse.ndim}D")
        return False
    if semantic.ndim != 1:
        print(f"Error: semantic_prompt should be 1D, got {semantic.ndim}D")
        return False
    if fine.shape[0] != 8:
        print(f"Error: fine_prompt should have 8 codebooks, got {fine.shape[0]}")
        return False
    if coarse.shape[0] != 2:
        print(f"Error: coarse_prompt should have 2 codebooks, got {coarse.shape[0]}")
        return False

    return True


def list_voices(output_format: str = 'table', prompts_dir: Optional[str] = None) -> None:
    """List all available voices in bark/assets/prompts/."""
    d = prompts_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), PROMPTS_DIR)
    if not os.path.isdir(d):
        print("No voices found.")
        return
    npz_files = [f for f in os.listdir(d) if f.endswith('.npz')]
    if not npz_files:
        print("No voices found.")
        return
    voices = []
    for f in sorted(npz_files):
        name = f[:-4]
        size = os.path.getsize(os.path.join(d, f))
        voices.append((name, size))
    if output_format == 'json':
        import json
        print(json.dumps([{"name": v[0], "size_bytes": v[1]} for v in voices], indent=2))
    else:
        print(f"{'Voice':<35} {'Size':>12}")
        print("-" * 49)
        for name, size in voices:
            print(f"  {name:<33} {size:>10,} B")


def show_voice_info(voice_name: str) -> None:
    """Show metadata for a specific voice prompt."""
    import numpy as np
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PROMPTS_DIR, f'{voice_name}.npz')
    if not os.path.isfile(path):
        print(f"Error: Voice '{voice_name}' not found")
        sys.exit(1)
    data = np.load(path)
    print(f"Voice: {voice_name}")
    print(f"File: {path}")
    print(f"Size: {os.path.getsize(path):,} bytes")
    print()
    for key in data.files:
        arr = data[key]
        print(f"  {key}: shape={arr.shape}, dtype={arr.dtype}")


def clone_voice(audio_path: str, voice_name: str, device: str, output_path: Optional[str] = None) -> str:
    """Extract voice features from audio and save as .npz prompt.

    Returns:
        Path to the saved prompt file.
    """
    import time
    import torch
    import numpy as np
    import soundfile as sf

    from bark.generation import load_codec_model
    from encodec.utils import convert_audio
    from hubert.hubert_manager import HuBERTManager
    from hubert.pre_kmeans_hubert import CustomHubert
    from hubert.customtokenizer import CustomTokenizer

    verbose = os.environ.get('VOICE_CLONE_VERBOSE', '0') == '1'
    _log(f"Using device: {device}")

    # Load codec model
    t0 = time.time() if verbose else None
    model = load_codec_model(use_gpu=(device == 'cuda'))
    if verbose:
        _log(f"  Codec model loaded in {time.time() - t0:.1f}s")

    # Setup HuBERT manager and download models if needed
    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()

    # Load HuBERT and tokenizer
    hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)
    tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)

    # Load and preprocess audio
    _log(f"Loading audio: {audio_path}")
    wav, sr = sf.read(audio_path, dtype='float32')
    wav = torch.from_numpy(wav)
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)  # (samples,) -> (1, samples)
    else:
        wav = wav.T  # (samples, channels) -> (channels, samples)
    wav = convert_audio(wav, sr, model.sample_rate, model.channels)
    wav = wav.to(device)

    # Extract semantic tokens
    t1 = time.time() if verbose else None
    _log("Extracting semantic tokens...")
    semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
    semantic_tokens = tokenizer.get_token(semantic_vectors)
    if verbose:
        _log(f"  Semantic extraction took {time.time() - t1:.1f}s")

    # Extract encodec codes
    t2 = time.time() if verbose else None
    _log("Extracting encodec codes...")
    with torch.no_grad():
        encoded_frames = model.encode(wav.unsqueeze(0))
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()
    if verbose:
        _log(f"  EnCodec encoding took {time.time() - t2:.1f}s")

    # Move to CPU
    codes = codes.cpu().numpy()
    semantic_tokens = semantic_tokens.cpu().numpy()

    # Determine output path
    if output_path is None:
        output_path = os.path.join(PROMPTS_DIR, f'{voice_name}.npz')
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    # Save as prompt
    np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)
    _log(f"Voice saved: {output_path}")

    # Validate integrity
    if not validate_prompt_integrity(output_path):
        print("Warning: Generated prompt failed integrity check")
    else:
        _log("Prompt integrity validated OK")

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Voice Clone — create voice prompts from audio samples"
    )
    parser.add_argument(
        '--device',
        choices=['auto', 'cuda', 'cpu', 'mps'],
        default='auto',
        help='Device to use: auto (default), cuda, cpu, or mps'
    )
    parser.add_argument('--device-info', action='store_true', help='Show available devices and recommended settings')
    parser.add_argument('--version', action='version', version='%(prog)s 1.1.0')
    parser.add_argument('--verbose', action='store_true', help='Verbose output with timing info')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode, suppress all output except errors')
    parser.add_argument('--audio', help='Path to reference audio file (<13s). If not provided, auto-detects from source_voice_input/')
    parser.add_argument('--name', help='Name for the cloned voice (required for cloning)')
    parser.add_argument('--output', help='Output path for the .npz prompt file (default: bark/assets/prompts/<name>.npz)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing voice')
    parser.add_argument('--list', dest='list_voices', action='store_true', help='List available voices')
    parser.add_argument('--info', dest='info_voice', metavar='VOICE', help='Show info for a voice')

    args = parser.parse_args()

    # Setup quiet mode
    if args.quiet:
        _log._quiet = True  # type: ignore[attr-defined]
        logger.setLevel(logging.CRITICAL)

    # Setup verbose mode
    if args.verbose:
        os.environ['VOICE_CLONE_VERBOSE'] = '1'
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(message)s')

    # --device-info takes precedence
    if args.device_info:
        show_device_info()
        return

    # --list
    if args.list_voices:
        list_voices()
        return

    # --info
    if args.info_voice:
        if not validate_voice_name(args.info_voice):
            sys.exit(1)
        show_voice_info(args.info_voice)
        return

    # For cloning, --name is required
    if not args.name:
        parser.error("--name is required for voice cloning")

    # Validate voice name
    if not validate_voice_name(args.name):
        sys.exit(1)

    # Check if voice already exists
    output_path = args.output
    if output_path is None:
        if voice_exists(args.name) and not args.force:
            print(f"Error: Voice '{args.name}' already exists")
            print(f"  Use --force to overwrite, or choose a different name")
            sys.exit(1)
    else:
        # If custom output path exists and no --force, error
        if os.path.isfile(output_path) and not args.force:
            print(f"Error: File already exists: {output_path}")
            print(f"  Use --force to overwrite")
            sys.exit(1)

    audio_path = args.audio

    # Auto-detect from source_voice_input/ if --audio not provided
    if not audio_path:
        audio_path = find_source_audio()
        if audio_path:
            _log(f"Auto-detected audio: {audio_path}")
        else:
            print(f"Error: No audio file specified and none found in '{SOURCE_VOICE_DIR}/'")
            print(f"Put a .wav, .mp3, or .ogg file in '{SOURCE_VOICE_DIR}/' or use --audio flag")
            sys.exit(1)

    # Validate audio file
    audio_info = validate_audio_file(audio_path)
    if audio_info is None:
        sys.exit(1)

    duration, sample_rate = audio_info
    _log(f"Audio: {duration:.1f}s, {sample_rate} Hz")

    device = resolve_device(args.device)

    try:
        result_path = clone_voice(audio_path, args.name, device, output_path)
        if args.quiet:
            print(result_path)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError during voice cloning: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
