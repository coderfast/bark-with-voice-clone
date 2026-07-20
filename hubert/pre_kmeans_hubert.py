"""
Modified HuBERT model without kmeans.
Original author: https://github.com/lucidrains/
Modified by: https://www.github.com/gitmylo/
License: MIT
"""

# Modified code from https://github.com/lucidrains/audiolm-pytorch/blob/main/audiolm_pytorch/hubert_kmeans.py

from pathlib import Path
from typing import Optional

import torch
from torch import nn
from einops import pack, unpack

import fairseq

from torchaudio.functional import resample

from audiolm_pytorch.utils import curtail_to_multiple

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def exists(val):
    return val is not None


class CustomHubert(nn.Module):
    """Custom HuBERT model for voice cloning without kmeans.

    This model extracts semantic features from audio waveforms for use
    in voice cloning pipelines.
    """

    def __init__(
        self,
        checkpoint_path: str,
        target_sample_hz: int = 16000,
        seq_len_multiple_of: Optional[int] = None,
        output_layer: int = 9,
        device: Optional[str] = None
    ):
        super().__init__()
        self.target_sample_hz = target_sample_hz
        self.seq_len_multiple_of = seq_len_multiple_of
        self.output_layer = output_layer

        model_path = Path(checkpoint_path)

        if not model_path.exists():
            raise FileNotFoundError(f'Checkpoint path does not exist: {checkpoint_path}')

        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        load_model_input = {checkpoint_path: checkpoint}
        model, *_ = fairseq.checkpoint_utils.load_model_ensemble_and_task(load_model_input)

        self.model = model[0]
        self.model.eval()

        if device is not None:
            self.model.to(device)

    @property
    def groups(self):
        return 1

    @torch.no_grad()
    def forward(
        self,
        wav_input: torch.Tensor,
        flatten: bool = True,
        input_sample_hz: Optional[int] = None
    ) -> torch.Tensor:
        """Extract semantic features from audio waveform.

        Args:
            wav_input: Input audio waveform tensor
            flatten: Whether to flatten the output
            input_sample_hz: Sample rate of input audio (resamples if different from target)

        Returns:
            Semantic feature tensor
        """
        device = wav_input.device

        if exists(input_sample_hz):
            wav_input = resample(wav_input, input_sample_hz, self.target_sample_hz)

        if exists(self.seq_len_multiple_of):
            wav_input = curtail_to_multiple(wav_input, self.seq_len_multiple_of)

        embed = self.model(
            wav_input,
            features_only=True,
            mask=False,  # thanks to @maitycyrus for noticing that mask is defaulted to True in the fairseq code
            output_layer=self.output_layer
        )

        embed, packed_shape = pack([embed['x']], '* d')

        # Convert to tensor directly without unnecessary numpy roundtrip
        codebook_indices = embed.to(device)

        if flatten:
            return codebook_indices

        codebook_indices, = unpack(codebook_indices, packed_shape, '*')
        return codebook_indices
