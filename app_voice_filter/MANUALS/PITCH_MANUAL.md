# PITCH_MANUAL — Contorno de pitch completo (pitch.png)

Guía completa: la melodía candidata con sus dudas incluidas, de cero a experto.

---

## Tabla de contenidos

1. [¿Qué es?](#1-qué-es)
2. [Analogía: la montaña rusa](#2-analogía-la-montaña-rusa)
3. [Anatomía: curva y nubes](#3-anatomía-curva-y-nubes)
4. [Cómo leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: autocorrelación y sus dos fracasos](#10-nivel-experto-autocorrelación-y-sus-dos-fracasos)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué es?

La línea que dibuja **qué tan agudo o grave** suena cada instante, en Hz,
con sus subidas y bajadas. Si el chroma decía "qué letras", esto dice "qué
nota exacta y cuándo". Incluye también los tramos dudosos (ruido, silencios,
reverberación), que se ven como **nubes de puntos dispersos**: el detector
adivinando.

```
Hz (log)
 300 ┤        ╭─╮           sol brillante del lead
 200 ┤   ╭────╯ ╰──╮        respuestas
 140 ┤╭──╯         ╰──╮     riff del bajo
  70 ┼╯               ╰──   (dientes de sierra regulares)
     └──────────────────→ t
         ·  ·   ·   ·      nubes = dudas (ignorar)
```

---

## 2. Analogía: la montaña rusa

Cada subida es la melodía elevándose, cada bajada el bajo descendiendo, cada
diente de sierra una nota picada del riff. Y las nubes de puntos son la
niebla del parque: donde hay niebla, el vagón (el detector) va a ciegas y lo
que diga no cuenta.

---

## 3. Anatomía: curva y nubes

- **X = tiempo (0-163 s).**
- **Y = frecuencia en Hz, escala logarítmica** (cada octava ocupa lo mismo,
  como en el piano).
- **Línea continua** = el detector está seguro (nota real casi siempre).
- **Nube dispersa** = está adivinando (ruido, reverb, silencio).
- En nuestro tema: dientes de sierra regulares entre 70 y 140 Hz (riff
  E-F-F#-G del bajo, nota por nota) y nubes en 65-100 s (voicing bajo: la
  zona que hay que filtrar).

---

## 4. Cómo leerlo paso a paso

**Paso 1. Localiza la banda con dientes regulares.**
Esa es la melodía/bajo principal (70-140 Hz aquí). Todo lo sólido vive ahí.

**Paso 2. Mide un diente.**
Ancho temporal de un diente ≈ duración de la nota (~0,15 s = corchea aquí).
Divide 60 entre el doble: BPM ≈ 90-100 sin calculadora.

**Paso 3. Marca las nubes.**
Zonas de puntos sin línea (65-100 s): el detector duda. Todo MIDI nacido
ahí es sospechoso: súbelo con `--min-conf` o recorta el tramo.

**Paso 4. Busca saltos imposibles.**
¿Un salto de 2 octavas en 10 ms? Ningún bajo chiptune lo hace: es error de
octava (el 2º armónico ganó). Anótalos: la `octave_guard` debería cazarlos;
si aparecen en el JSON, hay que endurecerla o bajar `--hi`.

**Paso 5. Cuenta voces.**
¿Una línea o dos superpuestas (una grave continua + saltos agudos)? Aquí
dos → `--voices 2` (el plugin afina a 4 bandas).

---

## 5. Patrones típicos y qué significan

### Patrón A: dientes de sierra regulares (nuestro riff)

```
Hz
140 ┤╭╮ ╭╮ ╭╮ ╭╮
100 ┤╯╰─╯╰─╯╰─╯╰─
    └────────────→
= notas picadas regulares. Un diente = un evento MIDI. Tempo estable.
```

### Patrón B: mesetas

```
200 ┤  ╭──────╮
    ┤──╯      ╰──
    └────────────→
= notas tenidas. Su largo es la duración MIDI (cuidado con colas de reverb
  que alargan: ver pitch_voiced).
```

### Patrón C: nubes

```
    ┤   ·  · · ·  ·
    ┤ · · · · · · ·
    └────────────→
= ruido/pausa/reverb. No transcribir: --min-conf o cambio de tramo.
```

### Patrón D: escalera rota (octavas falsas)

```
400 ┤     ×           (punto suelto arriba)
200 ┤───╯ ╰───╯ ╰───  (melodía real abajo)
    └────────────→
= el detector picó el armónico. Si el JSON trae el ×, fallo de
  octave_guard/--hi.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el pitch.png: dientes 70-140 Hz de 0 a 60 s. Riff claro.
2. Mide un diente (~0,15 s) → corchea → BPM ~90-100. El --auto dice 90.9
   (115.4 en el tema entero; el plugin clava 90.9): cuadra con tu medida.
3. Localiza nubes (65-100 s): zona a filtrar con min-conf 0.15-0.25.
4. Busca saltos de octava: si los hay y el JSON trae A8/D9, ya sabes el
   diagnóstico (cap 1.200 Hz + LEAD_CAP 87 los eliminan: la conversión final
   topa en 87).
5. Cuenta líneas: grave continua + saltos → 2+ voces. Plugin: 4 bandas.

---

## 7. Errores comunes al leerlo

1. **Transcribir las nubes.**
   El error caro: de ahí salían los MIDIs de 100+ de la v1. Nube = no nota.

2. **Creerse los saltos de octava.**
   Ningún dedo salta 2 octavas en 10 ms. Son armónicos ganando al pico.

3. **Confundir vibrato con varias notas.**
   Onda periódica pequeña sobre una meseta = una nota con vida, no 5
   notitas. El `merge_short_notes` las reunifica; no partas a mano.

4. **Leer Hz lineales.**
   El eje es logarítmico: de 70 a 140 hay la misma distancia que de 140 a
   280 (una octava en ambos). Mide en octavas, no en Hz.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **pitch_voiced** | Esta curva sin las nubes (solo tramos fiables). Aquí diagnosticas, allí decides |
| **cqt** | Los dientes son los bloques de allí |
| **hnr** | Donde el HNR es bajo, esta curva miente: ignórala ahí |
| **zcr** | Cada diente debería tener su diente de cruces por cero |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Banda de dientes sólidos | `--lo` / `--hi` (aquí 40 / 1.200) |
| Ancho de diente | Estima BPM (corchea ≈ 60/(2·BPM)) |
| Nubes | `--min-conf` 0.25-0.4 o recorte de tramo |
| Saltos de octava en JSON | Endurecer `octave_guard` / bajar `--hi` |
| Dos líneas superpuestas | `--voices 2` / `--xovers` |

---

## 10. Nivel experto: autocorrelación y sus dos fracasos

`autocorr_pitch()` por ventanas: resta media → ventana Hann → autocorrelación
vía FFT → pico en el rango permitido → interpolación parabólica → confianza
por contraste del pico. Sus dos fracasos clásicos en chiptune:

1. **Octava doble:** la cuadrada tiene un 2º armónico fortísimo y el pico
   cae en tau/2 (frecuencia doble). Lo corrige `octave_guard()`: baja por
   octavas mientras el peine de la inferior concentre más energía, con
   pre-corte de todo lo que supere 1,5× la zona útil.
2. **Ruido "voiced":** reverberación y soplo dan picos débiles pero
   suficientes. Lo corrigen el gate de RMS (0.01), el umbral de pico (0.3) y
   `--min-conf`.

Regla de auditoría: si una nota del MIDI no tiene su diente aquí, es
inventada. Sin excepciones.

---

## 11. Ejercicio práctico

1. Mide 3 dientes y promedia su ancho: estima el BPM a mano.
2. Compara con el BPM del JSON (90.9) y con el del --auto en tema entero
   (115.4). ¿Cuál cuadra con tu medida? (Pista: el plugin clava 90.9.)
3. Busca la nube 65-100 s: ¿cuántas notas del JSON nacen ahí? ¿Deberían?
4. Elige una nota aguda del JSON (> 80) y busca su diente: ¿existe?
5. Si un salto de octava llegó al JSON, propón el fix (hi/guardia/plugin).

---

## 12. Preguntas frecuentes

**¿Por qué logarítmico y no lineal?**
Porque la música es logarítmica (octavas) y así cada nota ocupa lo mismo.

**¿Diente = nota siempre?**
Casi: un diente puede ser un reataque de la misma nota (staccato). El
`merge_short_notes` decide con el MIDI vecino.

**¿Y si no hay dientes ni mesetas?**
O es ruido/textura (no transcribible nota a nota) o el rango del eje no
incluye la melodía: ajusta la vista antes de rendirte.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **Pitch** | Altura percibida; aquí f0 estimada por ventana |
| **Autocorrelación** | Similitud de la señal consigo misma desplazada; su pico da el periodo |
| **Interpolación parabólica** | Refinamiento sub-muestra del pico |
| **Diente** | Ciclo subida-bajada = nota picada |
| **Nube** | Dispersión sin línea: el detector adivina |

---

## 14. Chuleta final

```
dientes regulares = notas reales, un diente = un evento MIDI
ancho de diente ~= corchea -> estima BPM a mano
nubes = no convertir (min-conf o recorte)
salto de octava imposible = artefacto (guardia / --hi)
sin diente no hay nota: audita el MIDI aqui
```
