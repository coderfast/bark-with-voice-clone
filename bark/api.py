from typing import Optional, Union, Dict, Any, Literal

import numpy as np
import torch
import torchaudio

from .generation import codec_decode, generate_coarse, generate_fine, generate_text_semantic, SAMPLE_RATE


def text_to_semantic(
    text: str,
    history_prompt: Optional[str] = None,
    temp: float = 0.7,
    silent: bool = False,
) -> np.ndarray:
    """Generate semantic array from text.

    Args:
        text: text to be turned into audio
        history_prompt: history choice for audio cloning
        temp: generation temperature (1.0 more diverse, 0.0 more conservative)
        silent: disable progress bar

    Returns:
        numpy semantic array to be fed into `semantic_to_waveform`
    """
    x_semantic = generate_text_semantic(
        text,
        history_prompt=history_prompt,
        temp=temp,
        silent=silent,
        use_kv_caching=True
    )
    return x_semantic


def semantic_to_waveform(
    semantic_tokens: np.ndarray,
    history_prompt: Optional[str] = None,
    temp: float = 0.7,
    fine_temp: Optional[float] = None,
    silent: bool = False,
    output_full: bool = False,
) -> Union[np.ndarray, tuple]:
    """Generate audio array from semantic input.

    Args:
        semantic_tokens: semantic token output from `text_to_semantic`
        history_prompt: history choice for audio cloning
        temp: generation temperature (1.0 more diverse, 0.0 more conservative)
        fine_temp: temperature for fine generation (defaults to 0.5 if None)
        silent: disable progress bar
        output_full: return full generation to be used as a history prompt

    Returns:
        If output_full is False: numpy audio array at sample frequency 24khz
        If output_full is True: tuple of (full_generation dict, audio array)
    """
    coarse_tokens = generate_coarse(
        semantic_tokens,
        history_prompt=history_prompt,
        temp=temp,
        silent=silent,
        use_kv_caching=True
    )
    fine_tokens = generate_fine(
        coarse_tokens,
        history_prompt=history_prompt,
        temp=fine_temp if fine_temp is not None else 0.5,
    )
    audio_arr = codec_decode(fine_tokens)
    if output_full:
        full_generation = {
            "semantic_prompt": semantic_tokens,
            "coarse_prompt": coarse_tokens,
            "fine_prompt": fine_tokens,
        }
        return full_generation, audio_arr
    return audio_arr


def save_as_prompt(filepath: str, full_generation: Dict[str, Any]) -> None:
    """Save a full generation as a prompt file for reuse.

    Args:
        filepath: path to save the prompt file (must end with .npz)
        full_generation: dictionary containing 'semantic_prompt', 'coarse_prompt', and 'fine_prompt'

    Raises:
        ValueError: if filepath doesn't end with .npz or required keys are missing
        TypeError: if full_generation is not a dict
    """
    if not filepath.endswith(".npz"):
        raise ValueError(f"filepath must end with .npz, got: {filepath}")
    if not isinstance(full_generation, dict):
        raise TypeError(f"full_generation must be a dict, got: {type(full_generation)}")
    required_keys = ["semantic_prompt", "coarse_prompt", "fine_prompt"]
    for key in required_keys:
        if key not in full_generation:
            raise ValueError(f"full_generation must contain key '{key}'")
    np.savez(filepath, **full_generation)


def _resample_audio(
    audio: np.ndarray,
    source_sr: int,
    target_sr: int
) -> np.ndarray:
    """Resample audio to target sample rate.

    Args:
        audio: Audio array (1D for mono, 2D for stereo)
        source_sr: Source sample rate
        target_sr: Target sample rate

    Returns:
        Resampled audio array
    """
    if source_sr == target_sr:
        return audio

    # Convert to torch tensor
    if audio.ndim == 1:
        audio_tensor = torch.from_numpy(audio).unsqueeze(0)
    else:
        audio_tensor = torch.from_numpy(audio)

    # Resample
    resampled = torchaudio.functional.resample(audio_tensor, source_sr, target_sr)

    # Convert back to numpy
    return resampled.numpy()


def _convert_channels(
    audio: np.ndarray,
    target_channels: Literal["mono", "stereo"]
) -> np.ndarray:
    """Convert audio to target channel configuration.

    Args:
        audio: Audio array (1D for mono, 2D for stereo)
        target_channels: Target channels ("mono" or "stereo")

    Returns:
        Converted audio array
    """
    if target_channels == "mono":
        if audio.ndim == 1:
            return audio
        # Average channels to mono
        return np.mean(audio, axis=0)
    else:  # stereo
        if audio.ndim == 2 and audio.shape[0] == 2:
            return audio
        # Convert mono to stereo by duplicating
        if audio.ndim == 1:
            return np.stack([audio, audio])
        # If more than 2 channels, take first 2
        return audio[:2]


