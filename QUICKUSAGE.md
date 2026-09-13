# Quick Usage Guide

Ejemplos de línea de comando para generar audio con Bark en Windows, Linux y Mac.

## Instalación

### Windows

```cmd
git clone https://github.com/your-username/bark-with-voice-clone.git
cd bark-with-voice-clone
python -m venv venv
venv\Scripts\activate
pip install .
```

### Linux

```bash
git clone https://github.com/your-username/bark-with-voice-clone.git
cd bark-with-voice-clone
python3 -m venv venv
source venv/bin/activate
pip install .
```

### Mac

```bash
git clone https://github.com/your-username/bark-with-voice-clone.git
cd bark-with-voice-clone
python3 -m venv venv
source venv/bin/activate
pip install .
brew install ffmpeg
```

## Generar Audio Básico

### Windows

```cmd
python -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('output.wav', SAMPLE_RATE, generate_audio('Hola mundo'))"
```

### Linux / Mac

```bash
python3 -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('output.wav', SAMPLE_RATE, generate_audio('Hello world'))"
```

## Generar con Voz Específica

### Windows

```cmd
python -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('español.wav', SAMPLE_RATE, generate_audio('Buenos días, ¿cómo estás?', history_prompt='es_speaker_0'))"
```

### Linux / Mac

```bash
python3 -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('english.wav', SAMPLE_RATE, generate_audio('Good morning, how are you?', history_prompt='en_speaker_0'))"
```

## Generar con Sonidos Especiales

### Windows

```cmd
python -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('risa.wav', SAMPLE_RATE, generate_audio('¡Qué divertido! [laughs]'))"
```

### Linux / Mac

```bash
python3 -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('music.wav', SAMPLE_RATE, generate_audio('♪ Twinkle twinkle little star ♪'))"
```

## Voice Cloning

### Windows

```cmd
python -c "from bark.generation import load_codec_model, generate_text_semantic; from encodec.utils import convert_audio; import torchaudio, torch, numpy as np; model = load_codec_model(); hubert_manager = __import__('hubert.hubert_manager', fromlist=['HuBERTManager']).HuBERTManager(); hubert_manager.make_sure_hubert_installed(); hubert_manager.make_sure_tokenizer_installed(); hubert_model = __import__('hubert.pre_kmeans_hubert', fromlist=['CustomHubert']).CustomHubert('data/models/hubert/hubert.pt'); tokenizer = __import__('hubert.customtokenizer', fromlist=['CustomTokenizer']).CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth'); wav, sr = torchaudio.load('mi_voz.wav'); wav = convert_audio(wav, sr, model.sample_rate, model.channels); semantic_tokens = tokenizer.get_token(hubert_model.forward(wav, input_sample_hz=model.sample_rate)); encoded_frames = model.encode(wav.unsqueeze(0)); codes = torch.cat([e[0] for e in encoded_frames], dim=-1).squeeze(); np.savez('bark/assets/prompts/mi_voz.npz', fine_prompt=codes.numpy(), coarse_prompt=codes[:2,:].numpy(), semantic_prompt=semantic_tokens.numpy()); print('Voz clonada guardada')"
```

### Linux / Mac

```bash
python3 -c "from bark.generation import load_codec_model; from encodec.utils import convert_audio; import torchaudio, torch, numpy as np; model = load_codec_model(); hubert_manager = __import__('hubert.hubert_manager', fromlist=['HuBERTManager']).HuBERTManager(); hubert_manager.make_sure_hubert_installed(); hubert_manager.make_sure_tokenizer_installed(); hubert_model = __import__('hubert.pre_kmeans_hubert', fromlist=['CustomHubert']).CustomHubert('data/models/hubert/hubert.pt'); tokenizer = __import__('hubert.customtokenizer', fromlist=['CustomTokenizer']).CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth'); wav, sr = torchaudio.load('my_voice.wav'); wav = convert_audio(wav, sr, model.sample_rate, model.channels); semantic_tokens = tokenizer.get_token(hubert_model.forward(wav, input_sample_hz=model.sample_rate)); encoded_frames = model.encode(wav.unsqueeze(0)); codes = torch.cat([e[0] for e in encoded_frames], dim=-1).squeeze(); np.savez('bark/assets/prompts/my_voice.npz', fine_prompt=codes.numpy(), coarse_prompt=codes[:2,:].numpy(), semantic_prompt=semantic_tokens.numpy()); print('Voice cloned')"
```

### Usar voz clonada

#### Windows

```cmd
python -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('clonado.wav', SAMPLE_RATE, generate_audio('Hola soy tu voz clonada', history_prompt='mi_voz'))"
```

