import contextlib
import gc
import hashlib
import os
import re
import json
from typing import Optional, Dict, Any, Union

from encodec import EncodecModel
import funcy
import logging
import numpy as np
from scipy.special import softmax
import torch
import torch.nn.functional as F
import tqdm
from transformers import BertTokenizer
from huggingface_hub import hf_hub_download

from .model import GPTConfig, GPT
from .model_fine import FineGPT, FineGPTConfig

if (
    torch.cuda.is_available() and
    hasattr(torch.cuda, "amp") and
    hasattr(torch.cuda.amp, "autocast") and
    hasattr(torch.cuda, "is_bf16_supported") and
    torch.cuda.is_bf16_supported()
):
    autocast = funcy.partial(torch.cuda.amp.autocast, dtype=torch.bfloat16)
else:
    @contextlib.contextmanager
    def autocast():
        yield


# hold models in global scope to lazy load
models: Dict[str, Any] = {}
models_devices: Dict[str, str] = {}


# Audio and model constants
SEMANTIC_RATE_HZ = 49.9  # Semantic token rate in Hz (one token per ~20ms)
SEMANTIC_VOCAB_SIZE = 10_000  # Number of semantic tokens (HuBERT quantization vocabulary)

CODEBOOK_SIZE = 1024  # Size of each EnCodec codebook (10 bits per codebook entry)
N_COARSE_CODEBOOKS = 2  # Number of codebooks used in coarse generation
N_FINE_CODEBOOKS = 8  # Total number of codebooks in EnCodec (2 coarse + 6 fine)
COARSE_RATE_HZ = 75  # Coarse token rate in Hz

SAMPLE_RATE = 24_000  # Output audio sample rate in Hz


logger = logging.getLogger(__name__)


CUR_PATH = os.path.dirname(os.path.abspath(__file__))


default_cache_dir = os.path.join(os.path.expanduser("~"), ".cache")
CACHE_DIR = os.path.join(os.getenv("XDG_CACHE_HOME", default_cache_dir), "serp", "bark_v0")


def _str_to_bool(value: str) -> bool:
    """Convert a string environment variable to boolean."""
    return value.lower() in ("1", "true", "yes")


USE_SMALL_MODELS = _str_to_bool(os.environ.get("SERP_USE_SMALL_MODELS", "false"))
GLOBAL_ENABLE_MPS = _str_to_bool(os.environ.get("SERP_ENABLE_MPS", "false"))
OFFLOAD_CPU = _str_to_bool(os.environ.get("SERP_OFFLOAD_CPU", "false"))


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


def _apply_top_k_top_p(
    logits: torch.Tensor, top_k: Optional[int], top_p: Optional[float]
) -> torch.Tensor:
    """Apply top-k and/or top-p (nucleus) sampling to logits.

    Args:
        logits: Raw logits tensor
        top_k: If specified, keep only top k values
        top_p: If specified, keep smallest set of values with cumulative probability >= top_p

    Returns:
        Filtered logits tensor
    """
    if top_p is not None:
        original_device = logits.device
        logits_np = logits.detach().cpu().type(torch.float32).numpy()
        sorted_indices = np.argsort(logits_np)[::-1]
        sorted_logits = logits_np[sorted_indices]
        cumulative_probs = np.cumsum(softmax(sorted_logits))
        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[1:] = sorted_indices_to_remove[:-1].copy()
        sorted_indices_to_remove[0] = False
        logits_np[sorted_indices[sorted_indices_to_remove]] = -np.inf
        logits = torch.from_numpy(logits_np).to(original_device)
    if top_k is not None:
        v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
        logits[logits < v[-1]] = -float("Inf")
    return logits


def _safe_multinomial(probs: torch.Tensor, num_samples: int = 1) -> torch.Tensor:
    """Sample from multinomial distribution, working around MPS bug.

    The multinomial function is bugged on MPS devices, so we shuttle to CPU if necessary.
    """
    inf_device = probs.device
    if probs.device.type == "mps":
        probs = probs.to("cpu")
    result = torch.multinomial(probs, num_samples=num_samples)
    return result.to(inf_device)


def _ensure_model_loaded(model_type: str) -> None:
    """Ensure the specified model is loaded, calling preload_models() if needed."""
    global models
    if model_type not in models:
        preload_models()


