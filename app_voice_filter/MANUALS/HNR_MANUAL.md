# HNR_MANUAL — Relación armónicos/ruido (hnr.png)

Guía completa: ¿esto que suena es nota o es ruido? De cero a experto.

---

## Tabla de contenidos

1. [¿Qué mide?](#1-qué-mide)
2. [Analogía: la emisora con interferencias](#2-analogía-la-emisora-con-interferencias)
3. [Anatomía: una línea en dB](#3-anatomía-una-línea-en-db)
4. [Cómo leerla paso a paso](#4-cómo-leerla-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerla](#7-errores-comunes-al-leerla)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: estimación y trampas](#10-nivel-experto-estimación-y-trampas)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿Qué mide?

El **HNR** (Harmonics-to-Noise Ratio) separa el sonido en dos partes: la
**periódica** (vibración regular = nota) y la **ruidosa** (soplo, golpe,
estática). El número, en dB, dice cuánta nota hay frente a cuánto ruido:

```
HNR > 15 dB   ████████████░░░░  tono casi puro (flauta, bajo synth)
HNR 5-15 dB   ██████░░░░░░░░░░  nota con carácter (lead cuadrado, voz)
HNR < 5 dB    ██░░░░░░░░░░░░░░  golpe/estática: NO hay nota que transcribir
```

---

## 2. Analogía: la emisora con interferencias

Escuchas una emisora de radio: a veces la música llega nítida (HNR alto),
a veces la tapa la fritura (HNR bajo). El HNR es el "medidor de cobertura"
del dial: no te dice qué canción suena (eso es el pitch), te dice si merece
la pena intentar oírla. Con cobertura baja, ni el mejor oído transcribe.

---

## 3. Anatomía: una línea en dB

- **X = tiempo (0-163 s)**, **Y = dB** (más alto = más nota frente a ruido).
- Línea alta y estable = notas claras todo el rato (nuestro chiptune limpio:
  bajo y lead sintéticos, casi sin percusión acústica).
- Valles = percusión, silencios con soplo, secciones ruidosas o efectos.

---

## 4. Cómo leerla paso a paso

**Paso 1. Mira el nivel medio.**
¿Alto (> 10 dB)? Tema melódico, conversión fiable. ¿Bajo (< 5 dB)? Textura
ruidosa: no esperes un MIDI limpio.

**Paso 2. Localiza los valles.**
Cada valle es un golpe, un silencio ruidoso o una sección con efectos.
Anota si son periódicos (batería: normal, se filtra) o sostenidos (sección
ruidosa: evita el tramo).

**Paso 3. Mira el final.**
¿Caída sostenida? Fade-out con ruido o cola de reverb: corta antes.

**Paso 4. Cruza con el voicing.**
Voicing alto + HNR alto = nota segura. Voicing alto + HNR bajo = "ruido
sonoro" (motor, zumbido): el pitch dirá una nota que no es música.

**Paso 5. Decide el tramo.**
El de HNR más alto y estable (aquí casi cualquiera de 0-60 s).

---

## 5. Patrones típicos y qué significan

### Patrón A: alto y plano (nuestro caso)

```
dB
 │ ────────────────────────────  (15-25 dB, pequeñas olas)
 └──────────────────────────────→
= tema melódico limpio. Convierte tranquilo: el detector trabaja a gusto.
```

### Patrón B: valles periódicos

```
 │ ──╲＿╱──╲＿╱──╲＿╱──
 └──────────────────→
= golpes de batería entre notas. Normal: se filtran con --min-conf solos.
  No subas el umbral por ellos o recortarás las notas vecinas.
```

### Patrón C: meseta baja sostenida

```
 │ ─────╲＿＿＿＿＿＿＿＿
 └──────────────────→
= sección ruidosa o de efectos. No conviertas ahí; busca otro tramo (ver
  selfsim para elegir bloque).
```

### Patrón D: dientes de sierra en el HNR

```
 │ ╱╲╱╲╱╲╱╲╱╲╱╲
 └──────────────────→
= alternancia nota/golpe rapidísima (riff con batería marcada). El MIDI
  saldrá bien si los golpes son cortos: filter_short_notes los entierra.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el hnr.png: línea alta y estable → chiptune limpio, sin percusión
   acústica que estorbe.
2. Busca valles: escasos y estrechos → sin secciones ruidosas que evitar.
3. Conclusión: cualquier tramo 0-60 s vale por HNR; el 65-100 s se evita por
   voicing (pitch_voiced), no por ruido.
4. Verifica en el JSON: confianzas medias 0,68-0,80 por voz, coherentes con
   HNR alto. Si alguna voz diera 0,3 con este HNR, el problema sería de
   bandas (--xovers), no de ruido.
5. Nota mental: si algún día conviertes gameplay (no este WAV), los disparos
   hundirán esta curva: vuelve a este manual entonces.

---

## 7. Errores comunes al leerla

1. **Exigir HNR de flauta a una cuadrada.**
   Las ondas cuadradas tienen armónicos impares fuertes que el estimador lee
   parcialmente como "ruido": HNR medio en notas perfectas. Es normal aquí,
   no un fallo.

2. **Confundir zumbido con nota.**
   Un motor con zumbido periódico da HNR alto sin ser música. Por eso el
   conversor no filtra por HNR sino por confianza de pitch + min-conf.

3. **Recortar valles a mano en el WAV.**
   Los valles periódicos se filtran solos. Editar el audio antes de
   convertir mete bordes que generan más fantasmas de los que quita.

4. **Usarla como umbral automático.**
   No hay número mágico universal: 8 dB es gloria en gameplay y mediocridad
   en estudio. Lectura comparativa entre tramos, no absoluta.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **pitch_voiced** | Si discrepan (voicing alto + HNR bajo), desconfía del pitch |
| **flatness** | Cuentan lo mismo por caminos distintos; si ambas acusan un tramo, créelas |
| **intensity** | Valles de HNR sobre picos de energía = golpes |
| **zcr** | Ruido: HNR bajo + ZCR alto; nota aguda: HNR medio-alto + ZCR alto |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| HNR alto y plano | Convierte; `--min-conf` bajo (0,15) |
| Valles periódicos | Nada (se filtran solos) |
| Meseta baja | Cambia de tramo (ver selfsim) |
| HNR bajo con voicing alto | Sospecha SFX periódicos: revisa con oído, posible regla de plugin |

---

## 10. Nivel experto: estimación y trampas

Estimación típica: de la autocorrelación normalizada, `HNR = pico/(1-pico)`
en el lag del pitch, en dB. Trampas documentadas:

- **Cuadradas:** armónicos impares → HNR 5-15 dB en notas perfectas. Calibra
  tu ojo a este tema, no a valores de libro de voz.
- **Transitorios:** un ataque tiene HNR bajo 10-20 ms aunque sea nota
  legítima. Por eso el pitch se mide en el SUSTAIN (40 ms tras el onset),
  no en el ataque.
- **Doble voz:** dos notas a la vez bajan el HNR mutuo (cada una es "ruido"
  para la otra). Con --voices 2-4, exige menos HNR que en monofónico.

Por eso el conversor no filtra por HNR directamente: es **diagnóstico**, no
umbral. Su lectura correcta decide tramos y explica confianzas, no recorta
notas.

---

## 11. Ejercicio práctico

1. Estima el HNR medio a ojo y califícalo (alto/medio/bajo).
2. Cuenta valles que bajen de 5 dB: ¿periódicos o sostenidos?
3. Toma la voz con menor confianza del JSON: ¿coincide con algún valle?
4. Elige el mejor tramo de 20 s solo con esta curva y compáralo con el
   elegido por voicing (0-20 s). ¿Coinciden?
5. Si conviertes gameplay alguna vez, repite este ejercicio: verás la
   diferencia entre música y SFX en esta curva antes que en ninguna otra.

---

## 12. Preguntas frecuentes

**¿HNR o flatness para detectar ruido?**
Ambos; HNR asume periodicidad (mejor con música), flatness no (mejor con
ruido puro). Juntos no fallan.

**¿Un HNR bajo invalida el tramo?**
Si es sostenido, sí. Si son valles periódicos, no: es la batería haciendo
su trabajo.

**¿Por qué no filtra el código por HNR?**
Por las trampas de arriba (cuadradas, transitorios, doble voz). La
confianza de pitch + min-conf ya incluye esa información de forma más
robusta.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **HNR** | Harmonics-to-Noise Ratio, en dB: nota frente a ruido |
| **SUSTAIN** | Zona estable tras el ataque (40 ms), donde se mide el pitch |
| **Transitorio** | Ataque breve; HNR bajo legítimo de ~10-20 ms |
| **Unísono** | Dos voces en la misma nota (HNR y voicing no las separan) |

---

## 14. Chuleta final

```
HNR alto y plano = convierte tranquilo
valles periodicos = bateria, se filtran solos
meseta baja = cambia de tramo
cuadradas dan HNR medio: normal, no fallo
diagnostico, no umbral
```
