"""
Bark CLI - Command Line Interface for Text-to-Speech Generation

Usage:
    python bark_cli.py generate "Hello world" -o output.wav
    python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o hola.wav --sample-rate 44100 --bits 16 --channels mono
    python bark_cli.py voices
"""

import argparse
import os
import sys
import time
from typing import List, Optional

import numpy as np


AVAILABLE_VOICES = {
    "es": [f"es_speaker_{i}" for i in range(10)],
    "en": [f"en_speaker_{i}" for i in range(10)],
    "de": [f"de_speaker_{i}" for i in range(10)],
    "fr": [f"fr_speaker_{i}" for i in range(10)],
    "it": [f"it_speaker_{i}" for i in range(10)],
    "pt": [f"pt_speaker_{i}" for i in range(10)],
    "ja": [f"ja_speaker_{i}" for i in range(10)],
    "ko": [f"ko_speaker_{i}" for i in range(10)],
    "zh": [f"zh_speaker_{i}" for i in range(10)],
    "hi": [f"hi_speaker_{i}" for i in range(10)],
    "pl": [f"pl_speaker_{i}" for i in range(10)],
    "ru": [f"ru_speaker_{i}" for i in range(10)],
    "tr": [f"tr_speaker_{i}" for i in range(10)],
}


def print_header():
    """Print CLI header."""
    print("=" * 60)
    print("BARK CLI - Text-to-Speech with Voice Cloning")
    print("=" * 60)


def print_available_voices():
    """Print all available voices grouped by language."""
    print("\nAvailable voices:\n")
    for lang, voices in AVAILABLE_VOICES.items():
        print(f"  {lang.upper()}: {', '.join(voices)}")
    print()


