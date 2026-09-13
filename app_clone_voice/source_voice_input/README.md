# source_voice_input

Coloca aquí un archivo de audio (WAV, MP3, OGG, FLAC, M4A, WMA) con la voz que quieres clonar.

## Formato

- Un solo archivo de audio por ejecución
- Duración recomendada: 5-12 segundos
- Audio claro, sin ruido de fondo
- Una sola persona hablando

## Uso

```bash
# 1. Pon tu audio en esta carpeta
#    source_voice_input/mi_voz.wav

# 2. Ejecuta clone sin --audio
python voice_clone.py clone --name mi_voz

# 3. Genera audio con esa voz
python voice_clone.py generate --text "Hola mundo" --voice mi_voz --output hola.wav
```

## Formatos soportados

- `.wav`
- `.mp3`
- `.ogg`
- `.flac`
- `.m4a`
- `.wma`
