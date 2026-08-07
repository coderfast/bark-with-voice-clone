"""Generate better placeholder images using Pillow with diagrams, arrows, and structure."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

IMAGES_DIR = Path(__file__).parent / "images"
WIDTH, HEIGHT = 800, 450

# Colors
BLUE = (41, 98, 255)
LIGHT_BLUE = (200, 225, 255)
DARK_BLUE = (25, 55, 130)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LIGHT_GRAY = (240, 240, 240)
GREEN = (46, 160, 67)
ORANGE = (255, 152, 0)
RED = (220, 50, 50)
PURPLE = (128, 0, 128)
TEAL = (0, 150, 136)
BLACK = (30, 30, 30)


def get_font(size=14, bold=False):
    """Get font, fallback to default if not available."""
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_box(draw, x, y, w, h, text, fill=LIGHT_BLUE, outline=BLUE, text_color=BLACK, font_size=12):
    """Draw a rounded box with text."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=fill, outline=outline, width=2)
    font = get_font(font_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x + (w - tw) / 2, y + (h - th) / 2), text, fill=text_color, font=font)


def draw_arrow(draw, x1, y1, x2, y2, color=GRAY, width=2):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # Arrowhead
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_len = 10
    a1 = (x2 - arrow_len * math.cos(angle - 0.4), y2 - arrow_len * math.sin(angle - 0.4))
    a2 = (x2 - arrow_len * math.cos(angle + 0.4), y2 - arrow_len * math.sin(angle + 0.4))
    draw.polygon([(x2, y2), a1, a2], fill=color)