#### Linux / Mac

```bash
python3 -c "from bark import SAMPLE_RATE, generate_audio, preload_models; from scipy.io.wavfile import write; preload_models(); write('cloned.wav', SAMPLE_RATE, generate_audio('Hello I am your cloned voice', history_prompt='my_voice'))"
```

## Jupyter Notebooks

### Windows

```cmd
pip install jupyter
jupyter notebook clone_voice.ipynb
jupyter notebook generate.ipynb
jupyter notebook train_semantic.ipynb
```

### Linux / Mac

```bash
pip install jupyter
jupyter notebook clone_voice.ipynb
jupyter notebook generate.ipynb
jupyter notebook train_semantic.ipynb
```

## Fine-tuning

### Windows

```cmd
jupyter notebook train_semantic.ipynb
jupyter notebook train_coarse.ipynb
jupyter notebook train_fine.ipynb
```

### Linux / Mac

```bash
jupyter notebook train_semantic.ipynb
jupyter notebook train_coarse.ipynb
jupyter notebook train_fine.ipynb
```

## RVC (Voice Conversion)

### Windows

```cmd
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
python -c "from rvc_infer import get_vc, vc_single; get_vc('Retrieval-based-Voice-Conversion-WebUI/weights/modelo.pth', 'cuda:0', True); audio = vc_single(0, 'input.wav', -6, None, 'harvest', 'path/to/index', 0.75); import numpy as np; from scipy.io.wavfile import write; write('output_rvc.wav', 24000, audio)"
```

### Linux / Mac

```bash
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
python3 -c "from rvc_infer import get_vc, vc_single; get_vc('Retrieval-based-Voice-Conversion-WebUI/weights/model.pth', 'cuda:0', True); audio = vc_single(0, 'input.wav', -6, None, 'harvest', 'path/to/index', 0.75); import numpy as np; from scipy.io.wavfile import write; write('output_rvc.wav', 24000, audio)"
```

## Solución de Problemas

### Errores Comunes

#### Windows

```cmd
# CUDA out of memory - usar modelos pequeños
python -c "from bark.generation import preload_models; preload_models(text_use_small=True, coarse_use_small=True, fine_use_small=True)"

# Error fairseq
pip install fairseq

# Error encodec
pip install encodec
```

#### Linux

```bash
# Instalar ffmpeg
sudo apt-get install ffmpeg

# CUDA out of memory
python3 -c "from bark.generation import preload_models; preload_models(text_use_small=True, coarse_use_small=True, fine_use_small=True)"
```

#### Mac

```bash
# Instalar ffmpeg
brew install ffmpeg

# Apple Silicon - torch
pip install torch torchvision torchaudio

# CUDA out of memory
python3 -c "from bark.generation import preload_models; preload_models(text_use_small=True, coarse_use_small=True, fine_use_small=True)"
```

## Idiomas Soportados

| Idioma | Código | Ejemplo |
|--------|--------|---------|
| Español | `es_speaker_0` a `es_speaker_9` | `es_speaker_0` |
| Inglés | `en_speaker_0` a `en_speaker_9` | `en_speaker_0` |
| Alemán | `de_speaker_0` a `de_speaker_9` | `de_speaker_0` |
| Francés | `fr_speaker_0` a `fr_speaker_9` | `fr_speaker_0` |
| Italiano | `it_speaker_0` a `it_speaker_9` | `it_speaker_0` |
| Portugués | `pt_speaker_0` a `pt_speaker_9` | `pt_speaker_0` |
| Japonés | `ja_speaker_0` a `ja_speaker_9` | `ja_speaker_0` |
| Coreano | `ko_speaker_0` a `ko_speaker_9` | `ko_speaker_0` |
| Chino | `zh_speaker_0` a `zh_speaker_9` | `zh_speaker_0` |

## Sonidos Especiales

| Sonido | Código | Ejemplo |
|--------|--------|---------|
| Risa | `[laughs]` | `¡Qué divertido! [laughs]` |
| Suspiro | `[sighs]` | `Estoy cansado [sighs]` |
| Música | `♪ texto ♪` | `♪ La la la ♪` |
| Grito | `[gasps]` | `¡Oh! [gasps]` |
| Tos | `[clears throat]` | `Ejem [clears throat]` |
| Pausa | `—` o `...` | `Bueno... no sé` |
| Énfasis | MAYÚSCULAS | `¡ES INCREÍBLE!` |
| Hablante | `HOMBRE:` / `MUJER:` | `HOMBRE: Hola` |
