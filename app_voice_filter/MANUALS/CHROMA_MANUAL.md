# CHROMA_MANUAL — Cromagrama (chroma.png)

Guía completa: qué notas suenan sin importar la octava, de cero a experto.

---

## Tabla de contenidos

1. [¿Qué es?](#1-qué-es)
2. [Analogía: el coro por cuerdas](#2-analogía-el-coro-por-cuerdas)
3. [Anatomía: 12 filas](#3-anatomía-12-filas)
4. [Cómo leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: plegado por octavas y armónicos mentirosos](#10-nivel-experto-plegado-por-octavas-y-armónicos-mentirosos)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué es?

Doce filas, una por cada nota (C, C#, D, D#, E, F, F#, G, G#, A, A#, B),
**sin importar la octava**: un Do grave y un Do agudo encienden la misma
fila. Es resumir una orquesta anotando solo qué letras se tocan, ignorando
si las toca el contrabajo o el violín. Responde a una pregunta: **¿en qué
tono está el tema y qué notas usa?**

```
Octavas reales:          Chroma (plegado):
E1  E2  E3  E4           E  ████████████  (todo suma aquí)
G1  G2                   G  ██████░░░░░░
B1                       B  ████░░░░░░░░
```

---

## 2. Analogía: el coro por cuerdas

Imagina un coro dividido en 12 grupos, uno por nota. Cada grupo canta cuando
su nota suena en cualquier octava. El director (tú) mira qué grupos tienen la
boca abierta: si el grupo MI canta siempre y los demás callan, el tema está
en MI. No sabes si cantan sopranos o bajos (eso lo dice el pitch), pero sabes
**el vocabulario**.

---

## 3. Anatomía: 12 filas

- **X = tiempo (0-163 s).**
- **Y = las 12 clases de nota** (C abajo → B arriba, según implementación).
- Fila brillante = esa nota suena mucho en ese momento.
- En nuestro tema la fila de **E** arde de principio a fin: Peter Gunn en MI,
  con F, F#, G y A acompañando (el riff E-F-F#-G... y respuestas).

---

## 4. Cómo leerlo paso a paso

**Paso 1. Busca la fila más brillante en conjunto.**
Esa es la tónica (aquí E). Ya sabes el tono del tema en 10 segundos.

**Paso 2. Lista sus compañeras.**
¿Qué 2-4 filas más se encienden? Son el vocabulario (aquí F, F#, G, A).
Pocas filas = tema simple = JSON pequeño.

**Paso 3. Mira si cambian con el tiempo.**
¿Las mismas filas 163 s? Un solo centro tonal. ¿Cambian por bloques (~90 s,
~112 s)? Secciones con distinto material: confirma con selfsim.

**Paso 4. Detecta intrusos.**
¿Una fila que se enciende sola un instante (p. ej. D# perdido)? Candidata a
artefacto o nota de paso. Verifícala en pitch_voiced antes de creerla.

**Paso 5. Compara con el MIDI final.**
Toda nota del JSON debería pertenecer a las filas activas de su instante.
Si no, es fantasma.

---

## 5. Patrones típicos y qué significan

### Patrón A: una fila reina + corte (nuestro caso)

```
B  ···············
A  ████··████·····
G  ██████··██████·
F# ··██████··█████
F  ····█████████··
E  ███████████████  ← tónica
   └──────────────→
= riff en MI con vocabulario de 5 notas. Chiptune de manual.
```

### Patrón B: dos filas alternas

```
A  ████····████···
E  ····████····███
= pregunta-respuesta entre dos notas (ostinato). El loop es trivial y el
  JSON mínimo.
```

### Patrón C: todas encendidas

```
   ███████████████  (las 12)
= ruido, percusión densa o cluster. No hay melodía que transcribir aquí.
```

### Patrón D: franjas que cambian por bloques

```
   sección1: E F F# G | sección2: A B C D
= modulación o puente. Convierte cada bloque aparte o acepta vocabulario
  doble.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el chroma.png: fila E encendida siempre → tono MI.
2. Acompañantes: F, F#, G, A → el riff y sus grados vecinos. Vocabulario
   de ~5 clases = tema simple.
3. Recorre el tiempo: mismas filas 0-90 s, cambio ~90-112 s (puente),
   vuelta después → las 3 secciones del selfsim, vistas por notas.
4. Predice el JSON: notas en MI con alteraciones vecinas, nada de D# o B
   sostenidos sueltos. Si el MIDI trae uno, es artefacto (el plugin con
   LEAD_CAP y min-conf los elimina).
5. Comprueba: el vocabulario final (~35 MIDIs) son esas 5 clases en varias
   octavas. Cuadra.

---

## 7. Errores comunes al leerlo

1. **Creerse una fila tenue.**
   Los armónicos de cuadrada (3º = quinta, 5º = tercera) encienden filas que
   nadie toca: un bajo en E "ensucia" B y G#. Tenue + sin apoyo en
   pitch_voiced = mentira armónica.

2. **Pedirle la octava.**
   El chroma no sabe si es E2 o E4. Para octavas, CQT/pitch.

3. **Confundir nota de paso con modulación.**
   Una fila que parpadea un instante es un cromatismo del riff, no un cambio
   de tono. Modulación = bloque entero sostenido.

4. **Usarlo solo.**
   Chroma dice la familia; pitch_voiced dice si hay nota real. Juntos
   deciden, separados opinan.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **cqt** | El chroma es la CQT plegada por octavas |
| **pitch_voiced** | La nota exacta con octava; el chroma, la familia |
| **selfsim** | Los cambios de filas marcan las secciones |
| **mfcc** | Allí timbre, aquí notas: complementarios |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Filas definidas | Hay melodía real: convierte |
| 3-5 filas | Tema simple, JSON pequeño, chiptune ideal |
| Sopa uniforme | Sin melodía clara: no conviertas ese tramo |
| Nota MIDI fuera de filas activas | Candidata a artefacto (filtro futuro por chroma) |

---

## 10. Nivel experto: plegado por octavas y armónicos mentirosos

Cálculo: se suma la energía del espectro en cada clase `f → clase(f)`,
típicamente con ventana y normalización por frame. El veneno está en los
armónicos impares de la cuadrada: el 3er armónico de E cae en B (una
duodécima arriba) y el 5º en G#. Con bajo fuerte, B y G# aparecen "tocadas"
al 20-30 % de E. Por eso el conversor no filtra por chroma por defecto:
antes habría que modelar la plantilla armónica de cada voz (trabajo futuro;
el primer paso sería ponderar 1, 1/3, 1/5... según serie de Fourier de la
cuadrada). Mientras tanto: chroma para **diagnóstico y tono**, pitch para
**decisiones**.

---

## 11. Ejercicio práctico

1. Identifica la tónica y sus 4 compañeras en el chroma.
2. Traduce el riff E-F-F#-G a clases y búscalo en los primeros 20 s.
3. Localiza el bloque ~90-112 s: ¿qué filas cambian? ¿vuelve E después?
4. Toma 5 notas al azar del JSON y verifica que cada una pertenezca a una
   fila activa de su instante.
5. Si alguna no pertenece: ¿armónico (3º/5º del bajo) o fantasma total?

---

## 12. Preguntas frecuentes

**¿12 filas siempre?**
En música occidental sí. Otras tradiciones necesitarían más (cuartos de
tono), fuera del alcance chiptune.

**¿Por qué E y no otra?**
Porque la fila E es la más brillante en el tiempo total. Tónica = moda
ponderada por energía, no la primera nota.

**¿Sirve para el BPM?**
No. Para tempo, onsets.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **Clase de pitch** | Nota sin octava (los 12 nombres) |
| **Tónica** | Nota central del tono (aquí E) |
| **Plegado por octavas** | Sumar todas las octavas en 12 filas |
| **Cromatismo** | Nota fuera de la escala, de paso |
| **Plantilla armónica** | Patrón de armónicos esperado de un timbre |

---

## 14. Chuleta final

```
fila siempre viva = tonica (aqui E)
3-5 filas = tema simple, JSON pequeno
todas las filas = ruido o percusion
fila tenue = verifica en pitch_voiced (puede ser armonico)
nota fuera de filas activas = fantasma
```
