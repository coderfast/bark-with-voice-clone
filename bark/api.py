from typing import Optional, Union, Dict, Any

import numpy as np

from .generation import codec_decode, generate_coarse, generate_fine, generate_text_semantic


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


def generate_audio(
    text: str,
    history_prompt: Optional[str] = None,
    text_temp: float = 0.7,
    waveform_temp: float = 0.7,
    fine_temp: Optional[float] = None,
    silent: bool = False,
    output_full: bool = False,
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

    Returns:
        If output_full is False: numpy audio array at sample frequency 24khz
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
        return full_generation, audio_arr
    return out
