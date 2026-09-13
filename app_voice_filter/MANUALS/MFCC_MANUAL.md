# MFCC_MANUAL — Coeficientes cepstrales (mfcc.png)

Guía completa: la "huella dactilar" del timbre, de cero a experto.

---

## Tabla de contenidos

1. [¿Qué es?](#1-qué-es)
2. [Analogía: la ficha policial](#2-analogía-la-ficha-policial)
3. [Anatomía: 13 filas](#3-anatomía-13-filas)
4. [Cómo leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: la cadena Mel → log → DCT](#10-nivel-experto-la-cadena-mel--log--dct)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué es?

Si el Mel espectrograma es una foto del sonido, los **MFCC son su ficha
policial**: una docena de números por instante que describen **cómo suena**
(brillante, nasal, hueco...) ignorando **qué nota** suena:

```
Misma nota, distinto instrumento:    Distinta nota, mismo instrumento:
  piano Do  vs  trompeta Do            piano Do  vs  piano Sol
  MFCC DISTINTOS (timbre)              MFCC PARECIDOS (timbre)
  = "quién" distinto                   = mismo "quién"
```

Sirven para reconocer instrumentos y texturas, nunca melodías.

---

## 2. Analogía: la ficha policial

La policía no guarda tu foto entera para buscarte: guarda altura, color de
ojos, tatuajes... una docena de datos que bastan para distinguirte entre
millones. Los MFCC igual: 13 números bastan para distinguir un bajo cuadrado
de una trompeta, un piano o ruido. Foto (mel) para el álbum, ficha (MFCC)
para el archivo.

---

## 3. Anatomía: 13 filas

- **X = tiempo (0-163 s).**
- **Y = coeficientes 1 a 13.** El 1º mide energía global; del 2º en adelante
  miden la forma del espectro de grueso (2-4) a fino (10-13).
- **Franjas horizontales estables** = mismo timbre todo el rato (nuestro
  chiptune: el mismo "instrumento" 163 s).
- **Cambios de dibujo** (~65 s, ~90 s, ~112 s) = otra instrumentación o
  densidad: coinciden con las secciones del selfsim.

---

## 4. Cómo leerlo paso a paso

**Paso 1. Mira si hay franjas estables.**
Sí → un timbre dominante. No (todo cambia) → collage o mezcla inestable.

**Paso 2. Marca los cambios de dibujo.**
Cada cambio brusco vertical es un cambio de instrumentación o arreglo.
Anota los segundos: son candidatos a fronteras de sección.

**Paso 3. Mira el coeficiente 1.**
Sus picos son los picos de volumen global (cruza con intensity).

**Paso 4. Compara coeficientes 2-4 entre secciones.**
Si dos secciones comparten esos (forma gruesa) pero difieren en 10-13
(detalle), es el mismo instrumento con distinto registro o efecto.

**Paso 5. Concluye el banco de timbres.**
Un dibujo → un banco de osciladores (`triangle` bajo + `square` lead aquí).
Dos dibujos → dos bancos o dos conversiones separadas.

---

## 5. Patrones típicos y qué significan

### Patrón A: franjas estables (nuestro caso)

```
c13 ·······················
...  ═══════════════════════  (mismo dibujo 163 s)
c1  ███████████████████████
    └──────────────────────→
= un instrumento/textura. Un banco de osciladores basta para todo el tema.
```

### Patrón B: escalones

```
    dibujo1 ││ dibujo2 ││ dibujo1
    └──────────────────────→
= secciones con distinta instrumentación (verso/puente). Convierte cada
  escalón con sus timbres o acepta un banco medio.
```

### Patrón C: deriva lenta

```
    ╲ · · · · · · · · · · · ·╲  (el dibujo se desplaza)
= filtro que se abre/cierra (sweep de sintetizador) o crossfade. El timbre
  cambia dentro de la sección: ojo con un único banco fijo.
```

### Patrón D: todo plano y uniforme

```
    ───────────────────────  (sin dibujo)
= un solo sonido estático, silencio o fallo de cálculo. Verifica oyendo.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el mfcc.png: franjas estables casi todo el tema → un timbre.
2. Marca los cambios (~65, ~90, ~112 s): coinciden con puente y secciones
   del selfsim → el arreglo cambia, el instrumento no.
3. Conclusión: `triangle` para voz0-1 (bajo) + `square`/`sawtooth` para
   voz2 (lead) en preview y HTML, sin cambiar en 163 s.
4. Verifica en el player: si alguna sección suena "a otro instrumento",
   vuelve aquí y mira si su dibujo MFCC era distinto (entonces merece su
   propio banco).

---

## 7. Errores comunes al leerlo

1. **Buscar notas.**
   Aquí no hay notas. Nunca. Para notas: pitch, CQT, chroma.

2. **Confundir volumen con timbre.**
   El coeficiente 1 manda en energía; si todo "cambia" pero solo cambia el
   c1, es volumen (ver intensity), no instrumento nuevo.

3. **Sobreinterpretar el detalle (c10-13).**
   Los coeficientes finos son sensibles a ruido de codificación del ripeo.
   Decide con c2-c6; el resto matiza.

4. **Pedirle octavas.**
   Dos cuadradas a distinta altura dan MFCC casi idénticos. Para octavas,
   pitch.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **mel** | Los MFCC son la mel comprimida por DCT |
| **formants / lpc** | Otra forma de contar el mismo color tímbrico |
| **selfsim** | Los cambios de MFCC explican sus bloques |
| **jitter_shimmer** | Allí máquina-vs-humano; aquí qué máquina |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Un dibujo estable | Un banco: `--waveforms triangle,square,...` fijo |
| Escalones | Secciones: convierte dentro de un escalón o ajusta timbres por sección |
| Solo cambia c1 | Es volumen: `--normalize-vel` / `--smooth-vel`, no timbres |
| Deriva lenta | Filtro en movimiento: acepta banco medio o trocea |

---

## 10. Nivel experto: la cadena Mel → log → DCT

Ventana → FFT → banco de filtros Mel (~40) → logaritmo → DCT, quedándonos
con los 12-13 primeros coeficientes. Cada paso imita percepción: Mel =
resolución del oído, log = ley de volumen percibido, DCT = descorrelación
(compacta la info para clasificadores). Por eso 13 números bastan.

Límites: la DCT descarta fase y detalle fino (no sirve para pitch), y el
banco Mel promedia armónicos (no distingue cuadrada de sierra con igual
envolvente: para eso, formants/LPC). Uso futuro en el proyecto:
segmentación automática por secciones con k-means sobre MFCC para trocear
temas largos antes de convertir, sin mirar el selfsim a ojo.

---

## 11. Ejercicio práctico

1. Marca los cambios de dibujo y anota sus segundos.
2. Cruza con selfsim: ¿coinciden con fronteras de bloque?
3. Compara c2-c6 entre 0-20 s y 90-112 s: ¿mismo instrumento?
4. Escucha el player en ambas zonas: ¿el banco único convence en las dos?
5. Si no: propón en qué segundo partirías la conversión en dos.

---

## 12. Preguntas frecuentes

**¿Por qué 13 y no 40?**
Los primeros concentran la forma útil; el resto es detalle y ruido. 13 es
el estándar de voz; en música a veces 20.

**¿MFCC para transcribir notas?**
No. Hay variantes (chroma lo hace mejor) pero el conversor usa
autocorrelación: más directo y sin entrenamiento.

**¿Y si dos secciones suenan igual pero se ven distinto?**
Fíate del oído para timbres y de los MFCC para estructura: la vista exagera
diferencias inaudibles de codificación.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **MFCC** | Mel-Frequency Cepstral Coefficients: huella del timbre |
| **Cepstrum** | Espectro del log-espectro; separa fuente y filtro |
| **DCT** | Transformada coseno discreta; compacta la información |
| **Banco de filtros Mel** | ~40 filtros triangulares según percepción |
| **k-means** | Agrupamiento automático (futura segmentación) |

---

## 14. Chuleta final

```
franjas estables = mismo instrumento, un banco basta
cambio de dibujo = seccion -> convierte dentro de una
solo cambia c1 = volumen, no timbre
aqui no hay notas, solo color
```