def _convert_bit_depth(
    audio: np.ndarray,
    bits_per_sample: int
) -> np.ndarray:
    """Convert audio to target bit depth.

    Args:
        audio: Audio array (float32 normalized to [-1, 1])
        bits_per_sample: Target bits per sample (8 or 16)

    Returns:
        Converted audio array
    """
    if bits_per_sample == 8:
        # Convert to 8-bit unsigned (0-255)
        audio_8bit = ((audio + 1) * 127.5).astype(np.uint8)
        return audio_8bit
    elif bits_per_sample == 16:
        # Convert to 16-bit signed (-32768 to 32767)
        audio_16bit = (audio * 32767).astype(np.int16)
        return audio_16bit
    else:
        raise ValueError(f"bits_per_sample must be 8 or 16, got {bits_per_sample}")


def generate_audio(
    text: str,
    history_prompt: Optional[str] = None,
    text_temp: float = 0.7,
    waveform_temp: float = 0.7,
    fine_temp: Optional[float] = None,
    silent: bool = False,
    output_full: bool = False,
    sample_rate: Optional[int] = None,
    bits_per_sample: Optional[int] = None,
    channels: Optional[Literal["mono", "stereo"]] = None,
) -> Union[np.ndarray, tuple]:
    """Generate audio array from input text.

    Args:
        text: text to be turned into audio
        history_prompt: history choice for audio cloning
        text_temp: generation temperature (1.0 more diverse, 0.0 more conservative)
        waveform_temp: generation temperature (1.0 more diverse, 0.0 more conservative)
        fine_temp: temperature for fine generation (defaults to 0.5 if None)
        silent: disable progress bar
        output_full: return full generation to be used as a history prompt
        sample_rate: Output sample rate (11025, 22050, 44100, or None for 24000)
        bits_per_sample: Output bit depth (8 or 16, or None for float32)
        channels: Output channels ("mono" or "stereo", or None for original)

    Returns:
        If output_full is False: numpy audio array
        If output_full is True: tuple of (full_generation dict, audio array)
    """
    semantic_tokens = text_to_semantic(
        text,
        history_prompt=history_prompt,
        temp=text_temp,
        silent=silent,
    )
    out = semantic_to_waveform(
        semantic_tokens,
        history_prompt=history_prompt,
        temp=waveform_temp,
        fine_temp=fine_temp,
        silent=silent,
        output_full=output_full,
    )

    if output_full:
        full_generation, audio_arr = out
    else:
        audio_arr = out

    # Apply audio transformations in correct order
    # 1. Resample first (on float32 audio)
    if sample_rate is not None and sample_rate != SAMPLE_RATE:
        audio_arr = _resample_audio(audio_arr, SAMPLE_RATE, sample_rate)

    # 2. Convert channels
    if channels is not None:
        audio_arr = _convert_channels(audio_arr, channels)

    # 3. Convert bit depth last
    if bits_per_sample is not None:
        audio_arr = _convert_bit_depth(audio_arr, bits_per_sample)

    if output_full:
        return full_generation, audio_arr
    return audio_arr


def save_audio(
    filepath: str,
    audio: np.ndarray,
    sample_rate: Optional[int] = None,
    bits_per_sample: Optional[int] = None,
    channels: Optional[Literal["mono", "stereo"]] = None,
    source_sample_rate: int = SAMPLE_RATE,
) -> None:
    """Save audio array to file with specified format.

    Args:
        filepath: Output file path (.wav)
        audio: Audio array (float32 normalized to [-1, 1])
        sample_rate: Output sample rate (11025, 22050, 44100, or None for source rate)
        bits_per_sample: Bit depth (8 or 16, or None for float32)
        channels: Channels ("mono" or "stereo", or None for original)
        source_sample_rate: Source sample rate of the audio array
    """
    import scipy.io.wavfile as wavfile

    # Determine effective sample rate
    effective_sr = sample_rate if sample_rate is not None else source_sample_rate

    # Apply transformations in correct order
    # 1. Resample first (on float32 audio)
    if sample_rate is not None and sample_rate != source_sample_rate:
        audio = _resample_audio(audio, source_sample_rate, sample_rate)

    # 2. Convert channels
    if channels is not None:
        audio = _convert_channels(audio, channels)

    # 3. Convert bit depth last
    if bits_per_sample is not None:
        audio = _convert_bit_depth(audio, bits_per_sample)

    # Save file
    wavfile.write(filepath, effective_sr, audio)
