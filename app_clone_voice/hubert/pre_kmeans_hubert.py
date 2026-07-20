"""
Modified HuBERT model without kmeans.
Original author: https://github.com/lucidrains/
Modified by: https://www.github.com/gitmylo/
License: MIT
"""

# Modified code from https://github.com/lucidrains/audiolm-pytorch/blob/main/audiolm_pytorch/hubert_kmeans.py

from pathlib import Path

import torch
from torch import nn
from einops import pack, unpack

from torchaudio.functional import resample

import logging
logging.root.setLevel(logging.ERROR)


def curtail_to_multiple(x, multiple):
    """Truncate tensor length to be a multiple of `multiple`."""
    if multiple is None:
        return x
    seq_len = x.shape[-2]
    trimmed_len = seq_len - (seq_len % multiple)
    return x[..., :trimmed_len, :]


def exists(val):
    return val is not None


def default(val, d):
    return val if exists(val) else d


class CustomHubert(nn.Module):
    """
    HuBERT model for voice cloning.
    Loads from either HuggingFace format or fairseq checkpoint format.
    """

    def __init__(
        self,
        checkpoint_path,
        target_sample_hz=16000,
        seq_len_multiple_of=None,
        output_layer=9,
        device=None
    ):
        super().__init__()
        self.target_sample_hz = target_sample_hz
        self.seq_len_multiple_of = seq_len_multiple_of
        self.output_layer = output_layer

        if device is not None:
            self.to(device)

        model_path = Path(checkpoint_path)

        assert model_path.exists(), f'path {checkpoint_path} does not exist'

        checkpoint = torch.load(checkpoint_path, map_location='cpu')

        # Determine state dict from checkpoint format
        state_dict = self._extract_state_dict(checkpoint)
        self.model = self._load_hf_hubert(state_dict)

        if device is not None:
            self.model.to(device)

        self.model.eval()

    def _extract_state_dict(self, checkpoint):
        """Extract state dict from various checkpoint formats."""
        # Direct state dict (HuggingFace format)
        if any(k.startswith('hubert.') for k in checkpoint.keys()):
            return checkpoint

        # Fairseq checkpoint format (has 'model' key)
        if isinstance(checkpoint, dict) and 'model' in checkpoint:
            raw = checkpoint['model']
            # Fairseq keys often have 'encoder.' prefix — strip it for HF mapping
            state_dict = {}
            for k, v in raw.items():
                new_key = k
                if new_key.startswith('encoder.'):
                    new_key = new_key[len('encoder.'):]
                state_dict[new_key] = v
            return state_dict

        # Raw state dict (no prefix)
        return checkpoint

    def _load_hf_hubert(self, state_dict):
        """Load HuBERT using HuggingFace transformers."""
        from transformers import HubertModel, HubertConfig

        config = HubertConfig(
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12,
            intermediate_size=3072,
            hidden_act='gelu',
            hidden_dropout=0.1,
            attention_probs_dropout_prob=0.1,
            initializer_range=0.02,
            layer_norm_eps=1e-12,
            feat_extract_norm='layer',
            feat_extract_activation='gelu',
            conv_dim=(512, 512, 512, 512, 512, 512, 512),
            conv_stride=(5, 2, 2, 2, 2, 2, 2),
            conv_kernel=(10, 3, 3, 3, 3, 2, 2),
            num_conv_pos_embeddings=128,
            num_conv_pos_embedding_groups=16,
            do_stable_layer_norm=False,
            apply_spec_augment=False,
            mask_time_prob=0.0,
            mask_feature_prob=0.0,
            mask_time_length=10,
            mask_time_min_masks=2,
            mask_feature_length=10,
            mask_feature_min_masks=0,
            ctc_loss_reduction='sum',
            pad_token_id=0,
            bos_token_id=1,
            eos_token_id=2,
            vocab_size=1,
        )
        model = HubertModel(config)

        # Try loading with different key mappings
        cleaned = {}
        for key, value in state_dict.items():
            new_key = key
            # Map fairseq encoder keys to HuggingFace format
            if not new_key.startswith('hubert.'):
                new_key = 'hubert.' + new_key
            cleaned[new_key] = value

        # Try strict=False first to see what loads
        result = model.load_state_dict(cleaned, strict=False)
        if result.missing_keys:
            # Try alternative mapping (some checkpoints have different prefixes)
            cleaned2 = {}
            for key, value in state_dict.items():
                new_key = key
                if new_key.startswith('hubert.'):
                    pass  # already correct
                elif new_key.startswith('encoder.'):
                    new_key = 'hubert.' + new_key
                else:
                    new_key = 'hubert.' + new_key
                cleaned2[new_key] = value
            model.load_state_dict(cleaned2, strict=False)

        return model

    @property
    def groups(self):
        return 1

    @torch.no_grad()
    def forward(
        self,
        wav_input,
        flatten=True,
        input_sample_hz=None
    ):
        device = wav_input.device

        if exists(input_sample_hz):
            wav_input = resample(wav_input, input_sample_hz, self.target_sample_hz)

        if exists(self.seq_len_multiple_of):
            wav_input = curtail_to_multiple(wav_input, self.seq_len_multiple_of)

        # HuggingFace API
        if hasattr(self.model, 'hubert'):
            out = self.model.hubert(wav_input, output_hidden_states=True)
            if self.output_layer is not None and self.output_layer < len(out.hidden_states):
                embed = out.hidden_states[self.output_layer]
            else:
                embed = out.last_hidden_state
        else:
            out = self.model(wav_input, output_hidden_states=True)
            embed = out.last_hidden_state

        embed, packed_shape = pack([embed], '* d')

        codebook_indices = torch.from_numpy(embed.cpu().detach().numpy()).to(device)

        if flatten:
            return codebook_indices

        codebook_indices, = unpack(codebook_indices, packed_shape, '*')
        return codebook_indices