def draw_circle(draw, cx, cy, r, text, fill=LIGHT_BLUE, outline=BLUE, font_size=11):
    """Draw a circle with text."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=2)
    font = get_font(font_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), text, fill=BLACK, font=font)


def draw_header(draw, title, subtitle=""):
    """Draw title header."""
    draw.rectangle([0, 0, WIDTH, 50], fill=DARK_BLUE)
    font = get_font(18, bold=True)
    draw.text((20, 12), title, fill=WHITE, font=font)
    if subtitle:
        font_sm = get_font(11)
        draw.text((20, 35), subtitle, fill=(180, 200, 255), font=font_sm)


def draw_footer(draw, chapter):
    """Draw footer with chapter info."""
    draw.rectangle([0, HEIGHT - 25, WIDTH, HEIGHT], fill=LIGHT_GRAY)
    font = get_font(9)
    draw.text((20, HEIGHT - 20), f"La Biblia del AIML 2.1 | Capitulo {chapter}", fill=GRAY, font=font)


# ============================================================
# IMAGE GENERATORS
# ============================================================

def gen_05_srai():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "SRAI - Cadena de Redireccion", "Symbolic Reduction")
    # Chain: BUENOS DIAS -> HOLA -> Hello!
    y = 140
    boxes = [("BUENOS DIAS", 100), ("HOLA", 350), ("Hello!", 600)]
    for text, x in boxes:
        draw_box(draw, x, y, 140, 50, text, fill=(230, 245, 255), outline=BLUE, font_size=13)
    draw_arrow(draw, 245, 165, 345, 165, color=BLUE, width=3)
    draw_arrow(draw, 495, 165, 595, 165, color=BLUE, width=3)
    # Labels
    font = get_font(10)
    draw.text((260, 148), "srai", fill=RED, font=font)
    draw.text((510, 148), "srai", fill=RED, font=font)
    # Center note
    draw_box(draw, 250, 240, 300, 40, "Una frase puede redirigir a otra", fill=(255, 248, 230), outline=ORANGE, font_size=11)
    draw_footer(draw, 5)
    return img


def gen_06_condiciones():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Condiciones - Arbol de Decision", "AIML Conditions")
    # Root
    draw_box(draw, 320, 70, 160, 40, "mood = ?", fill=(230, 240, 255), outline=BLUE, font_size=12)
    # Branches
    draw_arrow(draw, 350, 115, 150, 165, color=GRAY)
    draw_arrow(draw, 400, 115, 400, 165, color=GRAY)
    draw_arrow(draw, 450, 115, 650, 165, color=GRAY)
    # Happy
    draw_box(draw, 80, 170, 140, 40, "happy", fill=(230, 255, 230), outline=GREEN, font_size=12)
    draw_box(draw, 80, 230, 140, 40, ":) Excelente!", fill=(240, 255, 240), outline=GREEN, font_size=10)
    # Neutral
    draw_box(draw, 330, 170, 140, 40, "neutral", fill=(255, 245, 230), outline=ORANGE, font_size=12)
    draw_box(draw, 330, 230, 140, 40, ":| Ok", fill=(255, 250, 240), outline=ORANGE, font_size=10)
    # Sad
    draw_box(draw, 580, 170, 140, 40, "sad", fill=(255, 230, 230), outline=RED, font_size=12)
    draw_box(draw, 580, 230, 140, 40, ":(", fill=(255, 240, 240), outline=RED, font_size=10)
    # Legend
    draw_box(draw, 250, 310, 300, 35, "<condition> if mood = 'happy'", fill=LIGHT_GRAY, outline=GRAY, font_size=10)
    draw_footer(draw, 6)
    return img


def gen_07_random():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Respuestas Aleatorias", "Random Responses")
    # Dice
    draw.rounded_rectangle([340, 80, 460, 200], radius=10, fill=(240, 240, 255), outline=PURPLE, width=3)
    draw.text((370, 100), "?", fill=PURPLE, font=get_font(40, bold=True))
    draw.text((355, 160), "random", fill=PURPLE, font=get_font(11))
    # Response options
    responses = ["Hola!", "Que tal!", "Hola amigo!", "Saludos!"]
    colors = [GREEN, BLUE, ORANGE, TEAL]
    for i, (resp, col) in enumerate(zip(responses, colors)):
        x = 60 + i * 180
        draw_box(draw, x, 250, 150, 40, resp, fill=(245, 245, 255), outline=col, font_size=12)
        draw_arrow(draw, 400, 205, x + 75, 245, color=col, width=2)
    # Labels
    font = get_font(10)
    for i in range(4):
        draw.text((115 + i * 180, 295), f"opcion {i+1}", fill=GRAY, font=font)
    draw_footer(draw, 7)
    return img


def gen_08_contexto():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Manejo de Contexto", "Conversation Context")
    # Sequence diagram
    draw_box(draw, 100, 80, 100, 40, "Usuario", fill=(230, 240, 255), outline=BLUE, font_size=11)
    draw_box(draw, 600, 80, 100, 40, "Bot", fill=(230, 255, 230), outline=GREEN, font_size=11)
    # Lifelines
    draw.line([(150, 125), (150, 350)], fill=GRAY, width=1)
    draw.line([(650, 125), (650, 350)], fill=GRAY, width=1)
    # Messages
    msgs = [
        (150, 160, 650, 160, "Hola, como estas?", BLUE),
        (650, 200, 150, 200, "Bien y tu?", GREEN),
        (150, 240, 650, 240, "Que tiempo hace?", BLUE),
        (650, 280, 150, 280, "that[2] = 'Bien y tu?'", ORANGE),
        (650, 320, 150, 320, "Soleado!", GREEN),
    ]
    for x1, y1, x2, y2, text, col in msgs:
        draw_arrow(draw, x1, y1, x2, y2, color=col, width=2)
        font = get_font(9)
        mx = (x1 + x2) / 2
        draw.text((mx - 50, y1 - 12), text, fill=col, font=font)
    draw_footer(draw, 8)
    return img


def gen_09_temas():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Sistema de Temas", "Topic System")
    # Outer topic
    draw.rounded_rectangle([150, 70, 650, 350], radius=12, fill=(245, 250, 255), outline=DARK_BLUE, width=2)
    draw.text((160, 75), "TOPIC=CLIMA", fill=DARK_BLUE, font=get_font(12, bold=True))
    # Categories inside
    cats = [
        (200, 120, "Sol", "Que tiempo hace?"),
        (200, 200, "Lluvia", "Llueve hoy?"),
        (200, 280, "Nieve", "Hay nieve?"),
        (450, 120, "Viento", "Hace viento?"),
        (450, 200, "Nublado", "Esta nublado?"),
    ]
    for x, y, title, pattern in cats:
        draw_box(draw, x, y, 180, 55, "", fill=WHITE, outline=TEAL)
        draw.text((x + 10, y + 5), title, fill=TEAL, font=get_font(11, bold=True))
        draw.text((x + 10, y + 25), pattern, fill=GRAY, font=get_font(9))
    draw_footer(draw, 9)
    return img


def gen_10_variables():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Variables y Alcance", "Variable Scope")
    # Concentric circles
    cx, cy = 400, 210
    draw.ellipse([cx - 180, cy - 140, cx + 180, cy + 140], fill=(255, 240, 240), outline=RED, width=2)
    draw.text((cx - 170, cy - 130), "bot-* (Global)", fill=RED, font=get_font(11, bold=True))
    draw.ellipse([cx - 130, cy - 100, cx + 130, cy + 100], fill=(255, 250, 230), outline=ORANGE, width=2)
    draw.text((cx - 120, cy - 90), "user-* (Sesion)", fill=ORANGE, font=get_font(11, bold=True))
    draw.ellipse([cx - 70, cy - 50, cx + 70, cy + 50], fill=(230, 255, 230), outline=GREEN, width=2)
    draw.text((cx - 60, cy - 15), "topic-*", fill=GREEN, font=get_font(11, bold=True))
    # Legend
    draw_box(draw, 50, 380, 200, 30, "user-name = 'Carlos'", fill=LIGHT_GRAY, outline=GRAY, font_size=9)
    draw_box(draw, 280, 380, 200, 30, "bot-author = 'AIML Bot'", fill=LIGHT_GRAY, outline=GRAY, font_size=9)
    draw_box(draw, 510, 380, 200, 30, "topic-current = 'clima'", fill=LIGHT_GRAY, outline=GRAY, font_size=9)
    draw_footer(draw, 10)
    return img


def gen_11_lista():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Elementos de Lista", "List Operations")
    # List visual
    items = ["apple", "banana", "cherry", "date"]
    for i, item in enumerate(items):
        x = 150 + i * 130
        draw_box(draw, x, 100, 110, 40, item, fill=(230, 240, 255), outline=BLUE, font_size=11)
    # Operations
    ops = [
        ("list", "apple banana cherry date", 70),
        ("first", "apple", 100),
        ("rest", "banana cherry date", 130),
        ("size", "4", 160),
    ]
    for op, result, y in ops:
        draw_box(draw, 80, y, 80, 25, op, fill=TEAL, outline=TEAL, text_color=WHITE, font_size=10)
        draw.text((180, y + 5), f"= {result}", fill=BLACK, font=get_font(10))
    draw_footer(draw, 11)
    return img


def gen_12_historial():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Historial de Conversacion", "Conversation History")
    # Timeline
    draw.line([(100, 200), (700, 200)], fill=GRAY, width=3)
    entries = [
        (150, "input[1]", "Hola", BLUE),
        (300, "input[2]", "Como estas?", BLUE),
        (450, "input[3]", "Que hora es?", BLUE),
        (600, "input[4]", "Gracias", GREEN),
    ]
    for x, label, text, col in entries:
        draw.ellipse([x - 15, 185, x + 15, 215], fill=col, outline=WHITE, width=2)
        draw.text((x - 30, 150), label, fill=col, font=get_font(10, bold=True))
        draw.text((x - 30, 230), text, fill=BLACK, font=get_font(10))
    # Labels
    draw.text((150, 280), "that[1] = 'Hola'", fill=GRAY, font=get_font(9))
    draw.text((300, 280), "that[2] = 'Como estas?'", fill=GRAY, font=get_font(9))
    draw_footer(draw, 12)
    return img


def gen_13_aprendizaje():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Aprendizaje Dinamico", "Dynamic Learning")
    # Cycle
    cx, cy = 400, 200
    r = 120
    steps = [("learn", 0), ("usar", 90), ("unlearn", 180), ("olvidar", 270)]
    colors = [GREEN, BLUE, RED, ORANGE]
    for i, (label, angle) in enumerate(steps):
        rad = math.radians(angle - 90)
        x = cx + r * math.cos(rad)
        y = cy + r * math.sin(rad)
        draw_box(draw, x - 50, y - 20, 100, 40, label, fill=(240, 248, 255), outline=colors[i], font_size=11)
    # Arrows between
    for i in range(4):
        a1 = math.radians(i * 90 - 90)
        a2 = math.radians((i + 1) * 90 - 90)
        x1 = cx + (r + 30) * math.cos(a1 + 0.3)
        y1 = cy + (r + 30) * math.sin(a1 + 0.3)
        x2 = cx + (r + 30) * math.cos(a2 - 0.3)
        y2 = cy + (r + 30) * math.sin(a2 - 0.3)
        draw_arrow(draw, x1, y1, x2, y2, color=GRAY, width=2)
    draw_footer(draw, 13)
    return img


def gen_14_transformaciones():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Transformaciones de Texto", "Text Transformations")
    # Pipeline
    steps = ["entrada", "person", "person2", "gender", "formal", "salida"]
    colors = [GRAY, TEAL, TEAL, BLUE, PURPLE, GREEN]
    for i, (step, col) in enumerate(zip(steps, colors)):
        x = 50 + i * 125
        draw_box(draw, x, 150, 100, 40, step, fill=(240, 248, 255), outline=col, font_size=10)
        if i < len(steps) - 1:
            draw_arrow(draw, x + 105, 170, x + 120, 170, color=GRAY, width=2)
    # Examples
    examples = [
        ("Input: 'yo tengo'", "person -> 'tu tienes'"),
        ("Input: 'el'", "gender -> 'ella'"),
        ("Input: 'hola'", "formal -> 'buenos dias'"),
    ]
    for i, (inp, out) in enumerate(examples):
        y = 250 + i * 30
        draw.text((100, y), inp, fill=BLACK, font=get_font(10))
        draw.text((350, y), out, fill=PURPLE, font=get_font(10))
    draw_footer(draw, 14)
    return img


def gen_15_operaciones():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Operaciones del Sistema", "System Operations")
    ops = [
        ("thinking", "Cerebro", TEAL, "<thinking>"),
        ("date", "Reloj", BLUE, "<date>"),
        ("eval", "Terminal", ORANGE, "<eval>"),
        ("system", "Servidor", RED, "<system>"),
    ]
    for i, (name, icon, col, tag) in enumerate(ops):
        x = 80 + i * 180
        draw_box(draw, x, 100, 150, 80, "", fill=(245, 248, 255), outline=col)
        draw.text((x + 10, 110), icon, fill=col, font=get_font(12, bold=True))
        draw.text((x + 10, 135), name, fill=BLACK, font=get_font(10))
        draw.text((x + 10, 155), tag, fill=GRAY, font=get_font(9))
    draw_footer(draw, 15)
    return img


def gen_16_formato():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Elementos de Formateo", "Formatting Elements")
    # Mockup window
    draw.rounded_rectangle([100, 70, 700, 380], radius=10, fill=WHITE, outline=GRAY, width=2)
    draw.rectangle([100, 70, 700, 100], fill=LIGHT_GRAY)
    draw.text((110, 78), "ChatBot Response", fill=BLACK, font=get_font(11, bold=True))
    # Content
    draw.text((120, 110), "Hola! Este es un mensaje con:", fill=BLACK, font=get_font(10))
    draw.text((120, 140), "  <b>Texto en negrita</b>", fill=BLACK, font=get_font(10))
    draw.text((120, 165), "  <a href='...'>Enlace</a>", fill=BLUE, font=get_font(10))
    draw.text((120, 190), "  <br>Salto de linea", fill=BLACK, font=get_font(10))
    draw_box(draw, 130, 220, 150, 60, "Tabla", fill=LIGHT_BLUE, outline=BLUE, font_size=10)
    draw_box(draw, 310, 220, 100, 60, "Imagen", fill=LIGHT_BLUE, outline=GREEN, font_size=10)
    draw_footer(draw, 16)
    return img


def gen_17_patrones_conv():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Patrones de Conversacion", "Conversation Patterns")
    # Mind map center
    draw_box(draw, 310, 180, 180, 50, "Conversacion", fill=DARK_BLUE, outline=DARK_BLUE, text_color=WHITE, font_size=12)
    # Branches
    branches = [
        (150, 80, "Saludo", GREEN),
        (600, 80, "Despedida", RED),
        (150, 300, "Fallback", ORANGE),
        (600, 300, "Confirmacion", TEAL),
        (400, 60, "Multi-turno", PURPLE),
    ]
    for x, y, label, col in branches:
        draw_box(draw, x, y, 120, 35, label, fill=(245, 248, 255), outline=col, font_size=10)
        draw_arrow(draw, 400, 205, x + 60, y + 35, color=col, width=2)
    draw_footer(draw, 17)
    return img


def gen_18_personalidad():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Patrones de Personalidad", "Personality Patterns")
    # Personality traits
    traits = [
        ("Formal", 100, 100, BLUE),
        ("Casual", 350, 100, GREEN),
        ("Funny", 600, 100, ORANGE),
        ("Empatico", 220, 280, PURPLE),
        ("Directo", 500, 280, TEAL),
    ]
    for label, x, y, col in traits:
        draw_box(draw, x, y, 120, 50, label, fill=(245, 248, 255), outline=col, font_size=12)
    # Scale bars
    draw.text((100, 370), "Formalidad: ", fill=BLACK, font=get_font(10))
    draw.rectangle([200, 370, 500, 385], fill=LIGHT_GRAY, outline=GRAY)
    draw.rectangle([200, 370, 350, 385], fill=BLUE)
    draw_footer(draw, 18)
    return img


def gen_19_memoria():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Patrones de Memoria", "Memory Patterns")
    # Memory types
    mem = [
        ("Corto Plazo", "RAM", "Sesion actual", 100, TEAL),
        ("Largo Plazo", "Disco", "learn / unlearn", 300, BLUE),
        ("Preferencias", "DB", "user-* variables", 500, PURPLE),
    ]
    for name, icon, desc, x, col in mem:
        draw_box(draw, x, 100, 180, 100, "", fill=(245, 248, 255), outline=col)
        draw.text((x + 10, 110), icon, fill=col, font=get_font(14, bold=True))
        draw.text((x + 10, 140), name, fill=BLACK, font=get_font(11))
        draw.text((x + 10, 165), desc, fill=GRAY, font=get_font(9))
    # Arrows
    draw_arrow(draw, 285, 150, 295, 150, color=GRAY, width=2)
    draw_arrow(draw, 485, 150, 495, 150, color=GRAY, width=2)
    draw_footer(draw, 19)
    return img


def gen_20_testing():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Testing y Debugging", "Testing Pipeline")
    # Pipeline
    steps = [
        ("Unit Tests", GREEN, "pytest"),
        ("Integration", BLUE, "tests/"),
        ("Performance", ORANGE, "benchmark"),
        ("Deploy", TEAL, "production"),
    ]
    for i, (name, col, detail) in enumerate(steps):
        x = 80 + i * 180
        draw_box(draw, x, 120, 150, 60, name, fill=(245, 248, 255), outline=col, font_size=12)
        draw.text((x + 10, 165), detail, fill=GRAY, font=get_font(9))
        if i < len(steps) - 1:
            draw_arrow(draw, x + 155, 150, x + 175, 150, color=col, width=3)
    # Status
    draw.text((80, 230), "Estado:", fill=BLACK, font=get_font(11, bold=True))
    for i, (name, col, _) in enumerate(steps):
        x = 80 + i * 180
        draw.ellipse([x + 60, 230, x + 75, 245], fill=GREEN)
        draw.text((x + 80, 230), "PASS", fill=GREEN, font=get_font(9))
    draw_footer(draw, 20)
    return img


def gen_21_optimizacion():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Optimizacion de Rendimiento", "Performance Optimization")
    # Metrics
    metrics = [
        ("Tiempo Respuesta", "45ms", GREEN, 100),
        ("Cache Hit", "87%", BLUE, 250),
        ("Memoria", "512MB", ORANGE, 400),
        ("CPU", "23%", TEAL, 550),
    ]
    for name, value, col, x in metrics:
        draw_box(draw, x, 80, 130, 80, "", fill=(245, 248, 255), outline=col)
        draw.text((x + 10, 90), name, fill=GRAY, font=get_font(9))
        draw.text((x + 10, 115), value, fill=col, font=get_font(18, bold=True))
    # Bar chart
    bars = [("AIML", 0.7, GREEN), ("LLM", 0.95, RED), ("Hybrid", 0.6, BLUE)]
    for i, (name, pct, col) in enumerate(bars):
        y = 220 + i * 40
        draw.text((100, y + 5), name, fill=BLACK, font=get_font(10))
        draw.rectangle([200, y, 200 + int(400 * pct), y + 25], fill=col)
        draw.rectangle([200, y, 600, y + 25], outline=GRAY)
    draw_footer(draw, 21)
    return img


def gen_22_organizacion():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Organizacion de Proyectos", "Project Structure")
    # File tree
    tree = [
        (0, "myproject/", DARK_BLUE),
        (1, "main.aiml", BLUE),
        (1, "modules/", TEAL),
        (2, "greetings.aiml", BLUE),
        (2, "weather.aiml", BLUE),
        (1, "topics/", GREEN),
        (1, "tests/", ORANGE),
        (2, "test_greetings.py", ORANGE),
        (1, "data/", PURPLE),
    ]
    for i, (indent, name, col) in enumerate(tree):
        y = 80 + i * 30
        x = 100 + indent * 40
        prefix = "  " if indent > 0 else ""
        color = col if not name.endswith("/") else TEAL
        if name.endswith(".py"):
            color = ORANGE
        elif name.endswith(".aiml") and indent == 0:
            color = DARK_BLUE
        draw.text((x, y), f"{prefix}{name}", fill=color, font=get_font(11, bold=(indent == 0)))
    draw_footer(draw, 22)
    return img


def gen_23_practicas():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Mejores Practicas", "Best Practices")
    # Checklist
    items = [
        ("Codigo limpio y documentado", True),
        ("Testing regular", True),
        ("Manejo de errores", True),
        ("Seguridad (no hardcodear)", True),
        ("Optimizacion de matching", True),
        ("Backups de modelos", False),
    ]
    for i, (item, ok) in enumerate(items):
        y = 80 + i * 40
        col = GREEN if ok else RED
        symbol = "OK" if ok else "X"
        draw_box(draw, 100, y, 25, 25, symbol, fill=col, outline=col, text_color=WHITE, font_size=10)
        draw.text((140, y + 5), item, fill=BLACK, font=get_font(11))
    draw_footer(draw, 23)
    return img


def gen_24_bot_cliente():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Bot de Atencion al Cliente", "Customer Service Bot")
    # Chat window
    draw.rounded_rectangle([100, 70, 700, 380], radius=10, fill=WHITE, outline=GRAY, width=2)
    # Bot messages
    draw.rounded_rectangle([120, 90, 450, 130], radius=8, fill=LIGHT_BLUE, outline=BLUE)
    draw.text((130, 100), "Bienvenido! Como puedo ayudarte?", fill=BLACK, font=get_font(10))
    # Options
    options = ["1. Estado de pedido", "2. Devoluciones", "3. Hablar con agente"]
    for i, opt in enumerate(options):
        y = 150 + i * 35
        draw.rounded_rectangle([300, y, 680, y + 30], radius=8, fill=(230, 255, 230), outline=GREEN)
        draw.text((310, y + 5), opt, fill=BLACK, font=get_font(10))
    draw_footer(draw, 24)
    return img


def gen_25_bot_educativo():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Bot Educativo", "Educational Bot")
    # Quiz interface
    draw.rounded_rectangle([100, 70, 700, 380], radius=10, fill=WHITE, outline=GRAY, width=2)
    draw.text((120, 85), "Leccion 3: AIML Basico", fill=DARK_BLUE, font=get_font(12, bold=True))
    draw.text((120, 120), "Pregunta: Cual es el elemento raiz?", fill=BLACK, font=get_font(11))
    # Options
    opts = ["a) <category>", "b) <aiml>", "c) <pattern>", "d) <template>"]
    for i, opt in enumerate(opts):
        y = 160 + i * 35
        col = GREEN if i == 1 else LIGHT_BLUE
        draw_box(draw, 120, y, 200, 28, opt, fill=col, outline=BLUE, font_size=10)
    # Progress
    draw.rectangle([120, 320, 680, 340], fill=LIGHT_GRAY)
    draw.rectangle([120, 320, 350, 340], fill=GREEN)
    draw.text((120, 345), "Progreso: 45%", fill=GRAY, font=get_font(9))
    draw_footer(draw, 25)
    return img


def gen_26_bot_salud():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Bot de Salud", "Health Bot")
    # Warning
    draw.rounded_rectangle([100, 70, 700, 110], radius=8, fill=(255, 230, 230), outline=RED, width=2)
    draw.text((120, 80), "AVISO: Este bot NO reemplaza consulta medica profesional", fill=RED, font=get_font(10, bold=True))
    # Form
    draw.text((120, 130), "Sintomas:", fill=BLACK, font=get_font(11, bold=True))
    symptoms = ["Fiebre", "Tos", "Dolor de cabeza", "Fatiga"]
    for i, s in enumerate(symptoms):
        y = 160 + i * 30
        draw.rectangle([120, y, 140, y + 20], outline=GRAY)
        draw.text((150, y + 2), s, fill=BLACK, font=get_font(10))
    # Emergency button
    draw_box(draw, 250, 320, 300, 40, "EMERGENCIA: Llamar 911", fill=RED, outline=RED, text_color=WHITE, font_size=12)
    draw_footer(draw, 26)
    return img


def gen_27_multilingue():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Bot Multilingue", "Multilingual Bot")
    # Language detection
    draw_box(draw, 100, 100, 150, 50, "Entrada", fill=LIGHT_BLUE, outline=BLUE, font_size=11)
    draw_arrow(draw, 255, 125, 320, 125, color=BLUE, width=2)
    draw_box(draw, 320, 100, 160, 50, "Detectar Idioma", fill=TEAL, outline=TEAL, text_color=WHITE, font_size=11)
    draw_arrow(draw, 485, 125, 550, 125, color=TEAL, width=2)
    # Languages
    langs = [("ES", 560, 80), ("EN", 620, 80), ("FR", 560, 140), ("PT", 620, 140)]
    for lang, x, y in langs:
        draw_box(draw, x, y, 50, 35, lang, fill=(230, 240, 255), outline=BLUE, font_size=10)
    # Translation pipeline
    draw.text((100, 200), "Pipeline: detect -> translate -> respond", fill=GRAY, font=get_font(10))
    draw_footer(draw, 27)
    return img


def gen_28_integracion_llm():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Integracion con LLMs", "AIML + LLM Hybrid")
    # Architecture
    draw_box(draw, 100, 120, 150, 60, "Usuario", fill=LIGHT_BLUE, outline=BLUE, font_size=12)
    draw_arrow(draw, 255, 150, 320, 150, color=BLUE, width=2)
    draw_box(draw, 320, 100, 160, 40, "AIML Engine", fill=GREEN, outline=GREEN, text_color=WHITE, font_size=11)
    draw_box(draw, 320, 160, 160, 40, "LLM Fallback", fill=PURPLE, outline=PURPLE, text_color=WHITE, font_size=11)
    draw_arrow(draw, 485, 120, 560, 120, color=GREEN, width=2)
    draw_arrow(draw, 485, 180, 560, 180, color=PURPLE, width=2)
    draw_box(draw, 560, 130, 120, 50, "Respuesta", fill=LIGHT_BLUE, outline=BLUE, font_size=12)
    # Decision
    draw.text((320, 230), "Si match AIML -> usar AIML, si no -> LLM", fill=GRAY, font=get_font(10))
    draw_footer(draw, 28)
    return img


def gen_29_despliegue():
    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Despliegue en Produccion", "Production Deployment")
    # Docker
    draw_box(draw, 80, 100, 120, 60, "Docker", fill=BLUE, outline=BLUE, text_color=WHITE, font_size=12)
    draw_arrow(draw, 205, 130, 270, 130, color=BLUE, width=2)
    # Load Balancer
    draw_box(draw, 270, 100, 140, 60, "Load Balancer", fill=ORANGE, outline=ORANGE, text_color=WHITE, font_size=11)
    # Instances
    for i in range(3):
        x = 450 + i * 90
        draw_arrow(draw, 415, 130, x + 20, 130, color=ORANGE, width=2)
        draw_box(draw, x, 100, 70, 60, f"Inst {i+1}", fill=TEAL, outline=TEAL, text_color=WHITE, font_size=9)
    # Monitoring
    draw_box(draw, 250, 220, 300, 50, "Monitoring & Logs", fill=PURPLE, outline=PURPLE, text_color=WHITE, font_size=11)
    draw_arrow(draw, 400, 165, 400, 215, color=GRAY, width=2)
    draw_footer(draw, 29)
    return img


# ============================================================
# MAIN
# ============================================================

GENERATORS = {
    "05_srai_cadena.png": gen_05_srai,
    "06_condiciones_arbol.png": gen_06_condiciones,
    "07_random_respuestas.png": gen_07_random,
    "08_contexto_conversacion.png": gen_08_contexto,
    "09_sistema_temas.png": gen_09_temas,
    "10_variables_alcance.png": gen_10_variables,
    "11_operaciones_lista.png": gen_11_lista,
    "12_historial_conversacion.png": gen_12_historial,
    "13_aprendizaje_ciclo.png": gen_13_aprendizaje,
    "14_transformaciones_texto.png": gen_14_transformaciones,
    "15_operaciones_sistema.png": gen_15_operaciones,
    "16_formato_respuesta.png": gen_16_formato,
    "17_patrones_conversacion.png": gen_17_patrones_conv,
    "18_patrones_personalidad.png": gen_18_personalidad,
    "19_patrones_memoria.png": gen_19_memoria,
    "20_testing_debugging.png": gen_20_testing,
    "21_optimizacion.png": gen_21_optimizacion,
    "22_organizacion_proyectos.png": gen_22_organizacion,
    "23_mejores_practicas.png": gen_23_practicas,
    "24_bot_cliente.png": gen_24_bot_cliente,
    "25_bot_educativo.png": gen_25_bot_educativo,
    "26_bot_salud.png": gen_26_bot_salud,
    "27_bot_multilingue.png": gen_27_multilingue,
    "28_integracion_llm.png": gen_28_integracion_llm,
    "29_despliegue_produccion.png": gen_29_despliegue,
}


def main():
    IMAGES_DIR.mkdir(exist_ok=True)

    # Check which images need regeneration (< 50KB or placeholder)
    to_generate = []
    for filename, gen_func in GENERATORS.items():
        img_path = IMAGES_DIR / filename
        if img_path.exists() and img_path.stat().st_size > 50_000:
            print(f"  Skipping {filename} (already {img_path.stat().st_size // 1024} KB)")
        else:
            to_generate.append((filename, gen_func))

    if not to_generate:
        print("All images are already generated!")
        return

    print(f"\nGenerating {len(to_generate)} images with Pillow...\n")

    success = 0
    for filename, gen_func in to_generate:
        try:
            img = gen_func()
            out_path = IMAGES_DIR / filename
            img.save(str(out_path), "PNG")
            size_kb = out_path.stat().st_size / 1024
            print(f"  OK: {filename} ({size_kb:.1f} KB)")
            success += 1
        except Exception as e:
            print(f"  ERROR: {filename}: {e}")

    print(f"\nDone: {success}/{len(to_generate)} images generated")
    print(f"Images saved to: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
