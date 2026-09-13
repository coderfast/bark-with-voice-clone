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


def save_audio_with_visualizations(
    filepath: str,
    audio: np.ndarray,
    sample_rate: Optional[int] = None,
    bits_per_sample: Optional[int] = None,
    channels: Optional[Literal["mono", "stereo"]] = None,
    source_sample_rate: int = SAMPLE_RATE,
    visualizations: str = "basic",
) -> dict:
    """Save audio array to file and generate visualization plots.

    Args:
        filepath: Output file path (.wav)
        audio: Audio array (float32 normalized to [-1, 1])
        sample_rate: Output sample rate (11025, 22050, 44100, or None for source rate)
        bits_per_sample: Bit depth (8 or 16, or None for float32)
        channels: Channels ("mono" or "stereo", or None for original)
        source_sample_rate: Source sample rate of the audio array
        visualizations: Level of visualizations to generate:
            - "basic": 4 core visualizations (wave, pitch, sweep, specgram)
            - "full": all 19 visualizations
            - "speech": 11 speech-focused visualizations
            - list: explicit list of visualization names

    Returns:
        Dictionary with 'audio' path and visualization paths
    """
    import os
    from utils.audio_visualizer import (
        generate_all_visualizations, generate_waveform, generate_pitch,
        generate_sweep, generate_spectrogram, generate_spectral_flatness,
        generate_zero_crossing_rate, generate_cqt_spectrogram,
        generate_chromagram, generate_self_similarity, generate_lpc_spectrum,
        generate_spectrogram_wide_narrow,
    )

    # Save audio file
    save_audio(filepath, audio, sample_rate, bits_per_sample, channels, source_sample_rate)

    # Determine effective sample rate for visualization
    effective_sr = sample_rate if sample_rate is not None else source_sample_rate

    # Apply same transformations for visualization (before bit depth conversion)
    audio_viz = audio.copy()
    if sample_rate is not None and sample_rate != source_sample_rate:
        audio_viz = _resample_audio(audio_viz, source_sample_rate, sample_rate)
    if channels is not None:
        audio_viz = _convert_channels(audio_viz, channels)

    # Convert to mono for visualization
    if audio_viz.ndim > 1:
        audio_mono = np.mean(audio_viz, axis=0)
    else:
        audio_mono = audio_viz

    # Generate visualizations in same directory as audio
    output_dir = os.path.dirname(filepath) or '.'
    base_name = os.path.splitext(os.path.basename(filepath))[0]

    # Determine which visualizations to generate
    if visualizations == "basic":
        viz_results = generate_all_visualizations(
            audio=audio_mono, sample_rate=effective_sr,
            output_path=output_dir, prefix=base_name,
        )
    elif visualizations == "speech":
        viz_results = generate_all_visualizations(
            audio=audio_mono, sample_rate=effective_sr,
            output_path=output_dir, prefix=base_name,
        )
        # Add speech-specific visualizations
        try:
            from utils.speech_analyzer import (
                generate_mel_spectrogram, generate_mfcc, generate_formants,
                generate_pitch_voicing, generate_intensity, generate_jitter_shimmer,
                generate_hnr,
            )
            p = os.path.join(output_dir, f"{base_name}_mel.png")
            generate_mel_spectrogram(audio_mono, effective_sr, p)
            viz_results['mel'] = p
            p = os.path.join(output_dir, f"{base_name}_mfcc.png")
            generate_mfcc(audio_mono, effective_sr, p)
            viz_results['mfcc'] = p
            p = os.path.join(output_dir, f"{base_name}_formants.png")
            generate_formants(audio_mono, effective_sr, p)
            viz_results['formants'] = p
            p = os.path.join(output_dir, f"{base_name}_pitch_voiced.png")
            generate_pitch_voicing(audio_mono, effective_sr, p)
            viz_results['pitch_voiced'] = p
            p = os.path.join(output_dir, f"{base_name}_intensity.png")
            generate_intensity(audio_mono, effective_sr, p)
            viz_results['intensity'] = p
            p = os.path.join(output_dir, f"{base_name}_jitter_shimmer.png")
            generate_jitter_shimmer(audio_mono, effective_sr, p)
            viz_results['jitter_shimmer'] = p
            p = os.path.join(output_dir, f"{base_name}_hnr.png")
            generate_hnr(audio_mono, effective_sr, p)
            viz_results['hnr'] = p
        except ImportError:
            pass
    elif visualizations == "full":
        # Generate all basic visualizations
        viz_results = generate_all_visualizations(
            audio=audio_mono, sample_rate=effective_sr,
            output_path=output_dir, prefix=base_name,
        )
        # Add speech-specific
        try:
            from utils.speech_analyzer import (
                generate_mel_spectrogram, generate_mfcc, generate_formants,
                generate_pitch_voicing, generate_intensity, generate_jitter_shimmer,
                generate_hnr,
            )
            for name, func in [
                ('mel', generate_mel_spectrogram),
                ('mfcc', generate_mfcc),
                ('formants', generate_formants),
                ('pitch_voiced', generate_pitch_voicing),
                ('intensity', generate_intensity),
                ('jitter_shimmer', generate_jitter_shimmer),
                ('hnr', generate_hnr),
            ]:
                p = os.path.join(output_dir, f"{base_name}_{name}.png")
                func(audio_mono, effective_sr, p)
                viz_results[name] = p
        except ImportError:
            pass
        # Add audio_visualizer extended
        try:
            for name, func in [
                ('flatness', generate_spectral_flatness),
                ('zcr', generate_zero_crossing_rate),
                ('cqt', generate_cqt_spectrogram),
                ('chroma', generate_chromagram),
                ('selfsim', generate_self_similarity),
                ('lpc', generate_lpc_spectrum),
                ('spec_wb_nb', generate_spectrogram_wide_narrow),
            ]:
                p = os.path.join(output_dir, f"{base_name}_{name}.png")
                func(audio_mono, effective_sr, p)
                viz_results[name] = p
        except ImportError:
            pass
    elif isinstance(visualizations, list):
        viz_results = {}
        # Map names to functions
        all_funcs = {
            'wave': lambda a, sr, p: generate_waveform(a, sr, p),
            'pitch': lambda a, sr, p: generate_pitch(a, sr, p),
            'sweep': lambda a, sr, p: generate_sweep(a, sr, p),
            'specgram': lambda a, sr, p: generate_spectrogram(a, sr, p),
            'flatness': lambda a, sr, p: generate_spectral_flatness(a, sr, p),
            'zcr': lambda a, sr, p: generate_zero_crossing_rate(a, sr, p),
            'cqt': lambda a, sr, p: generate_cqt_spectrogram(a, sr, p),
            'chroma': lambda a, sr, p: generate_chromagram(a, sr, p),
            'selfsim': lambda a, sr, p: generate_self_similarity(a, sr, p),
            'lpc': lambda a, sr, p: generate_lpc_spectrum(a, sr, p),
            'spec_wb_nb': lambda a, sr, p: generate_spectrogram_wide_narrow(a, sr, p),
        }
        # Add speech analyzer functions
        try:
            from utils.speech_analyzer import (
                generate_mel_spectrogram, generate_mfcc, generate_formants,
                generate_pitch_voicing, generate_intensity, generate_jitter_shimmer,
                generate_hnr,
            )
            all_funcs.update({
                'mel': generate_mel_spectrogram,
                'mfcc': generate_mfcc,
                'formants': generate_formants,
                'pitch_voiced': generate_pitch_voicing,
                'intensity': generate_intensity,
                'jitter_shimmer': generate_jitter_shimmer,
                'hnr': generate_hnr,
            })
        except ImportError:
            pass

        for name in visualizations:
            if name in all_funcs:
                p = os.path.join(output_dir, f"{base_name}_{name}.png")
                try:
                    all_funcs[name](audio_mono, effective_sr, p)
                    viz_results[name] = p
                except Exception:
                    pass
    else:
        viz_results = generate_all_visualizations(
            audio=audio_mono, sample_rate=effective_sr,
            output_path=output_dir, prefix=base_name,
        )

    return {'audio': filepath, **viz_results}
