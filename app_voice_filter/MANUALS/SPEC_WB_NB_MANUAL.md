# SPEC_WB_NB_MANUAL — Espectrogramas de banda ancha y banda estrecha (spec_wb_nb.png)

Guía completa: dos lupas distintas sobre el mismo sonido, de cero a experto.

---

## Tabla de contenidos

1. [¿Por qué hay dos imágenes?](#1-por-qué-hay-dos-imágenes)
2. [Analogía: mapa de carreteras y plano de calles](#2-analogía-mapa-de-carreteras-y-plano-de-calles)
3. [Anatomía de cada panel](#3-anatomía-de-cada-panel)
4. [Cómo leerlos paso a paso](#4-cómo-leerlos-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlos](#7-errores-comunes-al-leerlos)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: el compromiso tiempo-frecuencia](#10-nivel-experto-el-compromiso-tiempo-frecuencia)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Por qué hay dos imágenes?

Porque la física no deja verlo todo a la vez. Para saber **cuándo** empieza
una nota necesitas mirar ventanas de audio muy cortas; para saber **qué
frecuencia exacta** suena necesitas ventanas largas. Son dos microscopios:

- **Panel superior (Wideband, detalle temporal):** ventana corta (~5 ms).
  Ves columnas verticales nítidas = **ataques, golpes, inicios de nota**.
- **Panel inferior (Narrowband, detalle armónico):** ventana larga (~40 ms).
  Ves líneas horizontales finas = **frecuencias exactas y sus armónicos**.

```
Wideband (¿CUÁNDO?):              Narrowband (¿QUÉ?):
Hz                                Hz
│  │   │    │  │                   │ ─────────────── 440 Hz
│  │   │    │  │                   │ ─────────────── 880 Hz
│  │   │    │  │                   │ ─────────────── 1320 Hz
└──┴───┴────┴──┴──→ t              └──────────────────→ t
   ataques nítidos                    notas y armónicos
```

---

## 2. Analogía: mapa de carreteras y plano de calles

- **Wideband = mapa de carreteras:** ves dónde hay ciudades (eventos) y
  cuándo pasas por ellas, pero no las calles.
- **Narrowband = plano de calles:** ves cada casa (cada armónico) pero
  pierdes la noción del viaje.

El conversor necesita ambos: el mapa para **segmentar** (onsets) y el plano
para **afinar** (pitch). Por eso el código usa hop de 10 ms para onsets
(modo wideband) y frames de ~40 ms o más para pitch (modo narrowband).

---

## 3. Anatomía de cada panel

Ambos comparten ejes: **X = tiempo (0-163 s)**, **Y = frecuencia
(0-20.000 Hz)**, color naranja = energía. Solo cambia la ventana.

En nuestro tema:

- **Wideband:** rayas verticales cada ~0,15-0,3 s (el riff picando) sobre un
  fondo naranja continuo hasta ~15 kHz.
- **Narrowband:** familias de líneas horizontales: una grave (~100 Hz y
  múltiplos = bajo) y otra media (~300-1.000 Hz = lead).
- **Azul superior (15-20 kHz):** silencio en ambos. La fuente está limitada
  en banda (ver LPC_MANUAL): por encima no hay nada que transcribir.

---

## 4. Cómo leerlos paso a paso

**Paso 1. Cuenta rayas en el wideband.**
Elige 5 segundos y cuenta columnas verticales. Aquí salen ~30-60 en 10 s,
o sea un ataque cada ~0,15-0,3 s. Eso ya huele a corcheas a ~90-110 BPM sin
haber calculado nada.

**Paso 2. Busca familias de líneas en el narrowband.**
¿Una sola familia (una voz) o dos (bajo + lead)? Aquí dos: graves con
múltiplos densos (cuadrada del bajo) y medios con dibujo melódico (lead).

**Paso 3. Localiza el valle entre familias.**
La frontera visual entre ambas (~300 Hz) es tu `--xover`. Márcala.

**Paso 4. Mira hasta dónde llegan líneas con dibujo.**
Si por encima de ~1-2 kHz solo hay peine regular sin melodía, son armónicos:
el cap de 1.200 Hz del detector existe exactamente por esto.

**Paso 5. Cruza ambos paneles en un instante.**
Elige una raya del wideband (p. ej. t=12,4 s) y mira el narrowband ahí:
¿nace una línea horizontal nueva? Entonces es un onset real con nota nueva.
¿No nace nada? Era un golpe o un reataque de la misma nota.

---

## 5. Patrones típicos y qué significan

### Patrón A: rayas + dos familias (nuestro caso)

```
wideband:  │ │ │ │ │ │   (ataques regulares)
narrowband: ═══════  (graves, bajo)
            ───────  (medios, lead)
= riff + melodía. --voices 2, --xover en el valle.
```

### Patrón B: rayas sin líneas nuevas

```
wideband:  │ │ │ │ │ │
narrowband: ═══════════  (una línea continua, sin cambios)
= trémolo o redoble sobre la misma nota. El conversor tiende a partirla en
  muchas notas cortas: merge_short_notes las reunifica. No toques nada.
```

### Patrón C: líneas que nacen sin raya previa

```
wideband:  (nada, fondo liso)
narrowband:       ╭────────  (fade-in de una nota)
= entrada suave (cuerda, pad). El onset se detecta tarde: la nota sale
  corta o desplazada. Solo importa en música con ataques blandos; en
  chiptune es raro.
```

### Patrón D: manchas sin líneas ni rayas

```
ambos:  ░▒▓▒░▒▓▒░  (niebla)
= ruido o mezcla densa sin notas claras. No conviertas ese tramo.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el spec_wb_nb.png y confirma energía hasta ~15 kHz y azul arriba.
2. En el wideband, cuenta rayas entre los segundos 10 y 20: salen ~50 →
   un ataque cada ~0,2 s → corcheas a ~100 BPM. El --auto dirá 90.9: cuadra.
3. En el narrowband, identifica la familia grave (fundamental ~80-140 Hz con
   armónicos impares fuertes = cuadrada) y la media (dibujo que sube y baja
   = lead).
4. Marca el valle (~300 Hz): es el --xover del plugin ("120,480,1300" lo
   refina en 4 bandas).
5. Comprueba que por encima de ~1,5 kHz el peine es regular y sin dibujo:
   armónicos, no melodía. Cap de 1.200 Hz justificado.

---

## 7. Errores comunes al leerlos

1. **Leer armónicos como notas.**
   El error número uno. Una fundamental a 110 Hz pinta líneas en 110, 220,
   330, 440... No son 4 notas, es UNA. La guardia de octava del código
   existe por esto.

2. **Contar rayas de percusión como tempo.**
   Si hay hats a semicorcheas, el wideband los muestra y el BPM estimado se
   puede ir al doble. El --auto se defiende por alineación a rejilla, pero
   verifica a ojo.

3. **Pedirle al narrowband el timing exacto.**
   Sus líneas están borrosas en tiempo por construcción. El "cuándo" se lee
   arriba, el "qué" abajo. No al revés.

4. **Asumir que más líneas = más voces.**
   Una cuadrada solitaria ya pinta media docena de líneas. Voces se confirman
   con fundamentales independientes (pitch_voiced, CQT), no contando líneas.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **specgram** | El wideband con otra paleta; este añade el narrowband |
| **pitch_voiced** | Confirma que las líneas graves son el riff (70-140 Hz) |
| **intensity** | Las rayas coinciden con picos de energía |
| **zcr** | Cada raya debería tener su diente de cruces por cero |
| **cqt** | Las familias del narrowband, traducidas a notas |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Rayas cada X s | Estima BPM ≈ 60/(2X) si X es corchea; verifica el --auto |
| Dos familias de líneas | `--voices 2` (o `--xovers` para 4 bandas) |
| Valle entre familias | `--xover` / cortes de `--xovers` |
| Peine regular arriba sin dibujo | Cap 1.200 Hz (ya fijo en el detector) |
| Líneas que nacen sin raya | Sospecha ataques blandos; revisa duraciones a mano |

---

## 10. Nivel experto: el compromiso tiempo-frecuencia

Principio de incertidumbre tiempo-frecuencia: ventana corta = resolución
temporal ~5 ms pero bandas de ~200 Hz; ventana larga = resolución de ~10 Hz
pero borra ataques de menos de ~40 ms. No hay ventana perfecta: por eso el
pipeline usa dos escalas (hop 10 ms para onsets, frames largos para pitch)
igual que esta gráfica usa dos paneles.

Si un ataque corto "desaparece" del MIDI, cayó entre ventanas de pitch: baja
`--onset-hop`, no toques el pitch. Si una nota sale con frecuencia temblorosa,
la ventana de pitch es demasiado corta para ese grave: sube el frame mínimo
(o acepta que graves por debajo de ~40 Hz no son transcribibles con 48 kHz y
ventanas razonables).

---

## 11. Ejercicio práctico

1. Elige un segundo cualquiera (p. ej. t=33 s) y localiza su raya en el wideband.
2. En el narrowband, lista las líneas horizontales que nacen justo ahí con
   sus frecuencias aproximadas.
3. Convierte la más grave a MIDI a mano: `69 + 12·log2(f/440)`.
4. Busca ese MIDI y ese tiempo en el JSON: ¿lo encontró el conversor?
5. Repite con una línea aguda (> 1.500 Hz): ¿aparece en el JSON? (No debería:
   cap de 1.200 Hz. Si aparece, avisa.)

---

## 12. Preguntas frecuentes

**¿Por qué el narrowband se ve borroso en vertical?**
Porque cada columna integra ~40 ms: los ataques se untan. Es el precio del
detalle frecuencial.

**¿Y si las rayas no son regulares?**
Tempo libre o rubato: el BPM único del conversor sufrirá. Convierte tramos
cortos o acepta quantize suave.

**¿El azul de arriba es un problema?**
No: es ausencia de señal (fuente limitada a ~15 kHz). Problema sería que
hubiera energía arriba sin estructura (ruido de codificación fuerte).

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **Wideband** | Espectrograma de ventana corta: detalle temporal, onsets |
| **Narrowband** | Espectrograma de ventana larga: detalle frecuencial, armónicos |
| **Onset** | Instante de inicio de una nota o evento |
| **Ventana / hop** | Tamaño del fragmento analizado y salto entre análisis |
| **Compromiso tiempo-frecuencia** | No se puede tener máxima resolución en ambos ejes a la vez |

---

## 14. Chuleta final

```
wideband: rayas = onsets -> tempo y segmentacion
narrowband: lineas = notas + armonicos -> voces
dos familias -> --voices 2 / --xovers; valle = corte
peine arriba sin dibujo -> armonicos (cap 1200 Hz)
raya sin linea nueva -> golpe o reataque, no nota nueva
```
