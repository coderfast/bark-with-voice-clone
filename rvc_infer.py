"""
RVC (Retrieval-based Voice Conversion) inference module.

This module provides voice conversion capabilities using RVC models.
It requires the Retrieval-based-Voice-Conversion-WebUI repository to be
cloned in the project root directory. If not present, it will be
automatically downloaded using the RVCManager.

Global state:
    This module uses global variables for model state. Call get_vc() first
    to initialize the models before using vc_single().
"""

import os
import sys
import logging
from multiprocessing import cpu_count
from typing import Optional, Tuple, Any

import torch
import numpy as np

logger = logging.getLogger(__name__)

# Setup paths for RVC imports
now_dir = os.getcwd()
if now_dir not in sys.path:
    sys.path.append(now_dir)
rvc_path = os.path.join(now_dir, "Retrieval-based-Voice-Conversion-WebUI")

# Auto-download RVC if not present
try:
    from utils.rvc_manager import RVCManager
    if not RVCManager.is_rvc_installed(rvc_path):
        logger.info("RVC not found. Attempting to download automatically...")
        rvc_path = RVCManager.make_sure_rvc_installed(install_dir=rvc_path)
except ImportError:
    logger.warning("RVCManager not available. Make sure RVC is installed manually.")
except Exception as e:
    logger.warning(f"Could not auto-download RVC: {e}. Make sure RVC is installed.")

if rvc_path not in sys.path:
    sys.path.append(rvc_path)

# Global state for RVC models
# These are initialized by get_vc() and used by vc_single()
device: str = "cpu"
is_half: bool = True
n_spk: int = 0
tgt_sr: int = 0
net_g: Any = None
vc: Any = None
cpt: dict = {}
hubert_model: Any = None


def load_audio(file: str, sr: int) -> np.ndarray:
    """Load audio file and resample to target sample rate.

    Args:
        file: Path to audio file
        sr: Target sample rate

    Returns:
        numpy array of audio samples

    Raises:
        RuntimeError: If audio loading fails
    """
    try:
        import ffmpeg
        # Strip whitespace and quotes from file path
        file = file.strip(" ").strip('"').strip("\n").strip('"').strip(" ")
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="f32le", acodec="pcm_f32le", ac=1, ar=sr)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")

    return np.frombuffer(out, np.float32).flatten()


class Config:
    """Configuration for RVC inference based on GPU capabilities."""

    def __init__(self, device: str, is_half: bool):
        self.device = device
        self.is_half = is_half
        self.n_cpu = 0
        self.gpu_name = None
        self.gpu_mem = None
        self.x_pad, self.x_query, self.x_center, self.x_max = self.device_config()

    def device_config(self) -> Tuple[int, int, int, int]:
        """Configure device settings based on GPU capabilities.

        Returns:
            Tuple of (x_pad, x_query, x_center, x_max) parameters
        """
        if torch.cuda.is_available():
            i_device = int(self.device.split(":")[-1])
            self.gpu_name = torch.cuda.get_device_name(i_device)
            # Force single precision for 16-series, 10-series, and P40 GPUs
            if (
                ("16" in self.gpu_name and "V100" not in self.gpu_name.upper())
                or "P40" in self.gpu_name.upper()
                or "1060" in self.gpu_name
                or "1070" in self.gpu_name
                or "1080" in self.gpu_name
            ):
                logger.info("16-series/10-series GPU and P40: forcing single precision")
                self.is_half = False
            else:
                self.gpu_name = None
            self.gpu_mem = int(
                torch.cuda.get_device_properties(i_device).total_memory
                / 1024
                / 1024
                / 1024
                + 0.4
            )
        elif torch.backends.mps.is_available():
            logger.info("No NVIDIA GPU found, using MPS for inference")
            self.device = "mps"
        else:
            logger.info("No NVIDIA GPU found, using CPU for inference")
            self.device = "cpu"
            self.is_half = True

        if self.n_cpu == 0:
            self.n_cpu = cpu_count()

        # Configure parameters based on precision and GPU memory
        if self.is_half:
            # 6GB VRAM configuration
            x_pad = 3
            x_query = 10
            x_center = 60
            x_max = 65
        else:
            # 5GB VRAM configuration
            x_pad = 1
            x_query = 6
            x_center = 38
            x_max = 41

        if self.gpu_mem is not None and self.gpu_mem <= 4:
            x_pad = 1
            x_query = 5
            x_center = 30
            x_max = 32

        return x_pad, x_query, x_center, x_max


