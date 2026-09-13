from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

IMAGES = [
    ("00_portada.png", "Portada", "Portada de libro tecnico titled 'La Biblia del AIML 2.1', estilo minimalista con codigo XML flotante, esquema de arbol de decisiones, y un robot amigable leyendo un libro, fondo azul oscuro con detalles dorados, estilo flat design moderno"),
    ("01_historia_aiml.png", "Capitulo 1", "Linea de tiempo visual mostrando la evolucion de AIML desde 1995 hasta 2026, con hitos importantes: ALICE 1995, Loebner Prize 2000, AIML 1.0 2001, AIML 2.0 2012, AIML 2.1 2018, estilo infografia moderna colores azul y blanco"),
    ("02_arquitectura_procesador.png", "Capitulo 2", "Diagrama de arquitectura de un procesador AIML mostrando: Parser XML, Motor de Matching, Template Resolution, Sesiones, Variables, Historial, con flechas de flujo de datos, estilo diagrama tecnico limpio"),
    ("03_estructura_aiml.png", "Capitulo 3", "Diagrama anotado de la estructura basica de un archivo AIML, mostrando los elementos: aiml, category, pattern, template, con etiquetas y conexiones claras, estilo diagrama educativo"),
    ("04_wildcards_ejemplos.png", "Capitulo 4", "Ilustracion visual de los 4 wildcards de AIML: *, _, **, ^, con ejemplos de coincidencia para cada uno, usando texto resaltado y flechas, estilo tabla visual comparativa"),
    ("05_srai_cadena.png", "Capitulo 5", "Diagrama de flujo mostrando una cadena SRAI: 'BUENOS DIAS' -> 'HOLA' -> 'Hola!', con flechas de redireccion y nodo central, estilo flowchart moderno"),
    ("06_condiciones_arbol.png", "Capitulo 6", "Arbol de decision de un chatbot mostrando condicionales: if-else con ramas para mood (happy, sad, angry), con iconos de caritas y respuestas, estilo diagrama de arbol"),
    ("07_random_respuestas.png", "Capitulo 7", "Ilustracion de seleccion aleatoria de respuestas: dado o ruleta con multiples opciones de respuesta saliendo, estilo conceptual moderno"),
    ("08_contexto_conversacion.png", "Capitulo 8", "Diagrama de secuencia de conversacion mostrando: Usuario -> Bot -> that (respuesta anterior) -> siguiente respuesta, con burbujas de dialogo, estilo secuencia UML"),
    ("09_sistema_temas.png", "Capitulo 9", "Diagrama de contenedores mostrando temas como cajas que agrupan categories relacionadas: TEMA=CLIMA con categories de clima dentro, estilo diagrama de contenedores"),
    ("10_variables_alcance.png", "Capitulo 10", "Diagrama de alcance de variables AIML mostrando 3 niveles: user-* (sesion), bot-* (global), topic-* (tema), con circulos concentricos, estilo diagrama de scopes"),
    ("11_operaciones_lista.png", "Capitulo 11", "Infografia de operaciones de lista: list, first, rest, size, repeat, loop, con iconos y ejemplos visuales para cada operacion, estilo grid de iconos"),
    ("12_historial_conversacion.png", "Capitulo 12", "Linea de tiempo de historial de conversacion mostrando: input[1], input[2], input[3] con marcas de tiempo y contenido, estilo timeline visual"),
    ("13_aprendizaje_ciclo.png", "Capitulo 13", "Diagrama de ciclo de aprendizaje dinamico: learn -> usar -> unlearn -> learn, con iconos de cerebro y flechas circulares, estilo diagrama circular moderno"),
    ("14_transformaciones_texto.png", "Capitulo 14", "Pipeline de transformaciones de texto: entrada -> person -> person2 -> gender -> formal -> salida, con flechas y ejemplo visual para cada paso, estilo pipeline diagram"),
    ("15_operaciones_sistema.png", "Capitulo 15", "Diagrama de operaciones del sistema mostrando: thinking (cerebro), date (reloj), eval (terminal), system (servidor), con iconos modernos, estilo icon grid"),
    ("16_formato_respuesta.png", "Capitulo 16", "Mockup de respuesta enriquecida de chatbot mostrando: texto con formato, enlaces, imagenes, tablas, dentro de un marco de ventana, estilo UI mockup"),
    ("17_patrones_conversacion.png", "Capitulo 17", "Mapa mental de patrones de conversacion: saludo, despedida, fallback, confirmacion, multi-turno, con ramas y colores, estilo mind map"),
    ("18_patrones_personalidad.png", "Capitulo 18", "Diagrama de personalidad de chatbot mostrando: formal, casual, funny, empatico, con escalas y indicadores, estilo diagrama de personalidad"),
    ("19_patrones_memoria.png", "Capitulo 19", "Diagrama de memoria: corto plazo (RAM), largo plazo (disco), preferencias (base de datos), contexto (buffer), con iconos de almacenamiento, estilo diagrama de memoria"),
    ("20_testing_debugging.png", "Capitulo 20", "Pipeline de testing: unit tests -> integration tests -> performance tests -> deploy, con iconos de checkmarks y bug, estilo CI/CD pipeline"),
    ("21_optimizacion.png", "Capitulo 21", "Dashboard de optimizacion mostrando metricas: tiempo de respuesta, uso de memoria, cache hit ratio, con graficas y KPIs, estilo dashboard moderno"),
    ("22_organizacion_proyectos.png", "Capitulo 22", "Estructura de carpetas de proyecto AIML: main.aiml, modules/, topics/, tests/, data/, con iconos de carpeta y archivos, estilo tree diagram"),
    ("23_mejores_practicas.png", "Capitulo 23", "Checklist visual de mejores practicas: codigo limpio, seguridad, testing, documentacion, con checkmarks y X, estilo infographic de checklist"),
    ("24_bot_cliente.png", "Capitulo 24", "Mockup de interfaz de chatbot de atencion al cliente mostrando: menu de opciones, preguntas frecuentes, formulario de soporte, estilo UI moderno"),
    ("25_bot_educativo.png", "Capitulo 25", "Interfaz de chatbot educativo mostrando: leccion activa, quiz interactivo, progreso del estudiante, estilo UI de e-learning"),
    ("26_bot_salud.png", "Capitulo 26", "Interfaz de chatbot de salud con advertencias: formulario de sintomas, recomendaciones, boton de emergencia, estilo medical UI"),
    ("27_bot_multilingue.png", "Capitulo 27", "Diagrama de chatbot multilingue mostrando: deteccion de idioma, traduccion, respuestas en multiples idiomas, con banderas y texto, estilo internacionalizacion"),
    ("28_integracion_llm.png", "Capitulo 29", "Diagrama hibrido AIML + LLM: AIML como capa de control -> fallback a LLM -> respuesta, con iconos de cerebro y reglas, estilo architecture diagram"),
    ("29_despliegue_produccion.png", "Capitulo 30", "Diagrama de despliegue en produccion: Docker -> Load Balancer -> Instances -> Monitoring, con iconos de contenedor y graficas, estilo DevOps diagram"),
]

