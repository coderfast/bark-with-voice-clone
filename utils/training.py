"""
Shared training utilities for Bark fine-tuning notebooks.

This module contains common functions and classes used across
train_semantic.ipynb, train_coarse.ipynb, and train_fine.ipynb.
"""

import gc
import hashlib
import json
import math
import os
import re
from typing import Optional, Tuple, Dict, Any, List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
from tqdm.auto import tqdm
from encodec.utils import convert_audio
from transformers import BertTokenizer
from huggingface_hub import hf_hub_download

from bark.generation import (
    SEMANTIC_RATE_HZ,
    SEMANTIC_VOCAB_SIZE,
    CODEBOOK_SIZE,
    N_COARSE_CODEBOOKS,
    N_FINE_CODEBOOKS,
    COARSE_RATE_HZ,
    SAMPLE_RATE,
)

CHANNELS = 1


# Constants
CONTEXT_WINDOW_SIZE = 1024
MAX_SEMANTIC_LEN = 256
MAX_COARSE_LEN = 768
MAX_TEXT_LEN = 256

TEXT_ENCODING_OFFSET = 10_048
SEMANTIC_PAD_TOKEN = 10_000
TEXT_PAD_TOKEN = 129_595
SEMANTIC_INFER_TOKEN = 129_599

COARSE_SEMANTIC_PAD_TOKEN = 12_048
COARSE_INFER_TOKEN = 12_050


# Model paths
REMOTE_MODEL_PATHS = {
    "text_small": {
        "repo_id": "suno/bark",
        "file_name": "text.pt",
        "checksum": "b3e42bcbab23b688355cd44128c4cdd3",
    },
    "coarse_small": {
        "repo_id": "suno/bark",
        "file_name": "coarse.pt",
        "checksum": "5fe964825e3b0321f9d5f3857b89194d",
    },
    "fine_small": {
        "repo_id": "suno/bark",
        "file_name": "fine.pt",
        "checksum": "5428d1befe05be2ba32195496e58dc90",
    },
    "text": {
        "repo_id": "suno/bark",
        "file_name": "text_2.pt",
        "checksum": "54afa89d65e318d4f5f80e8e8799026a",
    },
    "coarse": {
        "repo_id": "suno/bark",
        "file_name": "coarse_2.pt",
        "checksum": "8a98094e5e3a255a5c9c0ab7efe8fd28",
    },
    "fine": {
        "repo_id": "suno/bark",
        "file_name": "fine_2.pt",
        "checksum": "59d184ed44e3650774a2f0503a48a97b",
    },
}

USE_SMALL_MODELS = os.environ.get("SERP_USE_SMALL_MODELS", "").lower() in ("1", "true", "yes")

default_cache_dir = os.path.join(os.path.expanduser("~"), ".cache")
CACHE_DIR = os.path.join(os.getenv("XDG_CACHE_HOME", default_cache_dir), "serp", "bark_v0")


def _clear_cuda_cache() -> None:
    """Clear CUDA cache if available."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _md5(fname: str) -> str:
    """Compute MD5 hash of a file.

    Args:
        fname: Path to file

    Returns:
        MD5 hash as hex string
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _download(from_hf_path: str, file_name: str, to_local_path: str) -> None:
    """Download a file from HuggingFace Hub.

    Args:
        from_hf_path: HuggingFace repository ID
        file_name: Name of file in repository
        to_local_path: Local path to save file
    """
    to_local_path = to_local_path.replace("\\", "/")
    path = '/'.join(to_local_path.split("/")[:-1])
    os.makedirs(path, exist_ok=True)
    hf_hub_download(repo_id=from_hf_path, filename=file_name, local_dir=path)
    os.replace(os.path.join(path, file_name), to_local_path)


def _tokenize(tokenizer: BertTokenizer, text: str) -> List[int]:
    """Tokenize text using BERT tokenizer.

    Args:
        tokenizer: BERT tokenizer instance
        text: Text to tokenize

    Returns:
        List of token IDs
    """
    return tokenizer.encode(text, add_special_tokens=False)