def _get_model_and_device(model_type: str) -> tuple:
    """Get model and device, handling CPU offloading if enabled.

    Returns:
        Tuple of (model, device)
    """
    global models_devices
    model = models[model_type]
    if OFFLOAD_CPU:
        model.to(models_devices[model_type])
    device = next(model.parameters()).device
    return model, device


if not hasattr(torch.nn.functional, 'scaled_dot_product_attention') and torch.cuda.is_available():
    logger.warning(
        "torch version does not support flash attention. You will get faster" +
        " inference speed by upgrade torch to newest nightly version."
    )


def _string_md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def _md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _get_ckpt_path(model_type, use_small=False, path=None):
    model_key = f"{model_type}_small" if use_small or USE_SMALL_MODELS else model_type
    model_name = REMOTE_MODEL_PATHS[model_key]["file_name"]
    if path is None:
        path = CACHE_DIR
    return os.path.join(path, f"{model_name}")


def _grab_best_device(use_gpu=True):
    if torch.cuda.device_count() > 0 and use_gpu:
        device = "cuda"
    elif torch.backends.mps.is_available() and use_gpu and GLOBAL_ENABLE_MPS:
        device = "mps"
    else:
        device = "cpu"
    return device


def _download(from_hf_path, file_name, to_local_path):
    """Download a file from HuggingFace Hub.

    Args:
        from_hf_path: HuggingFace repository ID (e.g., "suno/bark")
        file_name: Name of file in repository
        to_local_path: Local path to save file
    """
    to_local_path = to_local_path.replace("\\", "/")
    path = '/'.join(to_local_path.split("/")[:-1])
    os.makedirs(path, exist_ok=True)
    hf_hub_download(repo_id=from_hf_path, filename=file_name, local_dir=path)
    os.replace(os.path.join(path, file_name), to_local_path)

class InferenceContext:
    """Context manager for controlling cuDNN benchmarking during inference.

    Disables cuDNN benchmarking by default since inputs may vary in length,
    which would reduce the benefit of benchmarking.
    """

    def __init__(self, benchmark=False):
        self._chosen_cudnn_benchmark = benchmark
        self._cudnn_benchmark = None

    def __enter__(self):
        self._cudnn_benchmark = torch.backends.cudnn.benchmark
        torch.backends.cudnn.benchmark = self._chosen_cudnn_benchmark

    def __exit__(self, exc_type, exc_value, exc_traceback):
        torch.backends.cudnn.benchmark = self._cudnn_benchmark


if torch.cuda.is_available():
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True


@contextlib.contextmanager
def _inference_mode():
    with InferenceContext(), torch.inference_mode(), torch.no_grad(), autocast():
        yield


