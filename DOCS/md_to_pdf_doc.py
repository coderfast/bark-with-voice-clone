import re
import sys
import subprocess
import tempfile
import argparse
from pathlib import Path
from fpdf import FPDF


TEMPLATES = {
    "vintage_light_pink": {
        "name": "Vintage Light Pink",
        "cover_bg": (248, 220, 230),
        "title_color": (139, 69, 87),
        "subtitle_color": (160, 120, 135),
        "body_color": (61, 43, 48),
        "muted_color": (150, 130, 135),
        "code_bg": (250, 240, 243),
        "code_text": (80, 50, 55),
        "border_color": (212, 160, 176),
        "header_color": (200, 170, 180),
        "table_header_bg": (139, 69, 87),
        "table_header_text": (255, 255, 255),
        "table_row_bg": (248, 232, 238),
        "table_border": (200, 170, 180),
        "blockquote_color": (140, 110, 120),
        "image_placeholder_bg": (248, 232, 238),
        "image_placeholder_border": (180, 140, 155),
        "image_placeholder_text": (139, 69, 87),
        "footer_color": (160, 140, 145),
        "mermaid_bg": (245, 235, 240),
        "mermaid_border": (190, 160, 170),
        "mermaid_text": (120, 90, 100),
    },
    "vintage_white": {
        "name": "Vintage White",
        "cover_bg": (245, 245, 245),
        "title_color": (80, 80, 85),
        "subtitle_color": (110, 110, 115),
        "body_color": (50, 50, 55),
        "muted_color": (130, 130, 135),
        "code_bg": (245, 245, 245),
        "code_text": (50, 50, 55),
        "border_color": (190, 190, 195),
        "header_color": (170, 170, 175),
        "table_header_bg": (80, 80, 85),
        "table_header_text": (255, 255, 255),
        "table_row_bg": (240, 240, 240),
        "table_border": (180, 180, 185),
        "blockquote_color": (120, 120, 125),
        "image_placeholder_bg": (240, 240, 245),
        "image_placeholder_border": (160, 160, 165),
        "image_placeholder_text": (80, 80, 85),
        "footer_color": (140, 140, 145),
        "mermaid_bg": (238, 238, 242),
        "mermaid_border": (170, 170, 175),
        "mermaid_text": (100, 100, 105),
    },
    "vintage_light_blue": {
        "name": "Vintage Light Blue",
        "cover_bg": (220, 235, 250),
        "title_color": (70, 100, 140),
        "subtitle_color": (100, 130, 160),
        "body_color": (45, 55, 70),
        "muted_color": (120, 135, 155),
        "code_bg": (235, 242, 250),
        "code_text": (50, 60, 75),
        "border_color": (160, 185, 210),
        "header_color": (150, 175, 200),
        "table_header_bg": (70, 100, 140),
        "table_header_text": (255, 255, 255),
        "table_row_bg": (235, 242, 250),
        "table_border": (160, 185, 210),
        "blockquote_color": (100, 125, 150),
        "image_placeholder_bg": (230, 240, 250),
        "image_placeholder_border": (140, 170, 200),
        "image_placeholder_text": (70, 100, 140),
        "footer_color": (130, 150, 175),
        "mermaid_bg": (228, 238, 248),
        "mermaid_border": (150, 175, 205),
        "mermaid_text": (90, 115, 140),
    },
}