def _detokenize(tokenizer: BertTokenizer, enc_text: List[int]) -> str:
    """Detokenize token IDs back to text.

    Args:
        tokenizer: BERT tokenizer instance
        enc_text: List of token IDs

    Returns:
        Decoded text string
    """
    return tokenizer.decode(enc_text)


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace
    """
    return re.sub(r"\s+", " ", text).strip()


def load_filepaths_and_text(filename: str, split: str = "|") -> List[List[str]]:
    """Load filepaths and text from a file.

    Args:
        filename: Path to file containing filepath|text pairs
        split: Delimiter for splitting filepath and text

    Returns:
        List of [filepath, text] pairs
    """
    with open(filename, encoding='utf-8', errors='ignore') as f:
        filepaths_and_text = [line.strip().split(split) for line in f]
        base = os.path.dirname(filename)
        for j in range(len(filepaths_and_text)):
            filepaths_and_text[j][0] = os.path.join(base, filepaths_and_text[j][0])
    return filepaths_and_text


def _flatten_codebooks(arr: np.ndarray, offset_size: int = CODEBOOK_SIZE) -> np.ndarray:
    """Flatten codebook array with offset for interleaving.

    Args:
        arr: Array of shape (n_codebooks, n_steps)
        offset_size: Size of each codebook for offset calculation

    Returns:
        Flattened array with interleaved codebooks
    """
    assert len(arr.shape) == 2
    arr = arr.copy()
    if offset_size is not None:
        for n in range(1, arr.shape[0]):
            arr[n, :] += offset_size * n
    flat_arr = arr.ravel("F")
    return flat_arr


def _get_duration(wav: torch.Tensor, sr: int) -> float:
    """Get duration of audio tensor in seconds.

    Args:
        wav: Audio tensor
        sr: Sample rate

    Returns:
        Duration in seconds
    """
    return wav.shape[1] / sr


def _load_model(
    ckpt_path: str,
    device: torch.device,
    use_small: bool = False,
    model_type: str = "text"
) -> Any:
    """Load a Bark model from checkpoint.

    Args:
        ckpt_path: Path to checkpoint file
        device: Device to load model onto
        use_small: Whether to use small model
        model_type: Type of model ("text", "coarse", or "fine")

    Returns:
        Loaded model (and tokenizer for text model)
    """
    from bark.model import GPTConfig, GPT
    from bark.model_fine import FineGPT, FineGPTConfig

    if model_type == "text":
        ConfigClass = GPTConfig
        ModelClass = GPT
    elif model_type == "coarse":
        ConfigClass = GPTConfig
        ModelClass = GPT
    elif model_type == "fine":
        ConfigClass = FineGPTConfig
        ModelClass = FineGPT
    else:
        raise NotImplementedError()

    model_key = f"{model_type}_small" if use_small or USE_SMALL_MODELS else model_type
    model_info = REMOTE_MODEL_PATHS[model_key]

    if ckpt_path in [None, '']:
        ckpt_path = os.path.join(CACHE_DIR, model_info["file_name"])

    if not os.path.exists(ckpt_path):
        print(f"{model_type} model not found, downloading into `{CACHE_DIR}`.")
        _download(model_info["repo_id"], model_info["file_name"], ckpt_path)

    checkpoint = torch.load(ckpt_path, map_location=device)

    # Check for config.json in same directory as checkpoint
    config_path = os.path.join(os.path.dirname(ckpt_path), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            model_args = json.load(f)
    else:
        model_args = checkpoint["model_args"]

    if "input_vocab_size" not in model_args:
        model_args["input_vocab_size"] = model_args["vocab_size"]
        model_args["output_vocab_size"] = model_args["vocab_size"]
        del model_args["vocab_size"]

    gptconf = ConfigClass(**model_args)
    model = ModelClass(gptconf)

    if checkpoint.get("model", None) is not None:
        state_dict = checkpoint["model"]
    else:
        state_dict = checkpoint

    # Fixup checkpoint
    unwanted_prefix = "_orig_mod."
    for k, v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)

    unwanted_suffixes = [
        "lora_right_weight",
        "lora_left_weight",
        "lora_right_bias",
        "lora_left_bias",
    ]
    for k, v in list(state_dict.items()):
        for suffix in unwanted_suffixes:
            if k.endswith(suffix):
                state_dict.pop(k)

    # Fix lm_heads key format
    if state_dict.get('lm_head.0.weight', None) is not None:
        state_dict['lm_head.weight'] = state_dict.pop('lm_head.0.weight')
    for i in range(7):
        old_key = f'lm_heads.{i}.0.weight'
        new_key = f'lm_heads.{i}.weight'
        if state_dict.get(old_key, None) is not None:
            state_dict[new_key] = state_dict.pop(old_key)

    extra_keys = set(state_dict.keys()) - set(model.state_dict().keys())
    extra_keys = set([k for k in extra_keys if not k.endswith(".attn.bias")])
    missing_keys = set(model.state_dict().keys()) - set(state_dict.keys())
    missing_keys = set([k for k in missing_keys if not k.endswith(".attn.bias")])

    if len(extra_keys) != 0:
        print(f"extra keys found: {extra_keys}")
    if len(missing_keys) != 0:
        raise ValueError(f"missing keys: {missing_keys}")

    model.load_state_dict(state_dict, strict=False)
    n_params = model.get_num_params()
    if checkpoint.get("best_val_loss", None) is not None:
        val_loss = checkpoint["best_val_loss"].item()
        print(f"Loaded {model_type} model with {n_params} params, val_loss={val_loss:.4f}.")

    del checkpoint, state_dict
    _clear_cuda_cache()

    if model_type == "text":
        tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
        return model, tokenizer
    return model


class TtsDataset(torch.utils.data.Dataset):
    """Dataset for TTS training with semantic, coarse, and fine tokens."""

    def __init__(self, opt: Dict[str, Any]):
        """Initialize dataset.

        Args:
            opt: Dictionary with 'path', 'mode', and optionally 'tokenizer'
        """
        self.path = os.path.dirname(opt['path'])
        self.mode = opt['mode']
        self.tokenizer = opt.get('tokenizer')
        self.audiopaths_and_text = load_filepaths_and_text(
            os.path.join(opt['path'], opt['mode'] + '.txt')
        )

    def __getitem__(self, index):
        audiopath_and_text = self.audiopaths_and_text[index]
        audiopath = audiopath_and_text[0]

        if self.tokenizer is not None:
            # Semantic training (text -> semantic)
            text = audiopath_and_text[1]
            input_ids = np.array(_tokenize(self.tokenizer, text)) + TEXT_ENCODING_OFFSET
            input_ids = torch.from_numpy(input_ids).long()
            tokens = np.load(audiopath.replace('.wav', '.npz').replace('wavs', 'tokens'))
            semantic_tokens = torch.from_numpy(tokens['semantic']).long()
            return input_ids, semantic_tokens
        else:
            # Coarse or fine training
            tokens = np.load(audiopath.replace('.wav', '.npz').replace('wavs', 'tokens'))
            if 'semantic' in tokens:
                # Coarse training (semantic -> coarse)
                semantic_tokens = tokens['semantic']
                coarse_tokens = _flatten_codebooks(tokens['coarse'], offset_size=CODEBOOK_SIZE) + SEMANTIC_VOCAB_SIZE
                return torch.from_numpy(semantic_tokens), torch.from_numpy(coarse_tokens)
            else:
                # Fine training (coarse -> fine)
                return torch.from_numpy(tokens['fine'])

    def __len__(self):
        return len(self.audiopaths_and_text)


class TtsCollater:
    """Collater for TTS training batches."""

    def __call__(self, batch):
        # Determine training type based on batch structure
        if len(batch[0]) == 2 and isinstance(batch[0][0], torch.Tensor) and batch[0][0].dim() == 1:
            if batch[0][0].shape[0] > 100:  # Likely text tokens
                return self._collate_semantic(batch)
            else:
                return self._collate_coarse(batch)
        else:
            return self._collate_fine(batch)

    def _collate_semantic(self, batch):
        """Collate for semantic (text -> semantic) training."""
        texts = []
        semantic_tokens = []
        for input_ids, sem_tokens in batch:
            input_ids = F.pad(input_ids, (0, MAX_TEXT_LEN - len(input_ids)), value=TEXT_PAD_TOKEN)
            semantic_history = torch.full((256,), SEMANTIC_PAD_TOKEN, dtype=torch.long)
            input_ids = torch.cat([input_ids, semantic_history, torch.tensor([SEMANTIC_INFER_TOKEN])])
            texts.append(input_ids)
            sem_tokens = sem_tokens[:MAX_SEMANTIC_LEN]
            semantic_tokens.append(F.pad(sem_tokens, (0, MAX_SEMANTIC_LEN - len(sem_tokens)), value=SEMANTIC_PAD_TOKEN))
        return {
            'input_ids': torch.stack(texts).contiguous(),
            'semantic_tokens': torch.stack(semantic_tokens).contiguous()
        }

    def _collate_coarse(self, batch):
        """Collate for coarse (semantic -> coarse) training."""
        semantic_to_coarse_ratio = COARSE_RATE_HZ / SEMANTIC_RATE_HZ * N_COARSE_CODEBOOKS
        semantic_tokens = []
        coarse_tokens = []
        for sem_tokens, coarse_toks in batch:
            if len(sem_tokens) > MAX_SEMANTIC_LEN:
                start_idx = np.random.randint(0, len(sem_tokens) - MAX_SEMANTIC_LEN + 1)
                sem_tokens = sem_tokens[start_idx:start_idx + MAX_SEMANTIC_LEN]
            sem_tokens = F.pad(sem_tokens, (0, MAX_SEMANTIC_LEN - len(sem_tokens)), value=COARSE_SEMANTIC_PAD_TOKEN)
            sem_tokens = torch.cat([sem_tokens, torch.tensor([COARSE_INFER_TOKEN])])
            semantic_tokens.append(sem_tokens)

            start_idx_coarse = int(start_idx * semantic_to_coarse_ratio) if len(sem_tokens) > MAX_SEMANTIC_LEN else 0
            coarse_toks = coarse_toks[start_idx_coarse:start_idx_coarse + MAX_COARSE_LEN]
            coarse_toks = F.pad(coarse_toks, (0, MAX_COARSE_LEN - len(coarse_toks)), value=COARSE_SEMANTIC_PAD_TOKEN)
            coarse_tokens.append(coarse_toks)
        return {
            'semantic_tokens': torch.stack(semantic_tokens).contiguous(),
            'coarse_tokens': torch.stack(coarse_tokens).contiguous()
        }

    def _collate_fine(self, batch):
        """Collate for fine (coarse -> fine) training."""
        max_len = 1024
        fine_tokens = []
        for fine_tokens_ in batch:
            if fine_tokens_.shape[1] > max_len:
                start_idx = np.random.randint(0, fine_tokens_.shape[1] - max_len + 1)
                fine_tokens_ = fine_tokens_[:, start_idx:start_idx + max_len]
            pad_size = max_len - fine_tokens_.shape[1]
            fine_tokens_ = F.pad(fine_tokens_, (0, pad_size), value=CODEBOOK_SIZE)
            fine_tokens_ = fine_tokens_.T
            fine_tokens.append(fine_tokens_)
        return {'fine_tokens': torch.stack(fine_tokens).contiguous()}
