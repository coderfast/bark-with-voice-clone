# PITCH_VOICED_MANUAL — Pitch con probabilidad de sonoridad (pitch_voiced.png)

Guía completa: la melodía en la que puedes confiar, de cero a experto.

---

## Tabla de contenidos

1. [¿Qué añade respecto a pitch.png?](#1-qué-añade-respecto-a-pitchpng)
2. [Analogía: el testigo que dice cuándo duda](#2-analogía-el-testigo-que-dice-cuándo-duda)
3. [Anatomía: dos paneles](#3-anatomía-dos-paneles)
4. [Cómo leerlos paso a paso](#4-cómo-leerlos-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlos](#7-errores-comunes-al-leerlos)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: de qué está hecho el voicing](#10-nivel-experto-de-qué-está-hecho-el-voicing)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué añade respecto a pitch.png?

Dos paneles: arriba la misma curva de pitch, abajo la **probabilidad de que
haya realmente una nota sonando** (voicing, de 0 a 1). Es la diferencia entre
un testigo que habla siempre y uno que además **dice cuándo está seguro**.
Regla de oro: **solo se transcribe donde la curva de abajo esté alta**.

```
Arriba (pitch, Hz):    ╭─╮   ╭─╮   · · ·   ╭─╮
                    ───╯ ╰───╯ ╰── · · · ──╯ ╰──
Abajo (voicing):   ████████   ░░░░░░░░   ██████
                   seguro     duda: NO    seguro
                   TRANSCRIBIR  transcribir  TRANSCRIBIR
```

---

## 2. Analogía: el testigo que dice cuándo duda

Un testigo normal responde a todo, inventando cuando no sabe (pitch solo).
Un buen testigo dice "esto lo vi claro" y "esto no lo juro" (voiced). El juez
(el conversor, vía `--min-conf`) solo admite lo jurado. Esta gráfica es la
transcripción con las partes juradas subrayadas.

---

## 3. Anatomía: dos paneles

- **Panel superior:** tiempo (X, 0-163 s) contra frecuencia (Y, Hz). Igual
  que pitch.png: riff 70-140 Hz, lead arriba.
- **Panel inferior:** tiempo (X) contra probabilidad (Y, 0-1). Zonas pegadas
  al 1 = nota clara; pegadas al 0 = silencio, ruido o pausa.
- En nuestro tema el voicing está alto casi siempre (riff continuo, tasa
  ~0,99 en tema entero) y cae en 65-100 s: ahí el detector duda y hay que
  filtrar.

---

## 4. Cómo leerlos paso a paso

**Paso 1. Recorre solo el panel inferior.**
Marca tramos altos (verdes) y bajos (rojos). Los altos son tu terreno de
conversión; los bajos, tierra de nadie.

**Paso 2. Para cada tramo alto, sube al superior.**
¿Hay línea estable? Nota sólida: anota registro (grave → voz0-1, agudo →
voz2). ¿Hay nube? Contradicción: desconfía (ver HNR para desempatar).

**Paso 3. Mide la tasa global a ojo.**
¿Qué % del tiempo está alto? > 70 % → `--min-conf` 0,15 basta. Con caídas
largas → 0,25-0,35. (`--auto` lo calcula solo: voicing 0,987 → 0,15.)

**Paso 4. Busca parpadeo rápido.**
Voicing que sube y baja a cada nota = staccato o trémolo: las notas son
cortas de verdad, no un fallo. No las alargues a mano.

**Paso 5. Elige el tramo de conversión.**
El más largo con voicing alto y continuo (0-60 s aquí). Todo MIDI nacido
fuera de él debe justificarse.

---

## 5. Patrones típicos y qué significan

### Patrón A: alto + línea estable (nuestro riff)

```
arriba: ──╭─╮──╭─╮──
abajo:  ████████████
= nota sólida. Transcribir sin miedo: saldrá con confianza 0,7-0,9.
```

### Patrón B: bajo + nube

```
arriba:  · · · · · ·
abajo:  ░░░░░░░░░░░░
= ruido/pausa. No transcribir. Todo lo que salga de aquí es fantasma
  (aquí nacían los A8/D9 de la v1).
```

### Patrón C: parpadeo

```
abajo:  ██░██░██░██░
= staccato/trémolo real. Notas cortas legítimas: que filter_short_notes
  (0,04 s) decida, no tu ojo.
```

### Patrón D: huecos regulares largos

```
abajo:  ██████░░░░██████░░░░
= fraseo con pausas. Respetan el ritmo: son los silencios de la partitura,
  no fallos. El SONG los reproduce como aire entre notas.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el pitch_voiced.png y recorre el panel inferior: alto 0-65 s, caída
   65-100 s, alto después.
2. Tasa global ~0,99 → `--min-conf` 0,15 (lo que ponen --auto y el plugin).
3. Tramo elegido 0-20 s: voicing alto y continuo → conversión fiable.
4. Predice: voz0 densa (conf ~0,8), voz1-2 presentes, pocos fantasmas. Real:
   voz0 1.015 conf 0,80; voz1 749 conf 0,68; voz2 734 conf 0,71. Cuadra.
5. Si alguna nota del JSON tiene confianza < 0,3, busca su instante abajo:
   estará en una caída. Diagnóstico cerrado.

---

## 7. Errores comunes al leerlos

1. **Leer solo el panel superior.**
   Es pitch.png disfrazado. El valor de esta gráfica es el inferior.

2. **Pedirle voces.**
   El voicing no separa voces: dos voces suenan "voiced" igual que una.
   Para voces, bandas (mel) y registros (CQT).

3. **Alisar el parpadeo a mano.**
   El staccato es música, no ruido. El umbral decide nota a nota.

4. **Confundir caída con final.**
   Una caída en medio del tema (65-100 s) es pasaje dudoso, no final: el
   tema vuelve. No recortes el WAV ahí por error.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **pitch** | La curva sin semáforo; aquí diagnosticas, allí decides |
| **hnr** | Voicing alto + HNR alto = nota; si discrepan, desconfía del pitch |
| **intensity** | Los huecos de voicing suelen ir sobre valles de energía |
| **flatness** | Donde pica, el voicing debería caer; si no cae, optimismo del detector |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Voicing medio > 0,7 | `--min-conf` 0,15 |
| Caídas largas | `--min-conf` 0,25-0,35 |
| Tramo alto y continuo | Candidato a t0-t1 (aquí 0-20 s) |
| Saltos de registro con voicing alto | 2+ voces reales |

---

## 10. Nivel experto: de qué está hecho el voicing

Combina tres señales por ventana: RMS (¿hay energía?), fuerza del pico de
autocorrelación (¿hay periodo?) y continuidad con vecinos (¿dura?). Sus
puntos ciegos:

- **Reverb larga:** mantiene voicing alto tras el fin de la nota → colas que
  alargan duraciones. Defensa: release del ADSR corto y oído en el player.
- **Ruido impulsivo:** levanta el voicing un instante → notas cortas
  fantasma. Defensa: `filter_short_notes(min_dur=0.04)`.
- **Unísonos:** dos voces al unísono dan voicing 1 con una sola línea: el
  conversor verá una nota donde hay dos. Indetectable aquí; aceptable en
  chiptune (suenan igual).

Si ves notas de 0,03 s en el JSON sin joroba de voicing en su instante, son
del segundo punto ciego: sube `--min-conf`, no toques el pitch.

---

## 11. Ejercicio práctico

1. Estima la tasa de voicing a ojo (aquí ~0,99) y deduce el min-conf.
2. Localiza la caída 65-100 s: ¿qué notas del JSON nacen ahí? ¿confianza?
3. Elige 3 notas con confianza < 0,4 y verifica su instante en el panel
   inferior.
4. Busca parpadeo: ¿staccato real o ruido? Decide con duraciones del JSON.
5. Propón el t0-t1 ideal para una versión corta del SONG (pista: dentro de
   0-60 s).

---

## 12. Preguntas frecuentes

**¿Voicing 1 = nota correcta?**
No: = "hay algo periódico". La octava puede estar mal (ver guardia) o ser
un motor zumbando. Necesita al pitch de aliado.

**¿Por qué 0,15 y no 0,5?**
Porque en chiptune limpio casi todo es nota real; un umbral alto solo
recorta colas y matices. En gameplay ruidoso sí subiría a 0,3-0,4.

**¿El plugin puede usar el voicing?**
Hoy el plugin filtra por eventos (post), no por voicing. Mejora futura:
pasarle la curva para vetos por tramo.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **Voicing** | Probabilidad de que haya una nota sonando (0-1) |
| **min-conf** | Umbral de confianza mínima para aceptar la nota |
| **Staccato** | Notas cortas separadas por silencios |
| **Joroba de voicing** | Elevación local de la curva = nota candidata |
| **Tasa de voicing** | Fracción del tiempo con voicing alto |

---

## 14. Chuleta final

```
arriba nota + abajo ~1 = transcribir
abajo ~0 = no transcribir, diga lo que diga arriba
tasa alta -> --min-conf 0.15; con caidas -> 0.25-0.35
convierte tramos altos y continuos
parpadeo = staccato, no ruido
```
