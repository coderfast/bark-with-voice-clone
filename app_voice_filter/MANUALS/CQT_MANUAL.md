# CQT_MANUAL — Transformada de Q constante (cqt.png)

Guía completa: el espectrograma afinado como un piano, de cero a experto.

---

## Tabla de contenidos

1. [¿Qué tiene de especial?](#1-qué-tiene-de-especial)
2. [Analogía: el piano estirado](#2-analogía-el-piano-estirado)
3. [Anatomía: ejes y bloques](#3-anatomía-ejes-y-bloques)
4. [Cómo leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: la CQT como verdad visual](#10-nivel-experto-la-cqt-como-verdad-visual)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué tiene de especial?

En un piano cada octava ocupa el mismo espacio aunque sus frecuencias se
dupliquen (110, 220, 440, 880 Hz...). La **CQT** (Constant-Q Transform) hace
lo mismo con el eje vertical: **cada nota ocupa el mismo alto**, esté grave
o aguda. Es el espectrograma "traducido a partitura":

```
Lineal: la misma nota en 3 octavas      CQT: la misma nota en 3 octavas
Hz                                      Nota
880 ─┐                                    ─┐
     │ mucho espacio                       │ mismo alto
440 ─┤                                     │ mismo alto
     │                                     │
220 ─┤ poco espacio                        │ mismo alto
     └────────→ t                          └────────→ t
```

Un arpegio se ve como una **escalera**, un acorde como una **columna**, una
nota tenida como un **ladrillo**. Si sabes leer una partitura de piano-roll,
ya sabes leer una CQT.

---

## 2. Analogía: el piano estirado

Imagina un piano de cola estirado hasta medir 163 segundos de largo: cada
tecla es una fila, el tiempo avanza a la derecha, y cada vez que suena una
tecla se ilumina su casilla. La foto desde arriba de ese piano mágico es la
CQT. Las teclas graves abajo, las agudas arriba, y la música dibujando
caminos de luz.

---

## 3. Anatomía: ejes y bloques

- **X = tiempo (0-163 s).**
- **Y = frecuencia logarítmica (nota musical):** las etiquetas crecen por
  octavas. Dos bloques a la misma altura relativa en octavas distintas = la
  misma nota en otra octava (p. ej. E2 abajo y E4 arriba).
- **Bloques sólidos** = notas tenidas; **escaleras** = arpegios y riffs que
  suben/bajan; **columnas** = varias notas a la vez (acorde o coincidencia
  bajo+lead).

En nuestro tema: bloques graves repitiéndose (riff E-E-G... del Peter Gunn)
y actividad una o dos octavas arriba cuando entra el lead.

---

## 4. Cómo leerlo paso a paso

**Paso 1. Busca el registro grave.**
Abajo del todo, ¿hay bloques repitiéndose? Son el riff. Anota su altura
relativa: es la tónica del tema (MI aquí).

**Paso 2. Busca actividad una octava (o dos) arriba.**
¿Hay bloques que aparecen y desaparecen? Es el lead. Si suenan a la vez que
el bajo en vertical → `--voices 2` (o 4 bandas). Si se turnan → 1 voz basta.

**Paso 3. Cuenta el vocabulario.**
¿Cuántos bloques a distintas alturas? Si son ~10-15 notas repetidas, el JSON
será diminuto: perfecto para HTML5. (Aquí ~35 MIDIs únicos en el tema
entero.)

**Paso 4. Mide el loop.**
¿Cada cuántos segundos se repite el mismo dibujo? Aquí ~12-15 s: el ciclo
del Peter Gunn, como dice el selfsim.

**Paso 5. Marca lo sospechoso.**
Bloques aislados muy arriba sin familia abajo = candidatos a armónicos.
Bloques de 1 píxel de ancho = transitorios, no notas.

---

## 5. Patrones típicos y qué significan

### Patrón A: ladrillos graves en loop (nuestro riff)

```
octava 3   · · · ■ · · ■ · ·     (lead, entra y sale)
octava 2   ■ ■ ■ ■ ■ ■ ■ ■ ■     (riff medio)
octava 1   ■ ■ ■ ■ ■ ■ ■ ■ ■     (bajo, siempre)
           └──────────────→ t
= bajo continuo + lead por frases. 4 bandas finas lo parten limpio.
```

### Patrón B: escaleras

```
           · · · · ■
           · · · ■ ·
           · · ■ · ·
           · ■ · · ·
           └────────→
= arpegio. Cada peldaño una nota: el conversor debe dar una secuencia, no
  un acorde. Si sale un acorde, los onsets van tarde (--onset-hop).
```

### Patrón C: columnas

```
           ■ ■ ■
           ■ ■ ■
           ■ ■ ■
           └────→
= varias notas simultáneas. Con 2+ voces y bandas bien puestas salen
  repartidas; con 1 voz sale una sola (la más fuerte).
```

### Patrón D: polvo arriba

```
           · · · · · · · · · · ·  (puntitos sin estructura)
           ────────────────────  (música real abajo)
= armónicos y transitorios. No son melodía: el cap de 1.200 Hz los ignora.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el cqt.png y localiza los ladrillos graves: se repiten idénticos
   cada ~12-15 s (el loop).
2. Sube una octava: el mismo dibujo desplazado = el riff doblado arriba en
   algunas frases.
3. Sube otra: bloques sueltos del lead, solo en secciones (0-90 s sí,
   90-112 s distinto).
4. Cuenta alturas distintas con bloques sólidos: ~35 en todo el tema =
   vocabulario del JSON final.
5. Busca polvo arriba sin contrapartida: armónicos de cuadrada. El MIDI
   final no los trae (cap 1.200 Hz + LEAD_CAP 87 del plugin). Verdad visual
   confirmada.

---

## 7. Errores comunes al leerlo

1. **Leer armónicos como melodía aguda.**
   Todo bloque alto con gemelo exacto una octava abajo es sospechoso de
   armónico. Regla: sin familia propia (ataque propio, ritmo propio), no es
   voz.

2. **Confundir resolución con realidad.**
   La CQT interpola entre bins: un bloque "gordo" puede ser una sola nota con
   vibrato o dos semitonos vecinos. Para la nota exacta, pitch_voiced.

3. **Ignorar la octava.**
   Dos bloques iguales a distinta altura pueden ser la misma nota doblada
   (arreglo) o un error de octava del detector. El contexto rítmico decide:
   ¿dobla el riff (arreglo) o sustituye a la fundamental (error)?

4. **Pedirle timing fino.**
   Los bordes de bloque tienen la resolución de la ventana (~20-40 ms). Para
   onsets exactos, wideband.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **chroma** | La CQT plegada por octavas (12 filas). Misma lectura, menos detalle |
| **pitch_voiced** | Una sola línea melódica; la CQT muestra todas las capas |
| **selfsim** | Confirma que los bloques se repiten en loop |
| **mel** | Las franjas de la mel, traducidas a notas aquí |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Bloques graves + agudos simultáneos | `--voices 2` / `--xovers` |
| Vocabulario pequeño y repetido | JSON pequeño: apto HTML5 sin recortes |
| Rango de bloques sólidos | `--lo` / `--hi` (aquí 40 / 1.200) |
| Polvo arriba sin familia | Cap de lead (ya fijo a 1.200 Hz) |
| Columnas que salen como una nota | Sube `--voices` o revisa `--xovers` |

---

## 10. Nivel experto: la CQT como verdad visual

La CQT es lo más cercano a lo que el conversor intenta producir: una rejilla
tiempo×nota. Úsala como **auditoría**:

- MIDI dice A8 (117) pero aquí no hay bloque a esa altura → artefacto de
  octava: endurece `octave_guard` o baja `--hi`.
- Bloque sólido aquí ausente en el MIDI → `--min-conf` alto o onset que
  partió la nota (`--onset-hop`, `merge_short_notes`).
- Nota con duración la mitad que su bloque → onset fantasma en medio
  (reverberación o vibrato): ajusta `--onset-hop` o el umbral de flux.

Cálculo: Q constante = f/Δf igual en todas las bandas (típicamente 12-36 por
octava); ventanas largas abajo y cortas arriba, al revés que la FFT. Por eso
los graves salen nítidos en altura pero borrosos en tiempo: complementa con
el wideband para ataques.

---

## 11. Ejercicio práctico

1. Elige un bloque grave sólido y anota tiempo + octava.
2. Busca su gemelo una octava arriba en el mismo instante: ¿existe? ¿Es
   armónico o doblaje del arreglo? (Pista: si tiene su propio ritmo
   después, es arreglo.)
3. Traduce su altura a MIDI aproximado y búscalo en el JSON a ese tiempo.
4. Mide con el dedo el periodo del loop (dibujo que se repite).
5. Compara con SONG.dur y con el selfsim.

---

## 12. Preguntas frecuentes

**¿CQT o chroma para saber el tono?**
Chroma (más simple). CQT para saber las notas con octava.

**¿Por qué se ve borroso abajo?**
Ventanas largas en graves = borrosidad temporal. Física, no bug.

**¿Cuántos bins por octava tiene esta imagen?**
Típicamente 12 (uno por semitono) o 36. Con 12, cada fila es un semitono:
lectura directa a MIDI.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **CQT** | Transformada de Q constante: resolución logarítmica en frecuencia |
| **Q** | Factor de calidad f/Δf, constante en todas las bandas aquí |
| **Piano-roll** | Representación tiempo×nota de la música (lo que la CQT parece) |
| **Bloque / ladrillo** | Nota tenida en la CQT |
| **Polvo** | Puntos de alta frecuencia sin estructura: armónicos/transitorios |

---

## 14. Chuleta final

```
bloques = notas; escaleras = arpegios; columnas = acordes
misma forma otra octava = mismo dibujo desplazado en Y
bloque alto sin familia -> armonico, no melodia
bloque visible ausente en MIDI -> baja --min-conf
polvo arriba -> cap 1200 Hz
```