def load_hubert() -> None:
    """Load the HuBERT model for voice conversion."""
    global hubert_model
    from fairseq import checkpoint_utils
    models, saved_cfg, task = checkpoint_utils.load_model_ensemble_and_task(
        ["hubert_base.pt"], suffix=""
    )
    hubert_model = models[0]
    hubert_model = hubert_model.to(device)
    if is_half:
        hubert_model = hubert_model.half()
    else:
        hubert_model = hubert_model.float()
    hubert_model.eval()


def vc_single(
    sid: int,
    input_audio: Optional[str],
    f0_up_key: int,
    f0_file: Optional[str],
    f0_method: str,
    file_index: str,
    index_rate: float,
    filter_radius: int = 3,
    resample_sr: int = 48000,
    rms_mix_rate: float = 0.25,
    protect: float = 0.33,
) -> Tuple[Optional[str], Optional[np.ndarray]]:
    """Perform voice conversion on a single audio file.

    Args:
        sid: Speaker ID
        input_audio: Path to input audio file
        f0_up_key: Pitch shift amount
        f0_file: Optional F0 file for pitch guidance
        f0_method: F0 extraction method (harvest, pm, etc.)
        file_index: Path to index file for retrieval
        index_rate: Index retrieval rate
        filter_radius: Filter radius for smoothing
        resample_sr: Resample sample rate
        rms_mix_rate: RMS mixing rate
        protect: Protect voiceless consonants

    Returns:
        Tuple of (error message, audio array) or (None, audio array) on success
    """
    global tgt_sr, net_g, vc, hubert_model
    if input_audio is None:
        return "You need to upload an audio", None
    f0_up_key = int(f0_up_key)
    audio = load_audio(input_audio, 16000)
    times = [0, 0, 0]
    if hubert_model is None:
        load_hubert()
    if_f0 = cpt.get("f0", 1)
    version = cpt.get("version")
    audio_opt = vc.pipeline(
        hubert_model, net_g, sid, audio, input_audio, times, f0_up_key,
        f0_method, file_index, index_rate, if_f0, filter_radius=filter_radius,
        tgt_sr=tgt_sr, resample_sr=resample_sr, rms_mix_rate=rms_mix_rate,
        version=version, protect=protect, f0_file=f0_file
    )
    return None, audio_opt


def get_vc(model_path: str, device_: str, is_half_: bool) -> None:
    """Initialize RVC models for voice conversion.

    Args:
        model_path: Path to the RVC model (.pth file)
        device_: Device to use for inference (e.g., 'cuda:0', 'cpu')
        is_half_: Whether to use half precision (FP16)

    Note:
        This function initializes global state used by vc_single().
        Must be called before using vc_single().
    """
    global n_spk, tgt_sr, net_g, vc, cpt, device, is_half

    from lib.infer_pack.models import (
        SynthesizerTrnMs256NSFsid,
        SynthesizerTrnMs256NSFsid_nono,
        SynthesizerTrnMs768NSFsid,
        SynthesizerTrnMs768NSFsid_nono,
    )

    device = device_
    is_half = is_half_
    config = Config(device, is_half)
    logger.info(f"Loading RVC model: {model_path}")
    cpt = torch.load(model_path, map_location="cpu")
    tgt_sr = cpt["config"][-1]
    cpt["config"][-3] = cpt["weight"]["emb_g.weight"].shape[0]  # n_spk
    if_f0 = cpt.get("f0", 1)
    version = cpt.get("version", "v2")
    if if_f0 == 1:
        if version == "v1":
            net_g = SynthesizerTrnMs256NSFsid(*cpt["config"], is_half=is_half)
        else:
            net_g = SynthesizerTrnMs768NSFsid(*cpt["config"], is_half=is_half)
    else:
        if version == "v1":
            net_g = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
        else:
            net_g = SynthesizerTrnMs768NSFsid_nono(*cpt["config"])
    del net_g.enc_q
    logger.info(f"Model loaded: {net_g.load_state_dict(cpt['weight'], strict=False)}")
    net_g.eval().to(device)
    if is_half:
        net_g = net_g.half()
    else:
        net_g = net_g.float()
    vc = VC(tgt_sr, config)
    n_spk = cpt["config"][-3]