def sanitize(text):
    replacements = {
        '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2022': '*',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def parse_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text.strip()


def render_mermaid(code: str, tmp_dir: Path) -> str | None:
    import base64
    import urllib.request
    import urllib.parse

    png_file = tmp_dir / f"diagram_{hash(code) & 0xFFFFFFFF:08x}.png"

    try:
        encoded = base64.urlsafe_b64encode(code.encode("utf-8")).decode("utf-8")
        url = f"https://mermaid.ink/img/{encoded}?bgColor=white&width=800"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            if len(data) > 100:
                png_file.write_bytes(data)
                return str(png_file)
    except Exception:
        pass

    mmd_file = tmp_dir / f"diagram_{hash(code) & 0xFFFFFFFF:08x}.mmd"
    mmd_file.write_text(code, encoding="utf-8")
    try:
        result = subprocess.run(
            ["mmdc", "-i", str(mmd_file), "-o", str(png_file), "-w", "800", "-b", "white"],
            capture_output=True, timeout=30
        )
        if png_file.exists() and png_file.stat().st_size > 0:
            return str(png_file)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def parse_markdown(md_text, md_dir: Path = None):
    lines = md_text.split("\n")
    elements = []
    i = 0
    in_code = False
    code_buf = []
    code_lang = ""
    in_table = False
    table_rows = []

    img_pattern = re.compile(r'^!\[(.+?)\]\((.+?)\)$')

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            if in_code:
                if code_lang == "mermaid":
                    elements.append(("mermaid", "\n".join(code_buf)))
                else:
                    elements.append(("code", "\n".join(code_buf)))
                code_buf = []
                in_code = False
                code_lang = ""
            else:
                in_code = True
                code_lang = line.strip().replace("```", "").strip()
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("|") and not in_table:
            in_table = True
            table_rows = []

        if in_table:
            if line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if not all(re.match(r'^[-:]+$', c) for c in cells):
                    table_rows.append(cells)
            else:
                if table_rows:
                    elements.append(("table", table_rows))
                in_table = False
                table_rows = []
                continue
            i += 1
            continue

        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        img_match = img_pattern.match(stripped)
        if img_match:
            alt_text = img_match.group(1)
            img_path = img_match.group(2)
            exists = False
            if md_dir:
                full_path = md_dir / img_path
                if full_path.exists() and full_path.is_file():
                    exists = True
                else:
                    img_file = Path(img_path)
                    parent = img_file.parent
                    stem = img_file.stem
                    for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                        test_path = md_dir / parent / f"{stem}{ext}"
                        if test_path.exists() and test_path.is_file():
                            exists = True
                            break
            elements.append(("image", (alt_text, img_path, exists)))
            i += 1
            continue

        if stripped.startswith("# ") and not stripped.startswith("##"):
            elements.append(("h1", parse_inline(stripped[2:])))
        elif stripped.startswith("## "):
            elements.append(("h2", parse_inline(stripped[3:])))
        elif stripped.startswith("### "):
            elements.append(("h3", parse_inline(stripped[4:])))
        elif stripped.startswith("#### "):
            elements.append(("h4", parse_inline(stripped[5:])))
        elif stripped.startswith("> "):
            elements.append(("blockquote", parse_inline(stripped[2:])))
        elif stripped.startswith("---"):
            pass
        elif stripped.startswith("- ") or stripped.startswith("* "):
            elements.append(("li", parse_inline(stripped[2:])))
        elif re.match(r'^\d+\.\s', stripped):
            elements.append(("oli", parse_inline(stripped)))
        else:
            elements.append(("p", parse_inline(stripped)))

        i += 1

    return elements


class MarkdownPDF(FPDF):
    FONT_DIR = Path(__file__).parent / "fonts"

    def __init__(self, md_dir: Path = None, template: dict = None):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.md_dir = md_dir
        self.t = template or TEMPLATES["vintage_light_pink"]
        self.doc_title = ""
        self.doc_subtitle = ""
        self.doc_description = ""
        self.add_font("CourierNew", "", str(self.FONT_DIR / "CourierNew.ttf"))
        self.add_font("CourierNew", "B", str(self.FONT_DIR / "CourierNew-Bold.ttf"))
        self.add_font("CourierNew", "I", str(self.FONT_DIR / "CourierNew-Italic.ttf"))
        self.add_font("CourierNew", "BI", str(self.FONT_DIR / "CourierNew-BoldItalic.ttf"))

    def header(self):
        if self.page_no() > 1:
            self.set_y(8)
            self.set_font("CourierNew", "B", 8)
            self.set_text_color(*self.t["title_color"])
            short_title = (self.doc_title or "Documento").split(" — ")[0].strip()
            self.cell(0, 5, sanitize(short_title), align="C")
            self.set_draw_color(0, 0, 0)
            self.set_line_width(0.3)
            self.line(10, 14, 200, 14)
            self.set_y(18)

    def footer(self):
        self.set_y(-15)
        self.set_font("CourierNew", "", 8)
        self.set_text_color(*self.t["footer_color"])
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_chapter(self, level, title):
        self.start_section(title, level - 1)

    def chapter_title(self, level, text):
        sizes = {1: 16, 2: 13, 3: 11, 4: 10}
        if self.get_y() > 257:
            self.add_page()
        self.set_font("CourierNew", "B", sizes.get(level, 10))
        self.set_text_color(*self.t["title_color"])
        self.ln(4)
        self.multi_cell(0, 6, sanitize(text))
        if level <= 2:
            self.set_draw_color(*self.t["border_color"])
            self.set_line_width(0.3)
            self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(3)

    def body_text(self, text):
        self.set_font("CourierNew", "", 9)
        self.set_text_color(*self.t["body_color"])
        self.multi_cell(0, 5, sanitize(text))
        self.ln(2)

    def code_block(self, code):
        self.set_fill_color(*self.t["code_bg"])
        self.set_font("CourierNew", "", 7)
        self.set_text_color(*self.t["code_text"])
        y = self.get_y()
        lines = code.split("\n")
        h = min(len(lines), 80) * 3.5 + 6
        if y + h > 270:
            self.add_page()
        self.rect(10, self.get_y(), 190, h, "F")
        self.ln(3)
        for line in lines[:80]:
            self.set_x(14)
            self.cell(0, 3.5, sanitize(line[:100]))
            self.ln(3.5)
        self.ln(3)

    def image_block(self, alt_text: str, img_path: str, exists: bool):
        y = self.get_y()
        if y + 50 > 270:
            self.add_page()
            y = self.get_y()

        if exists:
            img_file = Path(img_path)
            parent = img_file.parent
            stem = img_file.stem
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                full_path = self.md_dir / parent / f"{stem}{ext}" if self.md_dir else None
                if full_path and full_path.exists():
                    try:
                        self.image(str(full_path), x=15, w=180)
                        self.ln(3)
                        return
                    except Exception as e:
                        print(f"Image error: {e}")
            try:
                self.image(img_path, x=15, w=180)
                self.ln(3)
                return
            except Exception as e:
                print(f"Image error: {e}")

        self.set_fill_color(*self.t["image_placeholder_bg"])
        self.set_draw_color(*self.t["image_placeholder_border"])
        y_start = self.get_y()
        box_h = 40
        self.rect(10, y_start, 190, box_h, "DF")

        self.set_font("CourierNew", "B", 8)
        self.set_text_color(*self.t["image_placeholder_text"])
        self.set_xy(12, y_start + 2)
        self.cell(186, 5, "[Imagen placeholder]")

        self.set_font("CourierNew", "", 6)
        self.set_text_color(80, 80, 80)
        self.set_xy(12, y_start + 8)

        prompt = alt_text
        max_chars = 280
        if len(prompt) > max_chars:
            prompt = prompt[:max_chars] + "..."

        self.multi_cell(186, 3.5, sanitize(prompt))
        self.set_y(y_start + box_h + 3)

    def mermaid_block(self, img_path: str, code: str = ""):
        from PIL import Image as PILImage
        y = self.get_y()
        max_w = 180
        max_h = 80
        if y + max_h > 270:
            self.add_page()
        try:
            with PILImage.open(img_path) as im:
                iw, ih = im.size
            ratio = iw / ih
            w = max_w
            h = w / ratio
            if h > max_h:
                h = max_h
                w = h * ratio
            x = 10 + (190 - w) / 2
            self.image(img_path, x=x, w=w, h=h)
            self.ln(5)
        except Exception:
            self.set_fill_color(*self.t["mermaid_bg"])
            self.set_draw_color(*self.t["mermaid_border"])
            y_start = self.get_y()
            self.rect(10, y_start, 190, 8, "DF")
            self.set_font("CourierNew", "B", 7)
            self.set_text_color(*self.t["mermaid_text"])
            self.set_x(12)
            self.cell(0, 8, "[Diagrama Mermaid - ver version Markdown para diagrama interactivo]")
            self.ln(9)

    def table_row(self, cells, is_header=False):
        self.set_font("CourierNew", "B" if is_header else "", 7)
        if is_header:
            self.set_fill_color(*self.t["table_header_bg"])
            self.set_text_color(*self.t["table_header_text"])
        else:
            self.set_fill_color(*self.t["table_row_bg"])
            self.set_text_color(*self.t["body_color"])
        n = max(len(cells), 1)
        w = 190 / n
        for cell in cells:
            self.cell(w, 5, sanitize(cell[:35]), border=1, fill=True)
        self.ln()

    def blockquote(self, text):
        self.set_font("CourierNew", "I", 9)
        self.set_text_color(*self.t["blockquote_color"])
        self.set_x(18)
        self.multi_cell(178, 5, sanitize(text))
        self.ln(3)

    def cover_page(self):
        self.set_fill_color(*self.t["cover_bg"])
        self.rect(0, 0, 210, 297, "F")

        self.set_draw_color(*self.t["title_color"])
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287, "D")

        title = self.doc_title or "Documento"
        parts = title.split(" — ", 1)
        line1 = parts[0].strip()
        line2 = parts[1].strip() if len(parts) > 1 else ""

        self.set_font("CourierNew", "B", 28)
        self.set_text_color(*self.t["title_color"])
        self.set_xy(15, 85)
        self.cell(180, 12, sanitize(line1), align="C")

        if line2:
            self.set_font("CourierNew", "B", 22)
            self.set_xy(15, 102)
            self.cell(180, 10, sanitize(line2), align="C")


