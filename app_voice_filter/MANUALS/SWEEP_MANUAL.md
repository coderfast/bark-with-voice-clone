# SWEEP_MANUAL — Centroide y ancho de banda espectral (sweep.png)

Guía completa para pasar de no saber nada a leer el brillo del sonido como un
experto, y a usarlo para afinar el conversor mini_pitch.py.

---

## Tabla de contenidos

1. [¿Qué es esta gráfica?](#1-qué-es-esta-gráfica)
2. [Analogía: la lámpara con regulador](#2-analogía-la-lámpara-con-regulador)
3. [Anatomía: ejes y líneas](#3-anatomía-ejes-y-líneas)
4. [Cómo leerla paso a paso (con nuestro tema)](#4-cómo-leerla-paso-a-paso-con-nuestro-tema)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado: 5 minutos con el Spy Hunter](#6-ejemplo-guiado-5-minutos-con-el-spy-hunter)
7. [Errores comunes al leerla](#7-errores-comunes-al-leerla)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: cómo lo calcula el código](#10-nivel-experto-cómo-lo-calcula-el-código)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué es esta gráfica?

El archivo `sweep.png` contiene dos curvas que recorren los 163 segundos del
tema. Cada curva resume **todo el espectro** en un solo número por instante:

- **Línea azul = centroide espectral:** el "centro de gravedad" de las
  frecuencias. Te dice si el sonido es oscuro (grave) o brillante (agudo).
- **Línea naranja = ancho de banda espectral:** cuánto se extiende el sonido
  alrededor de ese centro. Te dice si es concentrado (tono puro) o abierto
  (mezcla rica o ruido).

Si el espectrograma es el mapa completo del sonido, esta gráfica es su
**titular de periódico**: una línea que te cuenta la historia en 5 segundos.

---

## 2. Analogía: la lámpara con regulador

Imagina una habitación con una lámpara de luz regulable en color:

```
Luz cálida (bombilla)          Luz blanca (flexo de oficina)
     ●                                ○
  grave, oscuro                 agudo, brillante
  centroide BAJO                centroide ALTO
  (bajo, bombo)                 (platillos, lead chillón)
```

El centroide es el "color de la luz" del sonido en cada momento. El ancho de
banda es si la luz sale de un **láser** (estrecha, concentrada) o de una
**bombilla esmerilada** (ancha, difusa):

```
Banda estrecha (láser):        Banda ancha (bombilla):
      |                              /|\
      |                           /  |  \
──────┼──────                    /   |   \
      |                        /    |    \
   tono puro               mezcla rica / ruido
```

---

## 3. Anatomía: ejes y líneas

```
Magnitud (Hz)
    ▲
6000│                                          ╭──╮  ← pico: entra el lead
    │                                     ╭────╯  ╰──╮
4000│─────────────────────────────────────╯           ╰────  ← centroide ~2-4 kHz
    │     ╲╱╲╱╲╱  (naranja: ancho de banda, misma escala)
2000│  ──  bajo estable ──────────────────────────────
    │  riff de bajo manda, mezcla equilibrada
    └──────────────────────────────────────────────────▶ Tiempo
    0s         40s         80s         120s        160s
```

| Elemento | Qué es | En nuestro tema |
|---|---|---|
| **Eje X** | Tiempo, 0 a ~163 s | Igual en las 18 gráficas |
| **Eje Y** | Frecuencia en Hz | El centroide vive entre ~2.000 y ~4.000 Hz |
| **Línea azul** | Centroide: media ponderada por energía | Estable = mezcla equilibrada todo el rato |
| **Línea naranja** | Ancho de banda: dispersión alrededor del centro | Se abre donde suenan bajo + lead juntos |

---

## 4. Cómo leerla paso a paso (con nuestro tema)

Sigue estos pasos en orden, con el `sweep.png` abierto:

**Paso 1. Mira el nivel medio de la azul.**
¿Está abajo (< 1 kHz), en medio (2-4 kHz) o arriba (> 5 kHz)? Aquí está en
medio: mezcla equilibrada de graves y medios. Ni solo bajo ni solo chillido.

**Paso 2. Mira si sube y baja o es plana.**
Plana con pequeñas olas = el mismo arreglo todo el rato (riff en loop).
Aquí es plana: anticipa pocas notas distintas repetidas, ideal para HTML5.

**Paso 3. Busca picos y valles.**
Un pico = entró algo brillante (lead agudo, arpegio). Un valle = quedó solo
lo grave (pausa del lead). Marca en qué segundos ocurren: son las fronteras
de frase que luego verás en el selfsim (~90 s, ~112 s).

**Paso 4. Mira la naranja en esos mismos puntos.**
¿Se abre con el pico? Entonces entró un instrumento **más** (capas sumadas).
¿Se cierra? Entonces el sonido **cambió** de grave a agudo sin sumarse
(solo, no tutti).

**Paso 5. Saca la conclusión en una frase.**
"Mezcla equilibrada en loop con lead que entra y sale" → `--voices 2`.

---

## 5. Patrones típicos y qué significan

### Patrón A: centroide estable en medios (nuestro caso)

```
4000 │ ───╮  ╭───╮  ╭───  (pequeñas olas, mismo nivel)
     │    ╰──╯   ╰──╯
     └────────────────→
= riff continuo, arreglo homogéneo, JSON pequeño. El caso ideal.
```

### Patrón B: dos niveles alternos

```
4000 │      ╭─────╮       ╭─────╮
     │ ─────╯     ╰───────╯     ╰───
     └────────────────→
= dos capas que se turnan o se suman (bajo + lead). Confirma --voices 2
  con el corte --xover en el valle entre ambas (aquí 300 Hz).
```

### Patrón C: centroide pegado abajo

```
     │ ────────────────────────────  (bajo, ~200-500 Hz)
     └────────────────→
= casi solo bajo/bombo. Usa --voices 1 y baja --xover. Buscar lead aquí
  es buscar setas en el desierto.
```

### Patrón D: centroide por las nubes

```
8000 │ ────╲╱───╲╱───╲╱───  (alto e inquieto)
     └────────────────→
= contenido muy agudo o mucho ruido (hats, estática). Revisa --hi y sube
  --min-conf antes de culpar al detector.
```

### Patrón E: banda que respira

```
     │  naranja: ──╲＿＿＿╱──╲＿＿＿╱──  (se abre y se cierra)
     └────────────────→
= entra y sale el lead sobre el bajo continuo. Cada apertura es una frase
  del lead: cuéntalas y tendrás el número de frases del tema.
```

---

## 6. Ejemplo guiado: 5 minutos con el Spy Hunter

1. Abre `mini_pitch/_inputs/Spy Hunter NES/Spy Hunter NES Music_sweep.png`.
2. Comprueba que la azul se mueve entre 2.000 y 4.000 Hz: mezcla equilibrada.
3. Observa que no hay grandes escalones: un solo arreglo de principio a fin.
4. Fíjate en que la naranja acompaña a la azul: cuando hay más brillo hay más
   capas (bajo + lead), no un instrumento que cambie de registro.
5. Conclusión: `--voices 2`, corte 300 Hz, y vocabulario de notas pequeño.
   Efectivamente la conversión da ~35 MIDIs únicos: el titular no mentía.

---

## 7. Errores comunes al leerla

1. **Confundir pico de centroide con "nota más aguda".**
   Un pico puede ser un golpe brillante (hat) sin nota alguna. Verifica en
   el specgram si hay línea horizontal (nota) o raya vertical (golpe).

2. **Asustarse por una subida al final.**
   Muchos ripeos meten un fade con ruido o un "ding" final. Mira si la
   intensidad también sube: si no, es irrelevante.

3. **Pedirle notas.**
   Esta gráfica no dice qué nota suena, solo el color global. Para notas,
   pitch_voiced y CQT. Para color, esta.

4. **Ignorar la naranja.**
   Sin ella no distingues "más instrumentos" de "instrumento más agudo", y
   esa diferencia decide entre --voices 1 y 2.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **specgram / mel** | El centroide es su resumen en una línea. Mirada de 5 s aquí, detalle allí |
| **flatness** | Centroide alto + flatness alta = ruido brillante, no melodía |
| **intensity** | Si el volumen sube y el centroide no, entró grave (bombo/bajo) |
| **lpc** | El centroide es el centro de gravedad de esas siluetas |
| **formants** | Explican POR QUÉ el centroide está donde está (resonancias) |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Centroide bajo (< 500 Hz) todo el rato | `--voices 1`, baja `--xover` |
| Dos niveles alternos | `--voices 2`, `--xover` en medio |
| Centroide > 5 kHz | Revisa `--hi`, sube `--min-conf` |
| Banda que se abre/cierra | Frases del lead; no toques nada, está sano |

---

## 10. Nivel experto: cómo lo calcula el código

Centroide: `Σ(f · |X(f)|) / Σ|X(f)|` por ventana (media ponderada por
magnitud). Ancho de banda: `sqrt(Σ((f − centroide)² · |X(f)|) / Σ|X(f)|)`
(desviación estándar espectral). `analyze_layer()` no los calcula tal cual,
pero su f95 de energía acumulada responde a la misma pregunta ("¿dónde está
la luz?") y de ahí fija `--hi`.

Trampa conocida: un hi-hat constante sube el centroide sin aportar una sola
nota. Por eso el cap de detección del lead está fijo en 1.200 Hz pase lo que
pase con `--hi`: el brillo percusivo no debe transcribirse.

---

## 11. Ejercicio práctico

1. Abre el sweep.png y estima a ojo el valor medio de la azul (aquí ~3 kHz).
2. Cuenta los picos claros que superen 4 kHz: cada uno es candidato a entrada
   del lead. Anota sus segundos.
3. Comprueba esos segundos en el specgram: ¿hay líneas horizontales nuevas
   (lead) o rayas verticales (golpes)?
4. Compara con el selfsim: ¿coinciden tus segundos con fronteras de bloque?
5. Si todo cuadra, acabas de segmentar el tema sin oírlo.

---

## 12. Preguntas frecuentes

**¿Centroide alto significa música aguda?**
No necesariamente: puede ser ruido brillante. Cruza con flatness.

**¿Por qué la naranja a veces supera a la azul?**
Porque son magnitudes distintas (dispersión vs centro). No se comparan en
absoluto, solo sus formas.

**¿Sirve para poner el BPM?**
No directamente. Para tempo, onsets/wave/selfsim.

**¿Y si la gráfica es plana del todo?**
Un solo sonido estático (drone) o un fallo en la generación. Verifica
oyendo 5 segundos.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **Centroide espectral** | Media de frecuencias ponderada por energía; "el brillo" |
| **Ancho de banda espectral** | Dispersión del espectro alrededor del centroide |
| **f95** | Frecuencia bajo la que está el 95 % de la energía (prima del centroide) |
| **Tutti** | Pasaje donde suenan todas las capas a la vez |
| **Arreglo** | Reparto de instrumentos/voces del tema en cada momento |

---

## 14. Chuleta final

```
centroide ~2-4 kHz estable  -> mezcla equilibrada en loop, --voices 2
dos niveles                 -> bajo + lead, --xover en medio (aqui 300 Hz)
centroide > 5 kHz           -> sospecha ruido, sube --min-conf
banda que respira           -> frases del lead entrando/saliendo
pico sin linea en specgram  -> golpe, no nota
```
