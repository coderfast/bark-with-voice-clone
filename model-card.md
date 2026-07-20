# Model Card: Bark with Voice Clone

This is a fork of Suno's BARK text-to-audio model with added voice cloning capabilities using HuBERT semantic token quantization.

## Model Details

Bark is a series of three transformer models that turn text into audio.

### Text to semantic tokens
- Input: text, tokenized with [BERT tokenizer from Hugging Face](https://huggingface.co/docs/transformers/model_doc/bert#transformers.BertTokenizer)
- Output: semantic tokens that encode the audio to be generated

### Semantic to coarse tokens
- Input: semantic tokens
- Output: tokens from the first two codebooks of the [EnCodec Codec](https://github.com/facebookresearch/encodec) from Facebook

### Coarse to fine tokens
- Input: the first two codebooks from EnCodec
- Output: 8 codebooks from EnCodec

### Architecture

| Model | Parameters | Attention | Output Vocab size |
|:-----:|:----------:|-----------|:-----------------:|
| Text to semantic tokens | 80M | Causal | 10,000 |
| Semantic to coarse tokens | 80M | Causal | 2x 1,024 |
| Coarse to fine tokens | 80M | Non-causal | 6x 1,024 |

### Audio Codec
- **EnCodec**: Neural audio codec at 24kHz with 8 codebooks

## Voice Cloning (Added in this fork)

This fork adds voice cloning capabilities using:

### HuBERT Semantic Token Quantization
- **HuBERT Model**: Self-supervised speech representation model (modified, no kmeans)
- **Custom Tokenizer**: Quantizes speech features into 10,000 semantic tokens
- **Source**: Modified from [gitmylo/bark-voice-cloning-HuBERT-quantizer](https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer)

### Voice Cloning Pipeline
1. Load reference audio (5-12 seconds recommended)
2. Extract semantic features with HuBERT
3. Quantize features into semantic tokens
4. Extract audio codec codes with EnCodec
5. Save as `.npz` prompt file for voice conditioning

### Fine-tuning Support
The project supports fine-tuning all three model stages:
- **Semantic Model**: Text → Semantic tokens
- **Coarse Model**: Semantic → Coarse codes
- **Fine Model**: Coarse → Fine codes

Training features:
- LoRA adapters (configurable dimension, scaling, dropout)
- Mixed precision (bf16)
- Gradient accumulation
- Optional 4-bit/8-bit quantization

## Broader Implications

We anticipate that this model's text-to-audio capabilities can be used to improve accessibility tools in a variety of languages. Straightforward improvements will allow models to run faster than realtime, rendering them useful for applications such as virtual assistants.

While we hope that this release will enable users to express their creativity and build applications that are a force for good, we acknowledge that any text-to-audio model has the potential for dual use. The voice cloning capabilities in this fork should be used responsibly and with consent from the voice owners.

To further reduce the chances of unintended use, a simple classifier to detect Bark-generated audio with high accuracy is included (see `notebooks/fake_classifier.ipynb`).

## Usage Notes

- Voice cloning works best with clear, noise-free audio samples of 5-12 seconds
- Generated audio is 24kHz, mono channel
- RVC (Retrieval-based Voice Conversion) can be optionally applied as post-processing for pitch/timbre adjustment
- Fine-tuned models should be placed in `semantic_output/`, `coarse_output/`, and `fine_output/` directories

## License

MIT License - see LICENSE.md for details.