def _clear_cuda_cache():
    """Clear CUDA cache and synchronize to free GPU memory."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def clean_models(model_key=None):
    """Remove models from memory and clear cache.

    Args:
        model_key: Specific model to remove. If None, removes all models.
    """
    global models
    model_keys = [model_key] if model_key is not None else models.keys()
    for k in model_keys:
        if k in models:
            del models[k]
    _clear_cuda_cache()
    gc.collect()


def _load_model(ckpt_path, device, use_small=False, model_type="text"):
    """Load a Bark model from checkpoint file.

    Args:
        ckpt_path: Path to checkpoint file (.pt, .ckpt, or .bin)
        device: Device to load model onto ('cpu', 'cuda', etc.)
        use_small: Whether to use small model variant
        model_type: Type of model ("text", "coarse", or "fine")

    Returns:
        For text model: dict with 'model' and 'tokenizer' keys
        For other models: the model object directly

    Raises:
        NotImplementedError: If model_type is not one of "text", "coarse", "fine"
    """
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
    if not os.path.exists(ckpt_path):
        logger.info(f"{model_type} model not found, downloading into `{CACHE_DIR}`.")
        _download(model_info["repo_id"], model_info["file_name"], ckpt_path)
    checkpoint = torch.load(ckpt_path, map_location=device)
    # this is a hack
    # check if config.json is in the same directory as the checkpoint
    # if so, load it
    # otherwise, assume it's in the checkpoint
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
    # fixup checkpoint
    unwanted_prefix = "_orig_mod."
    for k, v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix) :]] = state_dict.pop(k)
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
    # fixup lm_heads key format for backward compatibility
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
        logger.warning(f"extra keys found: {extra_keys}")
    if len(missing_keys) != 0:
        raise ValueError(f"missing keys: {missing_keys}")
    model.load_state_dict(state_dict, strict=False)
    n_params = model.get_num_params()
    if checkpoint.get("best_val_loss", None) is not None:
        val_loss = checkpoint["best_val_loss"].item()
        logger.info(f"model loaded: {round(n_params/1e6,1)}M params, {round(val_loss,3)} loss")
    model.eval()
    model.to(device)
    del checkpoint, state_dict
    _clear_cuda_cache()
    if model_type == "text":
        tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
        return {
            "model": model,
            "tokenizer": tokenizer,
        }
    return model


def _load_codec_model(device):
    """Load the EnCodec audio codec model.

    Args:
        device: Device to load model onto

    Returns:
        EnCodec model instance
    """
    model = EncodecModel.encodec_model_24khz()
    model.set_target_bandwidth(6.0)
    model.eval()
    model.to(device)
    _clear_cuda_cache()
    return model


def load_model(use_gpu=True, use_small=False, force_reload=False, model_type="text", path=None):
    """Load a Bark model and cache it globally.

    This function handles model loading, caching, and device management.
    Models are cached in the global `models` dict for reuse.

    Args:
        use_gpu: Whether to use GPU for inference
        use_small: Whether to use small model variant
        force_reload: Force reload even if model is cached
        model_type: Type of model ("text", "coarse", or "fine")
        path: Path to model checkpoint or directory

    Returns:
        Loaded model (dict for text model, model object for others)

    Raises:
        NotImplementedError: If model_type is not supported
    """
    _load_model_f = funcy.partial(_load_model, model_type=model_type, use_small=use_small)
    if model_type not in ("text", "coarse", "fine"):
        raise NotImplementedError()
    global models
    global models_devices
    device = _grab_best_device(use_gpu=use_gpu)
    model_key = f"{model_type}"
    if OFFLOAD_CPU:
        models_devices[model_key] = device
        device = "cpu"
    if model_key not in models or force_reload:
        if path.endswith(".ckpt") or path.endswith(".pt") or path.endswith(".bin"):
            ckpt_path = path
        else:
            ckpt_path = _get_ckpt_path(model_type, use_small=use_small, path=path)
        # clean_models(model_key=model_key)
        model = _load_model_f(ckpt_path, device)
        models[model_key] = model
    if model_type == "text":
        models[model_key]["model"].to(device)
    else:
        models[model_key].to(device)
    return models[model_key]


def load_codec_model(use_gpu=True, force_reload=False):
    """Load the EnCodec audio codec model and cache it globally.

    Args:
        use_gpu: Whether to use GPU for inference
        force_reload: Force reload even if model is cached

    Returns:
        EnCodec model instance
    """
    global models
    global models_devices
    device = _grab_best_device(use_gpu=use_gpu)
    if device == "mps":
        # encodec doesn't support mps
        device = "cpu"
    model_key = "codec"
    if OFFLOAD_CPU:
        models_devices[model_key] = device
        device = "cpu"
    if model_key not in models or force_reload:
        clean_models(model_key=model_key)
        model = _load_codec_model(device)
        models[model_key] = model
    models[model_key].to(device)
    return models[model_key]


def preload_models(
    text_use_gpu=True,
    text_use_small=False,
    text_model_path=None,
    coarse_use_gpu=True,
    coarse_use_small=False,
    coarse_model_path=None,
    fine_use_gpu=True,
    fine_use_small=False,
    fine_model_path=None,
    codec_use_gpu=True,
    force_reload=False,
    path=None,
):
    """Load all necessary models for the Bark TTS pipeline.

    This function loads the text, coarse, fine, and codec models. It's
    recommended to call this once at the start of your application to
    avoid lazy loading delays during generation.

    Args:
        text_use_gpu: Use GPU for text model
        text_use_small: Use small text model variant
        text_model_path: Custom path to text model checkpoint
        coarse_use_gpu: Use GPU for coarse model
        coarse_use_small: Use small coarse model variant
        coarse_model_path: Custom path to coarse model checkpoint
        fine_use_gpu: Use GPU for fine model
        fine_use_small: Use small fine model variant
        fine_model_path: Custom path to fine model checkpoint
        codec_use_gpu: Use GPU for codec model
        force_reload: Force reload all models even if cached
        path: Base path for model checkpoints
    """
    if _grab_best_device() == "cpu" and (
        text_use_gpu or coarse_use_gpu or fine_use_gpu or codec_use_gpu
    ):
        logger.warning("No GPU being used. Careful, inference might be very slow!")
    _ = load_model(
        model_type="text", use_gpu=text_use_gpu, use_small=text_use_small, force_reload=force_reload, path=path if text_model_path is None else text_model_path
    )
    _ = load_model(
        model_type="coarse",
        use_gpu=coarse_use_gpu,
        use_small=coarse_use_small,
        force_reload=force_reload,
        path=path if coarse_model_path is None else coarse_model_path,
    )
    _ = load_model(
        model_type="fine", use_gpu=fine_use_gpu, use_small=fine_use_small, force_reload=force_reload, path=path if fine_model_path is None else fine_model_path
    )
    _ = load_codec_model(use_gpu=codec_use_gpu, force_reload=force_reload)


####
# Generation Functionality
####

def _tokenize(tokenizer, text):
    return tokenizer.encode(text, add_special_tokens=False)


def _detokenize(tokenizer, enc_text):
    return tokenizer.decode(enc_text)


def _normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()

TEXT_ENCODING_OFFSET = 10_048
SEMANTIC_PAD_TOKEN = 10_000
TEXT_PAD_TOKEN = 129_595
SEMANTIC_INFER_TOKEN = 129_599


def generate_text_semantic(
    text,
    history_prompt=None,
    temp=0.7,
    top_k=None,
    top_p=None,
    silent=False,
    min_eos_p=0.2,
    max_gen_duration_s=None,
    allow_early_stop=True,
    use_kv_caching=False,
):
    """Generate semantic tokens from text.

    Args:
        text: Text to generate semantic tokens for
        history_prompt: Optional voice prompt name or path to .npz file
        temp: Temperature for sampling (higher = more diverse)
        top_k: Top-k sampling parameter
        top_p: Nucleus sampling parameter
        silent: Disable progress bar
        min_eos_p: Minimum probability for early stop
        max_gen_duration_s: Maximum generation duration in seconds
        allow_early_stop: Allow early stopping when EOS is detected
        use_kv_caching: Use key-value caching for faster generation

    Returns:
        numpy array of semantic tokens
    """
    assert isinstance(text, str), f"text must be a string, got {type(text)}"
    text = _normalize_whitespace(text)
    assert len(text.strip()) > 0, "text must not be empty or contain only whitespace"
    if history_prompt is not None:
        if history_prompt.endswith(".npz"):
            try:
                semantic_history = np.load(history_prompt)["semantic_prompt"]
            except KeyError:
                semantic_history = np.load(history_prompt)["semantic"]
        else:
            semantic_history = np.load(
                os.path.join(CUR_PATH, "assets", "prompts", f"{history_prompt}.npz")
            )["semantic_prompt"]
        assert (
            isinstance(semantic_history, np.ndarray)
            and len(semantic_history.shape) == 1
            and len(semantic_history) > 0
            and semantic_history.min() >= 0
            and semantic_history.max() <= SEMANTIC_VOCAB_SIZE - 1
        )
    else:
        semantic_history = None
    # load models if not yet exist
    _ensure_model_loaded("text")
    model_container = models["text"]
    model = model_container["model"]
    tokenizer = model_container["tokenizer"]
    encoded_text = np.array(_tokenize(tokenizer, text)) + TEXT_ENCODING_OFFSET
    if OFFLOAD_CPU:
        model.to(models_devices["text"])
    device = next(model.parameters()).device
    if len(encoded_text) > 256:
        p = round((len(encoded_text) - 256) / len(encoded_text) * 100, 1)
        logger.warning(f"warning, text too long, lopping of last {p}%")
        encoded_text = encoded_text[:256]
    encoded_text = np.pad(
        encoded_text,
        (0, 256 - len(encoded_text)),
        constant_values=TEXT_PAD_TOKEN,
        mode="constant",
    )
    if semantic_history is not None:
        semantic_history = semantic_history.astype(np.int64)
        # lop off if history is too long, pad if needed
        semantic_history = semantic_history[-256:]
        semantic_history = np.pad(
            semantic_history,
            (0, 256 - len(semantic_history)),
            constant_values=SEMANTIC_PAD_TOKEN,
            mode="constant",
        )
    else:
        semantic_history = np.array([SEMANTIC_PAD_TOKEN] * 256)
    x = torch.from_numpy(
        np.hstack([
            encoded_text, semantic_history, np.array([SEMANTIC_INFER_TOKEN])
        ]).astype(np.int64)
    )[None]
    assert x.shape[1] == 256 + 256 + 1, f"Input shape mismatch: expected {256 + 256 + 1}, got {x.shape[1]}"
    with _inference_mode():
        x = x.to(device)
        n_tot_steps = 768
        # custom tqdm updates since we don't know when eos will occur
        pbar = tqdm.tqdm(disable=silent, total=100)
        pbar_state = 0
        tot_generated_duration_s = 0
        kv_cache = None
        for n in range(n_tot_steps):
            if use_kv_caching and kv_cache is not None:
                x_input = x[:, [-1]]
            else:
                x_input = x
            logits, kv_cache = model(
                x_input, merge_context=True, use_cache=use_kv_caching, past_kv=kv_cache
            )
            relevant_logits = logits[0, 0, :SEMANTIC_VOCAB_SIZE]
            if allow_early_stop:
                relevant_logits = torch.hstack(
                    (relevant_logits, logits[0, 0, [SEMANTIC_PAD_TOKEN]])  # eos
                )
            relevant_logits = _apply_top_k_top_p(relevant_logits, top_k, top_p)
            probs = F.softmax(relevant_logits / temp, dim=-1)
            item_next = _safe_multinomial(probs, num_samples=1)
            if allow_early_stop and (
                item_next == SEMANTIC_VOCAB_SIZE
                or (min_eos_p is not None and probs[-1] >= min_eos_p)
            ):
                # eos found, so break
                pbar.update(100 - pbar_state)
                break
            x = torch.cat((x, item_next[None]), dim=1)
            tot_generated_duration_s += 1 / SEMANTIC_RATE_HZ
            if max_gen_duration_s is not None and tot_generated_duration_s > max_gen_duration_s:
                pbar.update(100 - pbar_state)
                break
            if n == n_tot_steps - 1:
                pbar.update(100 - pbar_state)
                break
            req_pbar_state = np.min([100, int(round(100 * n / n_tot_steps))])
            if req_pbar_state > pbar_state:
                pbar.update(req_pbar_state - pbar_state)
            pbar_state = req_pbar_state
        pbar.close()
        out = x.detach().cpu().numpy().squeeze()[256 + 256 + 1 :]
    if OFFLOAD_CPU:
        model.to("cpu")
    assert all(0 <= out) and all(out < SEMANTIC_VOCAB_SIZE), "Generated tokens out of valid range"
    _clear_cuda_cache()
    return out


def _flatten_codebooks(arr, offset_size=CODEBOOK_SIZE):
    assert len(arr.shape) == 2, f"Expected 2D array, got {len(arr.shape)}D"
    arr = arr.copy()
    if offset_size is not None:
        for n in range(1, arr.shape[0]):
            arr[n, :] += offset_size * n
    flat_arr = arr.ravel("F")
    return flat_arr


COARSE_SEMANTIC_PAD_TOKEN = 12_048
COARSE_INFER_TOKEN = 12_050


def generate_coarse(
    x_semantic,
    history_prompt=None,
    temp=0.7,
    top_k=None,
    top_p=None,
    silent=False,
    max_coarse_history=630,  # min 60 (faster), max 630 (more context)
    sliding_window_len=60,
    use_kv_caching=False,
):
    """Generate coarse audio codes from semantic tokens.

    Args:
        x_semantic: numpy array of semantic tokens
        history_prompt: Optional voice prompt name or path to .npz file
        temp: Temperature for sampling
        top_k: Top-k sampling parameter
        top_p: Nucleus sampling parameter
        silent: Disable progress bar
        max_coarse_history: Maximum coarse history length (60-630)
        sliding_window_len: Sliding window length for generation
        use_kv_caching: Use key-value caching for faster generation

    Returns:
        numpy array of coarse audio codes with shape (N_COARSE_CODEBOOKS, n_steps)
    """
    assert (
        isinstance(x_semantic, np.ndarray)
        and len(x_semantic.shape) == 1
        and len(x_semantic) > 0
        and x_semantic.min() >= 0
        and x_semantic.max() <= SEMANTIC_VOCAB_SIZE - 1
    )
    assert 60 <= max_coarse_history <= 630, f"max_coarse_history must be between 60 and 630, got {max_coarse_history}"
    assert max_coarse_history + sliding_window_len <= 1024 - 256, "max_coarse_history + sliding_window_len exceeds limit"
    semantic_to_coarse_ratio = COARSE_RATE_HZ / SEMANTIC_RATE_HZ * N_COARSE_CODEBOOKS
    max_semantic_history = int(np.floor(max_coarse_history / semantic_to_coarse_ratio))
    if history_prompt is not None:
        if history_prompt.endswith(".npz"):
            x_history = np.load(history_prompt)
        else:
            x_history = np.load(
                os.path.join(CUR_PATH, "assets", "prompts", f"{history_prompt}.npz")
            )
        try:
            x_semantic_history = x_history["semantic_prompt"]
            x_coarse_history = x_history["coarse_prompt"]
        except KeyError:
            x_semantic_history = x_history["semantic"]
            x_coarse_history = x_history["coarse"]
        assert (
            isinstance(x_semantic_history, np.ndarray)
            and len(x_semantic_history.shape) == 1
            and len(x_semantic_history) > 0
            and x_semantic_history.min() >= 0
            and x_semantic_history.max() <= SEMANTIC_VOCAB_SIZE - 1
            and isinstance(x_coarse_history, np.ndarray)
            and len(x_coarse_history.shape) == 2
            and x_coarse_history.shape[0] == N_COARSE_CODEBOOKS
            and x_coarse_history.shape[-1] >= 0
            and x_coarse_history.min() >= 0
            and x_coarse_history.max() <= CODEBOOK_SIZE - 1
            and (
                round(x_coarse_history.shape[-1] / len(x_semantic_history), 1)
                == round(semantic_to_coarse_ratio / N_COARSE_CODEBOOKS, 1)
            )
        )
        x_coarse_history = _flatten_codebooks(x_coarse_history) + SEMANTIC_VOCAB_SIZE
        # trim histories correctly
        n_semantic_hist_provided = np.min(
            [
                max_semantic_history,
                len(x_semantic_history) - len(x_semantic_history) % 2,
                int(np.floor(len(x_coarse_history) / semantic_to_coarse_ratio)),
            ]
        )
        n_coarse_hist_provided = int(round(n_semantic_hist_provided * semantic_to_coarse_ratio))
        x_semantic_history = x_semantic_history[-n_semantic_hist_provided:].astype(np.int32)
        x_coarse_history = x_coarse_history[-n_coarse_hist_provided:].astype(np.int32)
        # trim for time alignment (sounds better)
        x_coarse_history = x_coarse_history[:-2]
    else:
        x_semantic_history = np.array([], dtype=np.int32)
        x_coarse_history = np.array([], dtype=np.int32)
    # load models if not yet exist
    _ensure_model_loaded("coarse")
    model, device = _get_model_and_device("coarse")
    # start loop
    n_steps = int(
        round(
            np.floor(len(x_semantic) * semantic_to_coarse_ratio / N_COARSE_CODEBOOKS)
            * N_COARSE_CODEBOOKS
        )
    )
    assert n_steps > 0 and n_steps % N_COARSE_CODEBOOKS == 0, f"n_steps must be positive and divisible by {N_COARSE_CODEBOOKS}, got {n_steps}"
    x_semantic = np.hstack([x_semantic_history, x_semantic]).astype(np.int32)
    x_coarse = x_coarse_history.astype(np.int32)
    base_semantic_idx = len(x_semantic_history)
    with _inference_mode():
        x_semantic_in = torch.from_numpy(x_semantic)[None].to(device)
        x_coarse_in = torch.from_numpy(x_coarse)[None].to(device)
        n_window_steps = int(np.ceil(n_steps / sliding_window_len))
        n_step = 0
        for _ in tqdm.tqdm(range(n_window_steps), total=n_window_steps, disable=silent):
            semantic_idx = base_semantic_idx + int(round(n_step / semantic_to_coarse_ratio))
            # pad from right side
            x_in = x_semantic_in[:, np.max([0, semantic_idx - max_semantic_history]) :]
            x_in = x_in[:, :256]
            x_in = F.pad(
                x_in,
                (0, 256 - x_in.shape[-1]),
                "constant",
                COARSE_SEMANTIC_PAD_TOKEN,
            )
            x_in = torch.hstack(
                [
                    x_in,
                    torch.tensor([COARSE_INFER_TOKEN])[None].to(device),
                    x_coarse_in[:, -max_coarse_history:],
                ]
            )
            kv_cache = None
            for _ in range(sliding_window_len):
                if n_step >= n_steps:
                    continue
                is_major_step = n_step % N_COARSE_CODEBOOKS == 0

                if use_kv_caching and kv_cache is not None:
                    x_input = x_in[:, [-1]]
                else:
                    x_input = x_in

                logits, kv_cache = model(x_input, use_cache=use_kv_caching, past_kv=kv_cache)
                logit_start_idx = (
                    SEMANTIC_VOCAB_SIZE + (1 - int(is_major_step)) * CODEBOOK_SIZE
                )
                logit_end_idx = (
                    SEMANTIC_VOCAB_SIZE + (2 - int(is_major_step)) * CODEBOOK_SIZE
                )
                relevant_logits = logits[0, 0, logit_start_idx:logit_end_idx]
                relevant_logits = _apply_top_k_top_p(relevant_logits, top_k, top_p)
                probs = F.softmax(relevant_logits / temp, dim=-1)
                item_next = _safe_multinomial(probs, num_samples=1)
                item_next += logit_start_idx
                x_coarse_in = torch.cat((x_coarse_in, item_next[None]), dim=1)
                x_in = torch.cat((x_in, item_next[None]), dim=1)
                n_step += 1
        del x_semantic_in
    if OFFLOAD_CPU:
        model.to("cpu")
    gen_coarse_arr = x_coarse_in.detach().cpu().numpy().squeeze()[len(x_coarse_history):]
    del x_coarse_in
    assert len(gen_coarse_arr) == n_steps, f"Generated length mismatch: expected {n_steps}, got {len(gen_coarse_arr)}"
    gen_coarse_audio_arr = gen_coarse_arr.reshape(-1, N_COARSE_CODEBOOKS).T - SEMANTIC_VOCAB_SIZE
    for n in range(1, N_COARSE_CODEBOOKS):
        gen_coarse_audio_arr[n, :] -= n * CODEBOOK_SIZE
    _clear_cuda_cache()
    return gen_coarse_audio_arr


def generate_fine(
    x_coarse_gen,
    history_prompt=None,
    temp=0.5,
    silent=True,
):
    """Generate full audio codes from coarse audio codes.

    Args:
        x_coarse_gen: numpy array of coarse audio codes with shape (n_coarse, n_steps)
        history_prompt: Optional voice prompt name or path to .npz file
        temp: Temperature for sampling (None for argmax)
        silent: Disable progress bar

    Returns:
        numpy array of fine audio codes with shape (N_FINE_CODEBOOKS, n_steps)
    """
    assert (
        isinstance(x_coarse_gen, np.ndarray)
        and len(x_coarse_gen.shape) == 2
        and 1 <= x_coarse_gen.shape[0] <= N_FINE_CODEBOOKS - 1
        and x_coarse_gen.shape[1] > 0
        and x_coarse_gen.min() >= 0
        and x_coarse_gen.max() <= CODEBOOK_SIZE - 1
    )
    if history_prompt is not None:
        if history_prompt.endswith(".npz"):
            try:
                x_fine_history = np.load(history_prompt)["fine_prompt"]
            except KeyError:
                x_fine_history = np.load(history_prompt)["fine"]
        else:
            x_fine_history = np.load(
                os.path.join(CUR_PATH, "assets", "prompts", f"{history_prompt}.npz")
            )["fine_prompt"]
        assert (
            isinstance(x_fine_history, np.ndarray)
            and len(x_fine_history.shape) == 2
            and x_fine_history.shape[0] == N_FINE_CODEBOOKS
            and x_fine_history.shape[1] >= 0
            and x_fine_history.min() >= 0
            and x_fine_history.max() <= CODEBOOK_SIZE - 1
        )
    else:
        x_fine_history = None
    n_coarse = x_coarse_gen.shape[0]
    # load models if not yet exist
    _ensure_model_loaded("fine")
    model, device = _get_model_and_device("fine")
    # make input arr
    in_arr = np.vstack(
        [
            x_coarse_gen,
            np.zeros((N_FINE_CODEBOOKS - n_coarse, x_coarse_gen.shape[1]))
            + CODEBOOK_SIZE,  # padding
        ]
    ).astype(np.int32)
    # prepend history if available (max 512)
    if x_fine_history is not None:
        x_fine_history = x_fine_history.astype(np.int32)
        in_arr = np.hstack(
            [
                x_fine_history[:, -512:].astype(np.int32),
                in_arr,
            ]
        )
        n_history = x_fine_history[:, -512:].shape[1]
    else:
        n_history = 0
    n_remove_from_end = 0
    # need to pad if too short (since non-causal model)
    if in_arr.shape[1] < 1024:
        n_remove_from_end = 1024 - in_arr.shape[1]
        in_arr = np.hstack(
            [
                in_arr,
                np.zeros((N_FINE_CODEBOOKS, n_remove_from_end), dtype=np.int32) + CODEBOOK_SIZE,
            ]
        )
    # we can be lazy about fractional loop and just keep overwriting codebooks
    n_loops = np.max([0, int(np.ceil((x_coarse_gen.shape[1] - (1024 - n_history)) / 512))]) + 1
    with _inference_mode():
        in_arr = torch.tensor(in_arr.T).to(device)
        for n in tqdm.tqdm(range(n_loops), disable=silent):
            start_idx = np.min([n * 512, in_arr.shape[0] - 1024])
            start_fill_idx = np.min([n_history + n * 512, in_arr.shape[0] - 512])
            rel_start_fill_idx = start_fill_idx - start_idx
            in_buffer = in_arr[start_idx : start_idx + 1024, :][None]
            for nn in range(n_coarse, N_FINE_CODEBOOKS):
                logits = model(nn, in_buffer)
                if temp is None:
                    relevant_logits = logits[0, rel_start_fill_idx:, :CODEBOOK_SIZE]
                    codebook_preds = torch.argmax(relevant_logits, -1)
                else:
                    relevant_logits = logits[0, :, :CODEBOOK_SIZE] / temp
                    probs = F.softmax(relevant_logits, dim=-1)
                    codebook_preds = torch.hstack(
                        [
                            _safe_multinomial(probs[nnn], num_samples=1)
                            for nnn in range(rel_start_fill_idx, 1024)
                        ]
                    )
                in_buffer[0, rel_start_fill_idx:, nn] = codebook_preds
            # transfer over info into model_in and convert to numpy
            for nn in range(n_coarse, N_FINE_CODEBOOKS):
                in_arr[
                    start_fill_idx : start_fill_idx + (1024 - rel_start_fill_idx), nn
                ] = in_buffer[0, rel_start_fill_idx:, nn]
        gen_fine_arr = in_arr.detach().cpu().numpy().squeeze().T
    if OFFLOAD_CPU:
        model.to("cpu")
    gen_fine_arr = gen_fine_arr[:, n_history:]
    if n_remove_from_end > 0:
        gen_fine_arr = gen_fine_arr[:, :-n_remove_from_end]
    assert gen_fine_arr.shape[-1] == x_coarse_gen.shape[-1], "Output length must match input length"
    _clear_cuda_cache()
    return gen_fine_arr


def codec_decode(fine_tokens):
    """Turn quantized audio codes into audio array using encodec.

    Args:
        fine_tokens: numpy array of fine audio codes

    Returns:
        numpy array of audio samples at 24kHz
    """
    # load models if not yet exist
    _ensure_model_loaded("codec")
    model, device = _get_model_and_device("codec")
    arr = torch.from_numpy(fine_tokens)[None]
    arr = arr.to(device)
    arr = arr.transpose(0, 1)
    emb = model.quantizer.decode(arr)
    out = model.decoder(emb)
    audio_arr = out.detach().cpu().numpy().squeeze()
    if OFFLOAD_CPU:
        model.to("cpu")
    return audio_arr
