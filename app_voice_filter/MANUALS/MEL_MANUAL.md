# MEL_MANUAL — Espectrograma en escala Mel (mel.png)

Guía completa: el espectrograma visto con oídos humanos, de cero a experto.

---

## Tabla de contenidos

1. [¿En qué se diferencia del specgram normal?](#1-en-qué-se-diferencia-del-specgram-normal)
2. [Analogía: el mapa con tu barrio gigante](#2-analogía-el-mapa-con-tu-barrio-gigante)
3. [Anatomía: ejes y franjas](#3-anatomía-ejes-y-franjas)
4. [Cómo leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones típicos y qué significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relación con las demás gráficas](#8-relación-con-las-demás-gráficas)
9. [De la gráfica a los parámetros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: Mel, filtros y el --auto](#10-nivel-experto-mel-filtros-y-el---auto)
11. [Ejercicio práctico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rápido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. ¿En qué se diferencia del specgram normal?

El oído humano no reparte su atención por igual: distingue 100 de 110 Hz sin
esfuerzo, pero 10.000 de 10.100 Hz le suenan idénticos. La **escala Mel**
deforma el eje de frecuencias para imitarlo: **expande los graves y comprime
los agudos**.

```
Lineal (specgram):            Mel (esta gráfica):
Hz                            Hz (equivalentes)
20000 ─┐                       ─┐
       │ agudos                    16000 ─┤ comprimidos
10000 ─┤  (mucho                      │  (poco espacio,
       │   espacio)                4000 ─┤   poco interés)
 5000 ─┤                           1000 ─┤
       │ graves                     250 ─┤ expandidos
  100 ─┘  (poco                       60 ─┘ (mucho detalle
            espacio)                          donde vive la música)
```

Consecuencia: la zona musical (bajo + lead, bajo 2 kHz) ocupa la mitad del
alto y se lee de un vistazo. Todo lo de arriba queda como "contexto".

---

## 2. Analogía: el mapa con tu barrio gigante

Es un mapa donde **tu barrio sale gigante y el resto del país encogido**,
porque es lo que te importa. Los graves son tu barrio (ahí viven bajo,
bombo, cuerpo de la melodía); los agudos son el resto del país (brillo,
aire, armónicos). El mapa Mel miente en las distancias para decirte la
verdad sobre lo importante.

---

## 3. Anatomía: ejes y franjas

- **X = tiempo (0-163 s)**, igual que siempre.
- **Y = frecuencia en escala Mel**, etiquetada en Hz equivalentes. Ojo: las
  marcas 60-1.000 Hz ocupan tanto alto como 4.000-16.000 Hz. No midas
  distancias verticales como si fueran lineales.
- **Franja baja gruesa y continua** = riff de bajo en loop (nuestro caso).
- **Franja media con dibujos** = lead con su melodía y sus armónicos.
- **Meseta tenue arriba** = aire y armónicos lejanos, sin información
  melódica.

---

## 4. Cómo leerlo paso a paso

**Paso 1. Localiza las franjas vivas.**
¿Cuántas hay y a qué altura? Aquí dos: baja (bajo) y media (lead). Dos
franjas = dos voces. Una sola = monofónico.

**Paso 2. Busca el valle entre ellas.**
El punto de menor energía entre franja baja y media (~300 Hz aquí) es tu
`--xover`. Es el corte que menos notas parte por la mitad.

**Paso 3. Sube hasta que se acabe el dibujo.**
Donde las franjas con forma se convierten en niebla uniforme, pon el cap:
aquí ~1.200 Hz para el detector de lead (`--hi` documenta el rango, el
detector capa a 1.200 fijo).

**Paso 4. Mira si las franjas cambian con el tiempo.**
¿Se mantienen 163 s? Arreglo único, un JSON coherente. ¿Se cortan o cambian
(~90 s, ~112 s)? Secciones: convierte dentro de una sola (ver selfsim).

**Paso 5. Compara anchos.**
Franja baja gorda y estable = bajo presente siempre (confianza alta en voz0:
0.80 en nuestra conversión). Franja media con altibajos = lead que entra y
sale (voz1 con menos notas: 749 contra 1.015... en 4 bandas se reparte más).

---

## 5. Patrones típicos y qué significan

### Patrón A: dos franjas estables (nuestro caso)

```
 Mel alto  ·············  niebla (aire)
         ═════════════  franja media (lead)
         ─────────────  valle (~300 Hz = xover)
         █████████████  franja baja (bajo en loop)
         └──────────────→ t
= bajo + lead. --voices 2 o 4 bandas finas. Caso ideal chiptune.
```

### Patrón B: una sola franja

```
         ·············  (vacío arriba)
         █████████████  una franja
         └──────────────→
= monofónico. --voices 1: forzar dos voces crea notas fantasma de la nada.
```

### Patrón C: franjas que se tocan sin valle

```
         █████████████
         █████████████  (pegadas, sin hueco)
         └──────────────→
= bajo y lead solapados en frecuencia. El corte es delicado: prueba --voices
  1 primero, y 2 solo si el oído lo pide.
```

### Patrón D: destellos verticales en toda la altura

```
         │  │    │  │   (columnas que cruzan todo)
         └──────────────→
= golpes o ruido de banda ancha. En tema limpio son escasos; en gameplay
  abundan (disparos, choques): confirma con HNR antes de convertir.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. Abre el mel.png: dos franjas abajo, niebla arriba. Dos voces.
2. Estima el valle entre franjas: cae ~300 Hz → `--xover 300` (y el plugin
   refina a 4 bandas con "120,480,1300").
3. Sube por la franja media hasta que pierde dibujo: ~1.200 Hz → cap del
   detector justificado a ojo.
4. Recorre el tiempo: franjas continuas 0-90 s, cambio ~90-112 s, vuelta
   después → el tramo 0-20 s vive dentro de un bloque (ver selfsim).
5. Predice: voz0 densa y confiada, voz1 con menos notas. La conversión real:
   voz0 1.015 notas conf 0.80, voz1 749 conf 0.68. La gráfica no mentía.

---

## 7. Errores comunes al leerlo

1. **Medir Hz en vertical como si fuera lineal.**
   En Mel, 5 cm arriba no son "5 veces más Hz". Lee las etiquetas, no las
   distancias.

2. **Llamar "nota" a la niebla de arriba.**
   Sin dibujo no hay melodía, por brillante que se vea. Niebla = aire.

3. **Poner el corte en la franja en vez de en el valle.**
   Un --xover dentro de una franja parte notas por la mitad y duplica
   eventos. Siempre en el valle de menor energía.

4. **Ignorar los cambios de sección.**
   Convertir a caballo de dos arreglos mezcla vocabularios y duplica el
   tamaño del JSON.

---

## 8. Relación con las demás gráficas

| Gráfica | Relación |
|---|---|
| **specgram** | Misma información, eje lineal. Mel para bandas, lineal para Hz exactos |
| **mfcc** | La mel comprimida a una docena de números |
| **chroma** | Colapsa este detalle en 12 notas; confirma la tonalidad (MI) |
| **cqt** | Traduce estas franjas a bloques de notas |
| **selfsim** | Sus bloques explican los cambios de franja |

---

## 9. De la gráfica a los parámetros del conversor

| Lectura | Parámetro |
|---|---|
| Valle entre franjas | `--xover` (aquí 300 Hz; plugin: "120,480,1300") |
| Fin del dibujo arriba | `--hi` + cap de lead 1.200 Hz |
| Franjas pegadas sin valle | Prueba `--voices 1` |
| Cambio de franjas en t | Frontera de sección: convierte dentro de un bloque |

---

## 10. Nivel experto: Mel, filtros y el --auto

La escala Mel: `m = 2595·log10(1 + f/700)`. Se implementa con un banco de
~40-128 filtros triangulares solapados sobre el espectro de potencia. El
`analyze_layer()` usa la idea sin el banco completo: su f95 de energía
acumulada y el histograma de pitch muestreado responden a lo mismo (dónde
está la música) con menos cómputo. Validación experta: los `band_edges` que
imprime el conversor (`voz0: 40-120 Hz`...) deberían caer sobre valles
reales de esta imagen. Si una voz sale vacía o con confianza baja, mira aquí
si su franja existe de verdad antes de tocar el código.

---

## 11. Ejercicio práctico

1. Marca con el dedo el valle bajo/lead y estima sus Hz.
2. Compara con el --xover usado (300) y los cortes del plugin (120, 480, 1300).
3. Busca el punto donde la franja media pierde dibujo y estima sus Hz.
4. Cuenta cuántas franjas con dibujo hay: ¿2? ¿justifican 4 bandas? (Las 4
   salen de subdividir esas 2 por nivel: 120 y 480 parten el bajo del riff
   medio; 1300 separa el aire.)
5. Elige un cambio de franja y busca su segundo en el selfsim.

---

## 12. Preguntas frecuentes

**¿Por qué se llama "Mel"?**
De "melody": la escala se ajustó con experimentos de percepción de altura
en los años 30.

**¿Mel o lineal para transcribir?**
Mel para decidir bandas y voces; lineal (o log/CQT) para leer notas exactas.

**¿Los colores significan dB?**
Energía en escala comprimida (log). Brillante = fuerte, pero sin unidades
absolutas: es comparativa dentro de la imagen.

---

## 13. Glosario rápido

| Término | Definición |
|---|---|
| **Escala Mel** | Escala perceptual: expande graves, comprime agudos |
| **Franja** | Banda horizontal de energía sostenida (voz o capa) |
| **Valle espectral** | Mínimo local de energía entre franjas; sitio del corte |
| **Niebla** | Energía difusa sin estructura melódica |
| **Banco de filtros** | Conjunto de filtros solapados que implementa la escala |

---

## 14. Chuleta final

```
graves expandidos = la zona musical se lee de un vistazo
valle entre franjas -> ahi va --xover (aqui 300 Hz)
fin del dibujo arriba -> cap --hi (detector: 1200 Hz)
franjas pegadas -> prueba --voices 1
cambio de franja = frontera de seccion (ver selfsim)
```
