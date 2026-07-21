# ROADMAP.md — Voice Filter Refactorización

## Objetivo
Dividir el monolito `voice_filter.py` (1959 líneas) en módulos separados por responsabilidad, manteniendo la misma funcionalidad y comportamiento.

## Estructura actual

```
app_voice_filter/
├── voice_filter.py          # Todo: config + widgets + audio + GUI (1959 líneas)
├── requirements.txt
├── APP_ARCHITECTURE.md
└── APP_TECHNICALSTACK.md
```

## Estructura propuesta

```
app_voice_filter/
├── voice_filter.py              # Entry point (main + imports, ~20 líneas)
│
├── config/
│   ├── __init__.py              # from .colors import COLORS
│   └── colors.py                # Diccionario COLORS (~60 líneas)
│
├── audio/
│   ├── __init__.py              # from .processor import AudioProcessor
│   └── processor.py             # AudioProcessor (~420 líneas)
│
├── widgets/
│   ├── __init__.py              # from .mixer_fader import MixerFader; from .vu_meter import AnalogVUMeter
│   ├── mixer_fader.py           # MixerFader (~260 líneas)
│   └── vu_meter.py              # AnalogVUMeter (~160 líneas)
│
├── gui/
│   ├── __init__.py              # from .app import VoiceFilterGUI
│   ├── app.py                   # VoiceFilterGUI main class (~600 líneas)
│   ├── transport.py             # Transport bar creation (~30 líneas)
│   ├── waveform.py              # Waveform display + dibujado (~50 líneas)
│   └── tabs.py                  # 8 pestañas del notebook + _create_slider (~500 líneas)
│
├── requirements.txt             # Sin cambios
├── APP_ARCHITECTURE.md          # Actualizar estructura
├── APP_TECHNICALSTACK.md        # Sin cambios
└── ROADMAP.md                   # Este archivo
```

## Tipos de controles identificados

| # | Control | Tipo | Archivo destino |
|---|---------|------|-----------------|
| 1 | `MixerFader` | Widget custom (`tk.Canvas`) | `widgets/mixer_fader.py` |
| 2 | `AnalogVUMeter` | Widget custom (`tk.Canvas`) | `widgets/vu_meter.py` |
| 3 | Channel strip | Patrón compuesto (Label + Fader + Label) | `gui/tabs.py` |
| 4 | Waveform display | Patrón compuesto (Label + Canvas) | `gui/waveform.py` |
| 5 | Transport bar | Patrón compuesto (LabelFrame + Buttons) | `gui/transport.py` |
| 6 | Menu bar | `tk.Menu` | `gui/app.py` |
| 7 | `COLORS` dict | Configuración | `config/colors.py` |
| 8 | `AudioProcessor` | Lógica de negocio | `audio/processor.py` |

## Fases de refactorización

### Fase 1: Configuración
**Crear:** `config/__init__.py`, `config/colors.py`

- Extraer el diccionario `COLORS` (líneas 458-515)
- Crear `__init__.py` que re-exporta `COLORS`

### Fase 2: Widgets custom
**Crear:** `widgets/__init__.py`, `widgets/mixer_fader.py`, `widgets/vu_meter.py`

- Extraer `MixerFader` (líneas 518-775, ~260 líneas)
- Extraer `AnalogVUMeter` (líneas 785-942, ~160 líneas)
- Ambas clases dependen de `COLORS` → importar desde `config`

### Fase 3: Audio processor
**Crear:** `audio/__init__.py`, `audio/processor.py`

- Extraer `AudioProcessor` (líneas 34-454, ~420 líneas)
- Solo depende de numpy, scipy, soundfile, sounddevice, threading

### Fase 4: GUI - Transport y Waveform
**Crear:** `gui/__init__.py`, `gui/transport.py`, `gui/waveform.py`

- Extraer `_create_transport()` (líneas 1060-1074)
- Extraer `_create_waveform()` + `_draw_waveform()` + `_draw_original_waveform()` + `_draw_modified_waveform()` (líneas 1076-1112, 1550-1588)
- Son funciones/métodos que se importan en `gui/app.py`

### Fase 5: GUI - Tabs del notebook
**Crear:** `gui/tabs.py`

- Extraer los 8 métodos `_create_*_tab()` (líneas 1172-1536)
- Extraer `_create_slider()` (líneas 1135-1164)
- ~500 líneas que se importan como mixin o funciones auxiliares

### Fase 6: GUI - Clase principal
**Crear:** `gui/app.py`

- `VoiceFilterGUI.__init__()`, `_create_variables()`, `_create_menu()`, `_create_main_frame()`, `_create_status_bar()`
- Toda la lógica de playback: `_play_original()`, `_play_modified()`, `_stop_audio()`, `_on_playback_finished()`
- Animación: `_start_animation()`, `_stop_animation()`, `_animate_meters()`
- Utilidades: `_get_params()`, `_reset_all()`, `_save_preset()`, `_load_preset()`, etc.

### Fase 7: Entry point
**Reemplazar:** `voice_filter.py`

```python
"""Voice Filter - Audio Processing Application"""
from gui.app import main

if __name__ == "__main__":
    main()
```

### Fase 8: Documentación
**Actualizar:** `APP_ARCHITECTURE.md`

- Actualizar la estructura del proyecto en el diagrama de carpetas

## Dependencias entre módulos

```
config/colors.py          ← (sin dependencias)
audio/processor.py        ← numpy, scipy, soundfile, sounddevice
widgets/mixer_fader.py    ← tkinter, config/colors
widgets/vu_meter.py       ← tkinter, numpy, config/colors
gui/tabs.py               ← tkinter, widgets, config/colors
gui/transport.py          ← tkinter, ttk
gui/waveform.py           ← tkinter, numpy, config/colors
gui/app.py                ← todo lo anterior
voice_filter.py           ← gui/app
```

## Orden de ejecución

1. Crear directorios (`config/`, `audio/`, `widgets/`, `gui/`) y `__init__.py`
2. Extraer `config/colors.py`
3. Extraer `widgets/mixer_fader.py` + `vu_meter.py`
4. Extraer `audio/processor.py`
5. Extraer `gui/tabs.py` (8 pestañas + _create_slider)
6. Extraer `gui/transport.py` + `gui/waveform.py`
7. Extraer `gui/app.py` ( VoiceFilterGUI main )
8. Crear nuevo `voice_filter.py` entry point
9. Actualizar `APP_ARCHITECTURE.md`
10. Probar la aplicación completa

## Verificación

1. Ejecutar `python voice_filter.py`
2. Cargar un archivo de audio
3. Reproducir original → verificar VU meter y fader LEDs animados
4. Reproducir modificado → verificar animación
5. Cambiar entre original y modificado reproduciendo → verificar que no se bloquea
6. Auto-preview: mover slider y soltar → verificar que reproduce
7. Presets: guardar y cargar preset
8. Reset: verificar que todos los controles vuelven a valores por defecto
