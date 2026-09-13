# MANUALS — Indice de guias de graficas de audio (mini_pitch)

Cada manual va de cero a experto con la misma estructura: que es, analogia,
anatomia de ejes, como leerlo paso a paso, patrones tipicos, ejemplo guiado
con el Spy Hunter, errores comunes, relacion con demas graficas, parametros
del conversor, nivel experto con codigo, ejercicio practico, preguntas
frecuentes, glosario y chuleta final.

Las graficas estan en `../_inputs/Spy Hunter NES/`. El de normalize es de
otro tema (LUFS) y se deja intacto.

---

## Por donde empezar (orden recomendado)

### Nivel basico (entender que suena)

1. **WAVEFORM_MANUAL.md** — la foto del volumen (wave.png)
2. **SPECTROGRAMA_MANUAL.md** — el mapa de frecuencias (specgram.png)
3. **INTENSITY_MANUAL.md** — el termometro del volumen (intensity.png)

### Nivel intermedio (entender que notas suenan)

4. **PITCH_VOICED_MANUAL.md** — en que tramos confiar (pitch_voiced.png)
5. **PITCH_MANUAL.md** — la melodia candidata (pitch.png)
6. **CQT_MANUAL.md** — el espectrograma como partitura (cqt.png)
7. **CHROMA_MANUAL.md** — en que tono esta el tema (chroma.png)

### Nivel avanzado (entender el timbre y la estructura)

8. **MEL_MANUAL.md** — el espectrograma con oidos humanos (mel.png)
9. **MFCC_MANUAL.md** — la huella dactilar del timbre (mfcc.png)
10. **HNR_MANUAL.md** — nota o ruido (hnr.png)
11. **FLATNESS_MANUAL.md** — tono o estatica (flatness.png)
12. **ZCR_MANUAL.md** — cruces por cero, barato (zcr.png)

### Nivel experto (detalles tecnicos)

13. **FORMANTS_MANUAL.md** — resonancias del sonido (formants.png)
14. **LPC_MANUAL.md** — silueta espectral (lpc.png)
15. **SWEEP_MANUAL.md** — brillo del sonido (sweep.png)
16. **SPEC_WB_NB_MANUAL.md** — wideband y narrowband (spec_wb_nb.png)
17. **JITTER_SHIMMER_MANUAL.md** — maquina o humano (jitter_shimmer.png)
18. **SELFSIM_MANUAL.md** — mapa de loops (selfsim.png)

### Utilidad general

19. **NORMALIZE_MANUAL.md** — normalizacion LUFS para videojuegos

---

## Todas las graficas

| Grafica | Manual | Pregunta que responde | Nivel |
|---------|--------|----------------------|-------|
| wave.png | WAVEFORM_MANUAL.md | Cuanto volumen y cuando? | Basico |
| specgram.png | SPECTROGRAMA_MANUAL.md | Que frecuencias suenan? | Basico |
| intensity.png | INTENSITY_MANUAL.md | Donde estan los acentos? | Basico |
| pitch_voiced.png | PITCH_VOICED_MANUAL.md | Que tramos son fiables? | Intermedio |
| pitch.png | PITCH_MANUAL.md | Que melodia candidata hay? | Intermedio |
| cqt.png | CQT_MANUAL.md | Que notas, en partitura? | Intermedio |
| chroma.png | CHROMA_MANUAL.md | En que tono esta? | Intermedio |
| mel.png | MEL_MANUAL.md | Donde estan bajo y lead? | Avanzado |
| mfcc.png | MFCC_MANUAL.md | Mismo instrumento todo el rato? | Avanzado |
| hnr.png | HNR_MANUAL.md | Nota o ruido? | Avanzado |
| flatness.png | FLATNESS_MANUAL.md | Tono o estatica? | Avanzado |
| zcr.png | ZCR_MANUAL.md | Grave/agudo/ruido, barato? | Avanzado |
| formants.png | FORMANTS_MANUAL.md | Que color tiene el timbre? | Expert |
| lpc.png | LPC_MANUAL.md | Cual es la silueta del sonido? | Expert |
| sweep.png | SWEEP_MANUAL.md | Como evoluciona el brillo? | Expert |
| spec_wb_nb.png | SPEC_WB_NB_MANUAL.md | Cuando (ataques) y que nota exacta? | Expert |
| jitter_shimmer.png | JITTER_SHIMMER_MANUAL.md | Maquina o humano? | Expert |
| selfsim.png | SELFSIM_MANUAL.md | Donde se repite el tema? | Expert |

---

## Del ojo al parametro (resumen)

```
tramo  -> selfsim (bloque) + pitch_voiced (voicing alto) + intensity (sin valles)
--xover -> mel / specgram (valle bajo/lead, aqui 300 Hz)
--hi    -> specgram / cqt (fin del dibujo; detector capa a 1200 Hz)
--min-conf -> pitch_voiced / flatness / hnr (0.15 si voicing alto, 0.25-0.35 si no)
BPM     -> spec_wb_nb (rayas/s) + wave (picos/s); desconfia del doble tempo
timbres -> formants / lpc / mfcc (triangle+square aqui)
```

`mini_pitch.py --auto` calcula todo esto solo desde el WAV; los manuales
ensenan a verificarlo a ojo.

---

## Estructura comun de cada manual

1. **Que es?** — explicacion intuitiva
2. **Analogia** — comparacion cotidiana
3. **Anatomia** — ejes, elementos visuales, que buscar
4. **Como leerlo paso a paso** — guia secuencial
5. **Patrones tipicos** — que significan los dibujos mas comunes
6. **Ejemplo guiado** — aplicacion al Spy Hunter NES
7. **Errores comunes** — que no hacer al leerlo
8. **Relacion con demas graficas** — como se complementan
9. **De la grafica al parametro** — que decisiones saca
10. **Nivel experto** — como se calcula y sus limites
11. **Ejercicio practico** — para practicar a ojo
12. **Preguntas frecuentes** — dudas comunes
13. **Glosario rapido** — terminos clave
14. **Chuleta final** — resumen para pegar en la pared