COLORS = {
    "bg_start": (44, 62, 80),
    "bg_end": (52, 73, 94),
    "title": (255, 255, 255),
    "subtitle": (189, 195, 199),
    "prompt": (149, 167, 183),
    "accent": (52, 152, 219),
    "border": (41, 128, 185),
}

def create_image(filename, title, prompt, width=800, height=400):
    img = Image.new("RGB", (width, height), COLORS["bg_start"])
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(COLORS["bg_start"][0] * (1 - ratio) + COLORS["bg_end"][0] * ratio)
        g = int(COLORS["bg_start"][1] * (1 - ratio) + COLORS["bg_end"][1] * ratio)
        b = int(COLORS["bg_start"][2] * (1 - ratio) + COLORS["bg_end"][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw.rectangle([(10, 10), (width - 10, height - 10)], outline=COLORS["border"], width=2)

    draw.rectangle([(10, 10), (width - 10, 60)], fill=COLORS["border"])

    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_prompt = ImageFont.truetype("arial.ttf", 12)
        font_icon = ImageFont.truetype("arial.ttf", 36)
    except OSError:
        try:
            font_title = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
            font_prompt = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
            font_icon = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
        except OSError:
            font_title = ImageFont.load_default()
            font_prompt = ImageFont.load_default()
            font_icon = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_width = bbox[2] - bbox[0]
    x_title = (width - text_width) // 2
    draw.text((x_title, 20), title, fill=COLORS["title"], font=font_title)

    icon_y = 80
    icon_symbols = ["[IMG]", "< >", "{ }", "#", "*"]
    icon = icon_symbols[hash(title) % len(icon_symbols)]
    bbox = draw.textbbox((0, 0), icon, font=font_icon)
    icon_width = bbox[2] - bbox[0]
    draw.text(((width - icon_width) // 2, icon_y), icon, fill=COLORS["accent"], font=font_icon)

    wrapped = textwrap.wrap(prompt, width=70)
    prompt_y = 160
    for line in wrapped[:6]:
        bbox = draw.textbbox((0, 0), line, font=font_prompt)
        line_width = bbox[2] - bbox[0]
        draw.text(((width - line_width) // 2, prompt_y), line, fill=COLORS["prompt"], font=font_prompt)
        prompt_y += 18

    footer = "Generar imagen con IA usando este prompt"
    bbox = draw.textbbox((0, 0), footer, font=font_prompt)
    footer_width = bbox[2] - bbox[0]
    draw.text(((width - footer_width) // 2, height - 40), footer, fill=COLORS["subtitle"], font=font_prompt)

    draw.line([(40, height - 55), (width - 40, height - 55)], fill=COLORS["border"], width=1)

    output_path = OUTPUT_DIR / filename
    img.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    print(f"Generating {len(IMAGES)} images...")
    for filename, title, prompt in IMAGES:
        path = create_image(filename, title, prompt)
        print(f"  Created: {path.name}")
    print("Done!")