def md_to_pdf(md_path: str, pdf_path: str | None = None, template_name: str = "vintage_light_pink"):
    md_file = Path(md_path)
    if not md_file.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)

    if pdf_path is None:
        short_name = template_name.replace("vintage_", "")
        pdf_path = str(md_file.with_suffix("")) + f"_{short_name}.pdf"

    template = TEMPLATES.get(template_name)
    if not template:
        print(f"Error: template '{template_name}' not found")
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    md_dir = md_file.parent
    md_text = md_file.read_text(encoding="utf-8")
    elements = parse_markdown(md_text, md_dir)

    mermaid_count = sum(1 for t, _ in elements if t == "mermaid")
    image_count = sum(1 for t, _ in elements if t == "image")
    if mermaid_count > 0:
        print(f"Rendering {mermaid_count} Mermaid diagrams...")
    if image_count > 0:
        print(f"Processing {image_count} images...")

    pdf = MarkdownPDF(md_dir=md_dir, template=template)

    for typ, val in elements:
        if typ == "h1":
            pdf.doc_title = val
            break

    found_title = False
    for typ, val in elements:
        if typ == "h1":
            found_title = True
            continue
        if found_title and typ in ("p", "blockquote"):
            if not pdf.doc_subtitle:
                pdf.doc_subtitle = val
            elif not pdf.doc_description:
                pdf.doc_description = val
                break

    pdf.add_page()
    pdf.cover_page()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        mermaid_cache = {}
        skip_first_h1 = True

        for typ, val in elements:
            if typ == "h1":
                pdf.add_chapter(1, val)
                if skip_first_h1:
                    skip_first_h1 = False
                    pdf.add_page()
                else:
                    pdf.add_page()
                    pdf.chapter_title(1, val)
            elif typ == "h2":
                pdf.add_chapter(2, val)
                pdf.chapter_title(2, val)
            elif typ == "h3":
                pdf.add_chapter(3, val)
                pdf.chapter_title(3, val)
            elif typ == "h4":
                pdf.add_chapter(4, val)
                pdf.chapter_title(4, val)
            elif typ == "code":
                pdf.code_block(val)
            elif typ == "mermaid":
                if val not in mermaid_cache:
                    img = render_mermaid(val, tmp_path)
                    mermaid_cache[val] = img
                img = mermaid_cache.get(val)
                if img:
                    pdf.mermaid_block(img, val)
                else:
                    pdf.set_fill_color(*template["mermaid_bg"])
                    pdf.set_draw_color(*template["mermaid_border"])
                    y_start = pdf.get_y()
                    if y_start + 10 > 270:
                        pdf.add_page()
                        y_start = pdf.get_y()
                    pdf.rect(10, y_start, 190, 8, "DF")
                    pdf.set_font("CourierNew", "B", 7)
                    pdf.set_text_color(*template["mermaid_text"])
                    pdf.set_x(12)
                    pdf.cell(0, 8, "[Diagrama Mermaid - ver version Markdown para diagrama interactivo]")
                    pdf.ln(9)
            elif typ == "image":
                alt_text, img_path, exists = val
                pdf.image_block(alt_text, img_path, exists)
            elif typ == "table":
                for j, row in enumerate(val):
                    pdf.table_row(row, is_header=(j == 0))
                pdf.ln(2)
            elif typ == "blockquote":
                pdf.blockquote(val)
            elif typ == "li":
                pdf.body_text(f"  - {val}")
            elif typ == "oli":
                pdf.body_text(f"  {val}")
            elif typ == "p":
                pdf.body_text(val)

    pdf.output(str(pdf_path))
    print(f"PDF generated: {pdf_path}")
    print(f"Template: {template['name']}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF with vintage templates")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output PDF file (optional)")
    parser.add_argument(
        "--template", "-t",
        choices=list(TEMPLATES.keys()),
        default="vintage_light_pink",
        help="Template to use (default: vintage_light_pink)"
    )
    args = parser.parse_args()
    md_to_pdf(args.input, args.output, args.template)
