# ROADMAP.md — app_clone_voice

Herramienta CLI para clonar voces a partir de muestras de audio.

---

## Estado Actual

### Fase 1: CLI Mejorado ✅ COMPLETADO
- Soporte MPS (Apple Silicon) con prioridad CUDA > MPS > CPU
- `--device-info` para ver dispositivos disponibles
- `--list` para listar voces
- `--info VOICE` para ver metadata de una voz
- `--verbose` para output detallado con tiempos
- `--version`
- `--force` para sobrescribir voces existentes

### Fase 2: Manejo de Errores ✅ COMPLETADO
- Validacion de audio: duracion < 13s, sample rate >= 8kHz
- Validacion de nombre de voz: solo alphanumeric, guion, guion bajo
- Validacion de voz existente antes de sobrescribir
- Try/except con mensajes claros (traceback solo con --verbose)
- KeyboardInterrupt con mensaje limpio

### Fase 3: Funcionalidades Adicionales ✅ COMPLETADO
- `--output PATH` para exportar prompt a ubicacion personalizada
- Validacion de integridad del prompt generado (shapes, keys)
- `--quiet` para modo silencioso (solo imprime path del resultado)
- Version 1.1.0

### Fase 4: Calidad de Codigo ✅ COMPLETADO
- Type hints en todas las funciones (`from __future__ import annotations`)
- Logging con `logging` module (reemplaza print directo)
- 20 tests unitarios passing

### Fase 5: Empaquetado ✅ COMPLETADO
- `pyproject.toml` para instalacion con pip
- Entry point `voice-clone` (despues de `pip install .`)
- `Dockerfile` para ejecucion aislada
- `.dockerignore`
- Configuracion de pytest, ruff, mypy

### Fase 6: Compilacion Portable ✅ COMPLETADO

Compilar la app Python como ejecutable standalone para que funcione sin Python instalado.

**Herramienta:** PyInstaller

**Archivos creados:**
- `build.py` — script de compilacion
- `voice_clone.spec` — configuracion PyInstaller
- `requirements-build.txt` — dependencias de compilacion

**Uso:**
```bash
pip install -r requirements-build.txt
python build.py           # onedir (recomendado)
python build.py --onefile # archivo unico (~1.5-2GB)
```

**Plataformas:**
- Windows: `dist/voice_clone.exe`
- Linux: `dist/voice_clone`
- macOS: `dist/voice_clone`

---

## Archivos

| Archivo | Funcion |
|---------|---------|
| `voice_clone.py` | CLI principal — clonar voces |
| `requirements.txt` | Dependencias para pip |
| `pyproject.toml` | Configuracion del paquete |
| `Dockerfile` | Contenedor Docker |
| `tests/test_voice_clone.py` | Tests unitarios |
| `build.py` | Script de compilacion (pendiente) |
| `voice_clone.spec` | Configuracion PyInstaller (pendiente) |
| `bark/` | Modulo Bark local (carga de modelos) |
| `hubert/` | Modulo HuBERT local (extraccion de features) |
| `source_voice_input/` | Carpeta para audios de referencia |
| `QUICKUSAGE.txt` | Guia rapida de uso |

---

## Cambios Recientes

| Cambio | Estado |
|--------|--------|
| `--output` para exportar a ubicacion personalizada | ✅ |
| `--quiet` para modo silencioso | ✅ |
| Validacion de integridad del prompt | ✅ |
| Type hints en todas las funciones | ✅ |
| Logging con `logging` module | ✅ |
| 20 tests unitarios | ✅ |
| `pyproject.toml` | ✅ |
| Entry point `voice-clone` | ✅ |
| `Dockerfile` | ✅ |
| Fase 6: Compilacion Portable (PyInstaller) | ✅ |
| Eliminar subcomando `generate` (app solo clona) | ✅ |
| Eliminar `fairseq` (no compila en Windows) | ✅ |
| Eliminar `audiolm-pytorch` (no usado) | ✅ |
| Eliminar `funcy` (reemplazado con `functools`) | ✅ |
| Soporte cross-platform (Windows, Linux, macOS) | ✅ |
| Dependencias: 12 → 9 | ✅ |
| Fix: reemplazar `torchaudio` por `soundfile` (torchaudio 2.11+ eliminó `info()`/`load()`) | ✅ |
| Fix: `feat_extract_norm='layer_norm'` → `'layer'` (transformers 5.x) | ✅ |
| Fix: `torch.load()` con `map_location='cpu'` en customtokenizer | ✅ |
| Dependencia: `soundfile` agregada a requirements.txt | ✅ |
| Monkey-patch `weight_norm` → `parametrizations.weight_norm` (elimina FutureWarning) | ✅ |

---

## Uso del Entry Point

```bash
# Instalar como paquete
pip install -e .

# Usar como comando
voice-clone --name mi_voz --audio ref.wav

# O ejecutar directamente
python voice_clone.py --name mi_voz --audio ref.wav
```

---

## Uso de Docker

```bash
# Construir imagen
docker build -t voice-clone .

# Ejecutar
docker run --rm -v $(pwd)/source_voice_input:/app/source_voice_input voice-clone --name mi_voz
```