def generate_audio_cli(
    text: str,
    output: str,
    voice: Optional[str] = None,
    sample_rate: Optional[int] = None,
    bits: Optional[int] = None,
    channels: Optional[str] = None,
    text_temp: float = 0.7,
    waveform_temp: float = 0.7,
    small_models: bool = False,
    no_viz: bool = False,
    viz_level: str = "basic",
) -> str:
    """Generate audio from text using Bark.

    Args:
        text: Text to generate audio for
        output: Output file path
        voice: Voice prompt name (e.g., es_speaker_0)
        sample_rate: Output sample rate (11025, 22050, 44100)
        bits: Bits per sample (8 or 16)
        channels: Channels (mono or stereo)
        text_temp: Text generation temperature
        waveform_temp: Waveform generation temperature
        small_models: Use small models (faster but lower quality)
        no_viz: Skip generating visualization plots
        viz_level: Visualization level (basic, speech, full)

    Returns:
        Path to generated audio file
    """
    from bark import SAMPLE_RATE, generate_audio, preload_models
    from bark.api import save_audio, save_audio_with_visualizations

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else '.', exist_ok=True)

    # Load models
    print(f"\nLoading models {'(small)' if small_models else '(full)'}...")
    start_time = time.time()
    preload_models(
        text_use_small=small_models,
        coarse_use_small=small_models,
        fine_use_small=small_models,
    )
    print(f"Models loaded in {time.time() - start_time:.1f}s")

    # Generate audio
    print(f"\nGenerating audio for: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
    if voice:
        print(f"Voice: {voice}")

    start_time = time.time()
    audio = generate_audio(
        text,
        history_prompt=voice,
        text_temp=text_temp,
        waveform_temp=waveform_temp,
        sample_rate=sample_rate,
        bits_per_sample=bits,
        channels=channels,
    )
    print(f"Audio generated in {time.time() - start_time:.1f}s")

    # Determine effective sample rate for saving
    effective_sr = sample_rate if sample_rate else SAMPLE_RATE

    # Save audio and visualizations
    if no_viz:
        save_audio(output, audio, sample_rate=effective_sr, source_sample_rate=effective_sr)
        print(f"\nAudio saved to: {output}")
    else:
        results = save_audio_with_visualizations(
            filepath=output,
            audio=audio,
            sample_rate=effective_sr,
            source_sample_rate=SAMPLE_RATE,
            visualizations=viz_level,
        )
        print(f"\nAudio saved to: {results['audio']}")
        print(f"Visualizations ({len(results) - 1} files):")
        for viz_type, path in sorted(results.items()):
            if viz_type != 'audio':
                print(f"  {viz_type}: {path}")

    # Get file size
    file_size = os.path.getsize(output)
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    else:
        size_str = f"{file_size / 1024:.1f} KB"

    print(f"Size: {size_str}")
    return output


def clone_voice_cli(
    audio_path: str,
    output_name: str,
    output_dir: str = "bark/assets/prompts",
) -> str:
    """Clone a voice from an audio file.

    Args:
        audio_path: Path to reference audio file (5-12 seconds)
        output_name: Name for the cloned voice prompt
        output_dir: Directory to save the prompt file

    Returns:
        Path to saved prompt file
    """
    from bark.generation import load_codec_model
    from encodec.utils import convert_audio
    import torchaudio
    import torch

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Load models
    print("\nLoading models...")
    model = load_codec_model(use_gpu=(device == 'cuda'))

    from hubert.hubert_manager import HuBERTManager
    from hubert.pre_kmeans_hubert import CustomHubert
    from hubert.customtokenizer import CustomTokenizer

    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()

    hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)
    tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)

    # Load and process audio
    print(f"\nProcessing audio: {audio_path}")
    wav, sr = torchaudio.load(audio_path)
    wav = convert_audio(wav, sr, model.sample_rate, model.channels)
    wav = wav.to(device)

    # Extract semantic tokens
    semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
    semantic_tokens = tokenizer.get_token(semantic_vectors)

    # Extract audio codes
    with torch.no_grad():
        encoded_frames = model.encode(wav.unsqueeze(0))
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()

    # Save prompt
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{output_name}.npz")
    np.savez(
        output_path,
        fine_prompt=codes.cpu().numpy(),
        coarse_prompt=codes[:2, :].cpu().numpy(),
        semantic_prompt=semantic_tokens.cpu().numpy()
    )

    print(f"\nVoice cloned and saved to: {output_path}")
    return output_path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Bark CLI - Text-to-Speech with Voice Cloning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate basic audio
  python bark_cli.py generate "Hello world" -o output.wav

  # Generate with specific voice
  python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o hola.wav

  # Generate with custom audio settings
  python bark_cli.py generate "Hello" -v en_speaker_0 -o output.wav --sample-rate 44100 --bits 16 --channels mono

  # Generate without visualization plots
  python bark_cli.py generate "Hello" -o output.wav --no-viz

  # Clone a voice
  python bark_cli.py clone --audio reference.wav --name my_voice

  # List available voices
  python bark_cli.py voices

  # Use small models (faster)
  python bark_cli.py generate "Hello" -o output.wav --small
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate audio from text")
    generate_parser.add_argument("text", help="Text to generate audio for")
    generate_parser.add_argument("-o", "--output", required=True, help="Output file path (.wav)")
    generate_parser.add_argument("-v", "--voice", help="Voice prompt name (e.g., es_speaker_0)")
    generate_parser.add_argument("--sample-rate", type=int, choices=[11025, 22050, 44100],
                                 help="Output sample rate (default: 24000)")
    generate_parser.add_argument("--bits", type=int, choices=[8, 16],
                                 help="Bits per sample (default: float32)")
    generate_parser.add_argument("--channels", choices=["mono", "stereo"],
                                 help="Audio channels (default: mono)")
    generate_parser.add_argument("--text-temp", type=float, default=0.7,
                                 help="Text generation temperature (default: 0.7)")
    generate_parser.add_argument("--waveform-temp", type=float, default=0.7,
                                 help="Waveform generation temperature (default: 0.7)")
    generate_parser.add_argument("--small", action="store_true",
                                 help="Use small models (faster but lower quality)")
    generate_parser.add_argument("--no-viz", action="store_true",
                                 help="Skip generating visualization plots")
    generate_parser.add_argument("--viz-level", choices=["basic", "speech", "full"],
                                 default="basic",
                                 help="Visualization level: basic (4), speech (11), full (19)")

    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone a voice from audio")
    clone_parser.add_argument("--audio", required=True, help="Path to reference audio file")
    clone_parser.add_argument("--name", required=True, help="Name for the cloned voice")
    clone_parser.add_argument("--output-dir", default="bark/assets/prompts",
                              help="Output directory (default: bark/assets/prompts)")

    # Voices command
    subparsers.add_parser("voices", help="List available voices")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    print_header()

    if args.command == "generate":
        generate_audio_cli(
            text=args.text,
            output=args.output,
            voice=args.voice,
            sample_rate=args.sample_rate,
            bits=args.bits,
            channels=args.channels,
            text_temp=args.text_temp,
            waveform_temp=args.waveform_temp,
            small_models=args.small,
            no_viz=args.no_viz,
        )

    elif args.command == "clone":
        clone_voice_cli(
            audio_path=args.audio,
            output_name=args.name,
            output_dir=args.output_dir,
        )

    elif args.command == "voices":
        print_available_voices()


if __name__ == "__main__":
    main()
