import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HTMLTocEntry:
    level: int
    title: str
    id: str
    num: str = ""


def sanitize_html(text):
    for k, v in {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}.items():
        text = text.replace(k, v)
    return text


def make_id(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s]+', '-', text).strip('-')


def parse_inline_html(text):
    parts = []
    last = 0
    for m in re.finditer(r'`(.+?)`', text):
        parts.append(sanitize_html(text[last:m.start()]))
        parts.append('<code>' + sanitize_html(m.group(1)) + '</code>')
        last = m.end()
    parts.append(sanitize_html(text[last:]))
    result = ''.join(parts)
    result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)
    result = re.sub(r'\*(.+?)\*', r'<em>\1</em>', result)
    return result


def parse_markdown_to_html(md_text, md_dir=None):
    lines = md_text.split("\n")
    html_parts = []
    toc_entries = []
    i = 0
    in_code = False
    code_buf = []
    code_lang = ""
    in_table = False
    table_rows = []
    h_counter = [0, 0, 0, 0]
    img_pattern = re.compile(r'^!\[(.+?)\]\((.+?)\)$')

    def flush_table():
        nonlocal table_rows, in_table
        if table_rows:
            html_parts.append(render_table(table_rows))
            table_rows = []
        in_table = False

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            if in_code:
                if in_table:
                    flush_table()
                lang_attr = f' class="language-{code_lang}"' if code_lang else ''
                code_content = sanitize_html("\n".join(code_buf))
                lang_label = code_lang.upper() if code_lang else "CODE"
                html_parts.append(
                    '<div class="code-block">'
                    f'<div class="code-header" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\'none\'?\'block\':\'none\'">&#9654; {lang_label}</div>'
                    f'<pre><code{lang_attr}>{code_content}</code></pre></div>'
                )
                code_buf = []
                in_code = False
                code_lang = ""
            else:
                if in_table:
                    flush_table()
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
                flush_table()
                continue
            i += 1
            continue

        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if in_table and not stripped.startswith("|"):
            flush_table()

        img_match = img_pattern.match(stripped)
        if img_match:
            alt_text = img_match.group(1)
            img_path = img_match.group(2)
            html_parts.append(
                '<div class="image-container">'
                f'<img src="{sanitize_html(img_path)}" alt="{sanitize_html(alt_text)}" loading="lazy" onclick="this.style.transform=this.style.transform===\'scale(1.5)\'?\'scale(1)\':\'scale(1.5)\'">'
                f'<p class="image-caption">{sanitize_html(alt_text)}</p></div>'
            )
            i += 1
            continue

        if stripped.startswith("# ") and not stripped.startswith("##"):
            h_counter[0] += 1
            h_counter[1] = 0
            h_counter[2] = 0
            h_counter[3] = 0
            title = stripped[2:]
            num = str(h_counter[0])
            entry_id = make_id(title)
            toc_entries.append(HTMLTocEntry(1, title, entry_id, num))
            html_parts.append(
                f'<h1 id="{entry_id}" class="chapter-title">'
                f'<span class="chapter-num">{num}.</span> {parse_inline_html(title)}</h1>'
            )
        elif stripped.startswith("## "):
            h_counter[1] += 1
            h_counter[2] = 0
            h_counter[3] = 0
            title = stripped[3:]
            num = f"{h_counter[0]}.{h_counter[1]}"
            entry_id = make_id(title)
            toc_entries.append(HTMLTocEntry(2, title, entry_id, num))
            html_parts.append(
                f'<h2 id="{entry_id}" class="section-title">'
                f'<span class="section-num">{num}</span> {parse_inline_html(title)}</h2>'
            )
        elif stripped.startswith("### "):
            h_counter[2] += 1
            h_counter[3] = 0
            title = stripped[4:]
            num = f"{h_counter[0]}.{h_counter[1]}.{h_counter[2]}"
            entry_id = make_id(title)
            toc_entries.append(HTMLTocEntry(3, title, entry_id, num))
            html_parts.append(
                f'<h3 id="{entry_id}" class="subsection-title">{parse_inline_html(title)}</h3>'
            )
        elif stripped.startswith("#### "):
            h_counter[3] += 1
            title = stripped[5:]
            num = f"{h_counter[0]}.{h_counter[1]}.{h_counter[2]}.{h_counter[3]}"
            entry_id = make_id(title)
            toc_entries.append(HTMLTocEntry(4, title, entry_id, num))
            html_parts.append(
                f'<h4 id="{entry_id}" class="subsubsection-title">{parse_inline_html(title)}</h4>'
            )
        elif stripped.startswith("> "):
            content = parse_inline_html(stripped[2:])
            html_parts.append(f'<blockquote class="callout">{content}</blockquote>')
        elif stripped.startswith("---"):
            html_parts.append('<hr class="section-divider">')
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_parts.append(f'<li class="bullet-item">{parse_inline_html(stripped[2:])}</li>')
        elif re.match(r'^\d+\.\s', stripped):
            html_parts.append(f'<li class="numbered-item">{parse_inline_html(stripped)}</li>')
        else:
            html_parts.append(f'<p>{parse_inline_html(stripped)}</p>')

        i += 1

    if in_table:
        flush_table()

    return "\n".join(html_parts), toc_entries


def render_table(rows):
    if not rows:
        return ""
    html = '<div class="table-container"><table>'
    for j, row in enumerate(rows):
        tag = "th" if j == 0 else "td"
        html += "<tr>"
        for cell in row:
            html += f"<{tag}>{sanitize_html(cell)}</{tag}>"
        html += "</tr>"
    html += "</table></div>"
    return html


def build_toc_html(toc_entries):
    html = '<div class="toc-content">'
    for entry in toc_entries:
        indent_class = f"toc-level-{entry.level}"
        html += (
            f'<a href="#{entry.id}" class="toc-link {indent_class}" '
            f'data-level="{entry.level}">'
            f'<span class="toc-num">{entry.num}</span> {sanitize_html(entry.title)}'
            f'</a>'
        )
    html += '</div>'
    return html


def build_full_html(content, toc_html):
    return f'''<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>La Biblia del AIML 2.1</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-tertiary: #e9ecef;
            --text-primary: #212529;
            --text-secondary: #495057;
            --text-muted: #6c757d;
            --accent-primary: #1e3a5f;
            --accent-secondary: #277846;
            --accent-tertiary: #8e44ad;
            --border-color: #dee2e6;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.15);
            --code-bg: #2d3436;
            --code-text: #dcdcdc;
            --sidebar-width: 320px;
            --header-height: 56px;
            --font-size-base: 16px;
        }}

        [data-theme="dark"] {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent-primary: #58a6ff;
            --accent-secondary: #3fb950;
            --accent-tertiary: #bc8cff;
            --border-color: #30363d;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.3);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.4);
            --code-bg: #010409;
            --code-text: #c9d1d9;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: var(--font-size-base);
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.7;
            transition: background 0.3s, color 0.3s;
            overflow-x: hidden;
        }}

        /* ===== HEADER ===== */
        .header {{
            position: fixed; top: 0; left: 0; right: 0;
            height: var(--header-height);
            background: var(--accent-primary);
            color: white;
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 20px; z-index: 1000;
            box-shadow: var(--shadow-md);
        }}

        .header-left {{
            display: flex; align-items: center; gap: 16px;
        }}

        .header-title {{ font-size: 1.1rem; font-weight: 600; white-space: nowrap; }}

        .header-controls {{
            display: flex; gap: 8px; align-items: center;
        }}

        .btn {{
            padding: 6px 12px; border: none; border-radius: 6px;
            cursor: pointer; font-size: 0.85rem; font-weight: 500;
            transition: all 0.2s; background: rgba(255,255,255,0.15);
            color: white; display: flex; align-items: center; gap: 4px;
        }}

        .btn:hover {{ background: rgba(255,255,255,0.25); }}

        .search-box {{ position: relative; }}

        .search-box input {{
            padding: 7px 14px 7px 32px; border: none; border-radius: 20px;
            background: rgba(255,255,255,0.2); color: white;
            font-size: 0.85rem; width: 220px; transition: all 0.3s;
        }}

        .search-box input::placeholder {{ color: rgba(255,255,255,0.7); }}
        .search-box input:focus {{ outline: none; background: rgba(255,255,255,0.3); width: 280px; }}

        .search-box .search-icon {{
            position: absolute; left: 10px; top: 50%;
            transform: translateY(-50%); opacity: 0.7; font-size: 0.85rem;
        }}

        .search-results {{
            position: absolute; top: calc(100% + 4px); left: 0; right: 0;
            background: var(--bg-primary); border-radius: 8px;
            box-shadow: var(--shadow-lg); max-height: 300px; overflow-y: auto;
            display: none; z-index: 1001; border: 1px solid var(--border-color);
        }}

        .search-results.active {{ display: block; }}

        .search-result-item {{
            padding: 10px 14px; border-bottom: 1px solid var(--border-color);
            cursor: pointer; transition: background 0.2s;
        }}

        .search-result-item:hover {{ background: var(--bg-secondary); }}
        .search-result-item .result-title {{ font-weight: 500; color: var(--accent-primary); font-size: 0.9rem; }}
        .search-result-item .result-context {{ font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }}

        /* ===== SIDEBAR ===== */
        .sidebar {{
            position: fixed; top: var(--header-height); left: 0;
            width: var(--sidebar-width);
            bottom: 0;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            overflow-y: scroll; z-index: 900;
            transition: transform 0.3s ease;
            -webkit-overflow-scrolling: touch;
        }}

        .sidebar-header {{
            padding: 16px 18px 12px;
            border-bottom: 1px solid var(--border-color);
            background: var(--bg-secondary);
        }}

        .sidebar-header h3 {{
            font-size: 0.95rem; color: var(--accent-primary); font-weight: 600;
            margin-bottom: 8px;
        }}

        .sidebar-search {{
            width: 100%; padding: 7px 12px; border: 1px solid var(--border-color);
            border-radius: 6px; font-size: 0.82rem; background: var(--bg-primary);
            color: var(--text-primary); outline: none;
        }}

        .sidebar-search:focus {{ border-color: var(--accent-primary); }}

        .toc-content {{ padding: 8px 0; }}

        .toc-link {{
            display: block; padding: 6px 18px;
            color: var(--text-secondary); text-decoration: none;
            font-size: 0.82rem; transition: all 0.15s;
            border-left: 3px solid transparent; line-height: 1.4;
        }}

        .toc-link:hover {{
            background: var(--bg-tertiary);
            color: var(--accent-primary);
            border-left-color: var(--accent-primary);
        }}

        .toc-link.active {{
            background: var(--bg-tertiary);
            color: var(--accent-primary);
            border-left-color: var(--accent-primary);
            font-weight: 500;
        }}

        .toc-link.search-match {{
            background: rgba(255, 235, 59, 0.15);
            border-left-color: #f39c12;
        }}

        .toc-level-1 {{ padding-left: 18px; font-weight: 600; font-size: 0.85rem; }}
        .toc-level-2 {{ padding-left: 32px; }}
        .toc-level-3 {{ padding-left: 46px; font-size: 0.78rem; }}
        .toc-level-4 {{ padding-left: 58px; font-size: 0.75rem; color: var(--text-muted); }}

        .toc-num {{ color: var(--accent-secondary); font-weight: 600; margin-right: 5px; }}

        /* ===== MAIN CONTENT ===== */
        .main-content {{
            margin-left: var(--sidebar-width);
            padding: 36px 50px 60px;
            min-height: calc(100vh - var(--header-height));
        }}

        .chapter-title {{
            font-size: 1.9rem; color: var(--accent-primary);
            margin: 40px 0 18px; padding-bottom: 12px;
            border-bottom: 3px solid var(--accent-primary);
        }}

        .chapter-num {{ color: var(--accent-secondary); margin-right: 8px; }}

        .section-title {{
            font-size: 1.4rem; color: var(--accent-primary);
            margin: 32px 0 14px; padding-left: 14px;
            border-left: 4px solid var(--accent-secondary);
        }}

        .section-num {{ color: var(--accent-secondary); margin-right: 6px; font-weight: 600; }}

        .subsection-title {{ font-size: 1.15rem; color: var(--text-primary); margin: 24px 0 10px; }}
        .subsubsection-title {{ font-size: 0.95rem; color: var(--text-secondary); margin: 18px 0 8px; font-weight: 500; }}

        p {{ margin-bottom: 14px; }}

        .code-block {{
            margin: 18px 0; border-radius: 10px;
            overflow: hidden; box-shadow: var(--shadow-md);
        }}

        .code-header {{
            background: #3d4f5f; color: #88d498;
            padding: 6px 14px; font-family: 'Fira Code', monospace;
            font-size: 0.72rem; font-weight: 600; letter-spacing: 0.5px;
            cursor: pointer; user-select: none;
        }}

        .code-header:hover {{ background: #4a6070; }}

        pre {{
            background: var(--code-bg); color: var(--code-text);
            padding: 16px; overflow-x: auto;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem; line-height: 1.5;
        }}

        code {{
            font-family: 'Fira Code', monospace;
            background: var(--bg-tertiary); padding: 2px 5px;
            border-radius: 3px; font-size: 0.88em;
        }}

        pre code {{ background: none; padding: 0; }}

        .table-container {{
            margin: 18px 0; overflow-x: auto;
            border-radius: 8px; box-shadow: var(--shadow-sm);
        }}

        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}

        th {{
            background: var(--accent-primary); color: white;
            padding: 10px 14px; text-align: left; font-weight: 600;
        }}

        td {{ padding: 10px 14px; border-bottom: 1px solid var(--border-color); }}
        tr:nth-child(even) {{ background: var(--bg-secondary); }}
        tr:hover {{ background: var(--bg-tertiary); }}

        blockquote.callout {{
            margin: 18px 0; padding: 14px 18px;
            border-left: 4px solid var(--accent-tertiary);
            background: var(--bg-secondary);
            border-radius: 0 8px 8px 0;
            font-style: italic; color: var(--text-secondary);
        }}

        .image-container {{ margin: 22px 0; text-align: center; }}

        .image-container img {{
            max-width: 100%; height: auto; border-radius: 10px;
            box-shadow: var(--shadow-md); cursor: zoom-in;
            transition: transform 0.3s;
        }}

        .image-container img:hover {{ box-shadow: var(--shadow-lg); }}

        .image-caption {{
            margin-top: 8px; font-size: 0.82rem;
            color: var(--text-muted); font-style: italic;
        }}

        .section-divider {{
            margin: 36px 0; border: none;
            border-top: 2px solid var(--border-color);
        }}

        .bullet-item, .numbered-item {{
            margin: 6px 0 6px 22px;
        }}

        strong {{ color: var(--accent-primary); font-weight: 600; }}
        em {{ color: var(--accent-tertiary); }}

        /* ===== SETTINGS PANEL ===== */
        .settings-overlay {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5); z-index: 2000;
            display: none; align-items: center; justify-content: center;
        }}

        .settings-overlay.active {{ display: flex; }}

        .settings-panel {{
            background: var(--bg-primary); border-radius: 16px;
            padding: 28px 32px; width: 360px;
            box-shadow: var(--shadow-lg); border: 1px solid var(--border-color);
        }}

        .settings-panel h3 {{
            font-size: 1.1rem; color: var(--accent-primary);
            margin-bottom: 20px; padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        .setting-group {{ margin-bottom: 18px; }}

        .setting-group label {{
            display: block; font-size: 0.85rem; font-weight: 500;
            color: var(--text-secondary); margin-bottom: 8px;
        }}

        .setting-group .btn-group {{
            display: flex; gap: 8px;
        }}

        .setting-group .btn-option {{
            flex: 1; padding: 8px 12px; border: 2px solid var(--border-color);
            border-radius: 8px; background: var(--bg-secondary);
            color: var(--text-primary); cursor: pointer; font-size: 0.85rem;
            transition: all 0.2s; text-align: center;
        }}

        .setting-group .btn-option:hover {{
            border-color: var(--accent-primary);
        }}

        .setting-group .btn-option.active {{
            border-color: var(--accent-primary);
            background: var(--accent-primary); color: white;
        }}

        .font-size-slider {{
            width: 100%; margin-top: 4px;
            accent-color: var(--accent-primary);
        }}

        .settings-close {{
            width: 100%; padding: 10px; border: none; border-radius: 8px;
            background: var(--accent-primary); color: white;
            font-size: 0.9rem; font-weight: 500; cursor: pointer;
            margin-top: 8px; transition: opacity 0.2s;
        }}

        .settings-close:hover {{ opacity: 0.9; }}

        /* ===== BACK TO TOP ===== */
        .back-to-top {{
            position: fixed; bottom: 24px; right: 24px;
            width: 44px; height: 44px;
            background: var(--accent-primary); color: white;
            border: none; border-radius: 50%;
            cursor: pointer; font-size: 1.2rem;
            box-shadow: var(--shadow-lg);
            opacity: 0; visibility: hidden;
            transition: all 0.3s; z-index: 800;
        }}

        .back-to-top.visible {{ opacity: 1; visibility: visible; }}
        .back-to-top:hover {{ transform: translateY(-2px); }}

        /* ===== RESPONSIVE ===== */
        @media (max-width: 1024px) {{
            .sidebar {{
                transform: translateX(-100%);
            }}
            .sidebar.open {{
                transform: translateX(0);
                box-shadow: var(--shadow-lg);
            }}
            .main-content {{
                margin-left: 0;
                padding: 28px 20px;
            }}
            .search-box input {{ width: 160px; }}
            .search-box input:focus {{ width: 200px; }}
        }}

        @media print {{
            .header, .sidebar, .back-to-top, .settings-overlay {{ display: none !important; }}
            .main-content {{ margin: 0; padding: 20px; max-width: 100%; }}
        }}
    </style>
</head>
<body>

    <!-- HEADER -->
    <header class="header">
        <div class="header-left">
            <button class="btn" id="sidebarToggle" title="Mostrar/ocultar panel lateral">&#9776;</button>
            <span class="header-title">La Biblia del AIML 2.1</span>
        </div>
        <div class="header-controls">
            <div class="search-box">
                <span class="search-icon">&#128269;</span>
                <input type="text" id="searchInput" placeholder="Buscar...">
                <div class="search-results" id="searchResults"></div>
            </div>
            <button class="btn" id="settingsBtn" title="Configuracion">&#9881;</button>
            <button class="btn" id="themeToggle" title="Tema claro/oscuro">&#9788;</button>
        </div>
    </header>

    <!-- SIDEBAR -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>Tabla de Contenidos</h3>
            <input type="text" class="sidebar-search" id="sidebarSearch" placeholder="Filtrar secciones...">
        </div>
        {toc_html}
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content" id="mainContent">
        {content}
    </main>

    <!-- SETTINGS PANEL -->
    <div class="settings-overlay" id="settingsOverlay">
        <div class="settings-panel">
            <h3>&#9881; Configuracion</h3>

            <div class="setting-group">
                <label>Tamanio de fuente</label>
                <input type="range" class="font-size-slider" id="fontSizeSlider" min="12" max="22" value="16" step="1">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-muted);margin-top:4px;">
                    <span>12px</span>
                    <span id="fontSizeValue">16px</span>
                    <span>22px</span>
                </div>
            </div>

            <div class="setting-group">
                <label>Ancho del sidebar</label>
                <div class="btn-group">
                    <button class="btn-option" data-sidebar="260">Estrecho</button>
                    <button class="btn-option active" data-sidebar="320">Normal</button>
                    <button class="btn-option" data-sidebar="400">Ancho</button>
                </div>
            </div>

            <div class="setting-group">
                <label>Tema de colores</label>
                <div class="btn-group">
                    <button class="btn-option active" data-theme-btn="light">Claro</button>
                    <button class="btn-option" data-theme-btn="dark">Oscuro</button>
                </div>
            </div>

            <button class="settings-close" id="settingsClose">Cerrar</button>
        </div>
    </div>

    <!-- BACK TO TOP -->
    <button class="back-to-top" id="backToTop" title="Volver arriba">&#8593;</button>

    <script>
        // ===== ELEMENTS =====
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mainContent = document.getElementById('mainContent');
        const backToTop = document.getElementById('backToTop');
        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');
        const sidebarSearch = document.getElementById('sidebarSearch');
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsOverlay = document.getElementById('settingsOverlay');
        const settingsClose = document.getElementById('settingsClose');
        const themeToggle = document.getElementById('themeToggle');
        const fontSizeSlider = document.getElementById('fontSizeSlider');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const tocLinks = document.querySelectorAll('.toc-link');

        // ===== THEME =====
        let savedTheme = localStorage.getItem('aiml-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeIcon();
        updateThemeButtons();

        themeToggle.addEventListener('click', () => {{
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('aiml-theme', next);
            updateThemeIcon();
            updateThemeButtons();
        }});

        function updateThemeIcon() {{
            const t = document.documentElement.getAttribute('data-theme');
            themeToggle.innerHTML = t === 'light' ? '&#9788;' : '&#9790;';
        }}

        function updateThemeButtons() {{
            const t = document.documentElement.getAttribute('data-theme');
            document.querySelectorAll('[data-theme-btn]').forEach(btn => {{
                btn.classList.toggle('active', btn.getAttribute('data-theme-btn') === t);
            }});
        }}

        document.querySelectorAll('[data-theme-btn]').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const theme = btn.getAttribute('data-theme-btn');
                document.documentElement.setAttribute('data-theme', theme);
                localStorage.setItem('aiml-theme', theme);
                updateThemeIcon();
                updateThemeButtons();
            }});
        }});

        // ===== SIDEBAR TOGGLE =====
        sidebarToggle.addEventListener('click', () => {{
            sidebar.classList.toggle('open');
        }});

        // Close sidebar on click outside (mobile)
        mainContent.addEventListener('click', () => {{
            if (window.innerWidth <= 1024) {{
                sidebar.classList.remove('open');
            }}
        }});

        // ===== SCROLL =====
        window.addEventListener('scroll', () => {{
            backToTop.classList.toggle('visible', window.scrollY > 300);
            updateActiveTocLink();
        }});

        backToTop.addEventListener('click', () => {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});

        // ===== TOC ACTIVE LINK =====
        function updateActiveTocLink() {{
            const headings = document.querySelectorAll('h1[id], h2[id], h3[id], h4[id]');
            let current = '';
            headings.forEach(heading => {{
                if (heading.getBoundingClientRect().top <= 100) {{
                    current = heading.id;
                }}
            }});
            tocLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {{
                    link.classList.add('active');
                }}
            }});
        }}

        // ===== TOC CLICK =====
        tocLinks.forEach(link => {{
            link.addEventListener('click', (e) => {{
                e.preventDefault();
                const target = document.getElementById(link.getAttribute('href').substring(1));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    if (window.innerWidth <= 1024) {{
                        sidebar.classList.remove('open');
                    }}
                }}
            }});
        }});

        // ===== SIDEBAR SEARCH =====
        sidebarSearch.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            tocLinks.forEach(link => {{
                const text = link.textContent.toLowerCase();
                if (query && text.includes(query)) {{
                    link.classList.add('search-match');
                    link.style.display = '';
                }} else if (query) {{
                    link.classList.remove('search-match');
                    link.style.display = 'none';
                }} else {{
                    link.classList.remove('search-match');
                    link.style.display = '';
                }}
            }});
        }});

        // ===== HEADER SEARCH =====
        const contentSections = [];
        document.querySelectorAll('h1[id], h2[id], h3[id], h4[id]').forEach(heading => {{
            contentSections.push({{
                id: heading.id,
                title: heading.textContent,
                element: heading
            }});
        }});

        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            searchResults.innerHTML = '';
            if (query.length < 2) {{
                searchResults.classList.remove('active');
                return;
            }}
            const matches = contentSections.filter(s =>
                s.title.toLowerCase().includes(query)
            ).slice(0, 8);
            if (matches.length > 0) {{
                matches.forEach(match => {{
                    const item = document.createElement('div');
                    item.className = 'search-result-item';
                    item.innerHTML = '<div class="result-title">' + match.title + '</div>' +
                        '<div class="result-context">Ir a seccion...</div>';
                    item.addEventListener('click', () => {{
                        match.element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        searchResults.classList.remove('active');
                        searchInput.value = '';
                    }});
                    searchResults.appendChild(item);
                }});
                searchResults.classList.add('active');
            }} else {{
                searchResults.classList.remove('active');
            }}
        }});

        document.addEventListener('click', (e) => {{
            if (!e.target.closest('.search-box')) {{
                searchResults.classList.remove('active');
            }}
        }});

        // ===== SETTINGS =====
        settingsBtn.addEventListener('click', () => {{
            settingsOverlay.classList.add('active');
        }});

        settingsClose.addEventListener('click', () => {{
            settingsOverlay.classList.remove('active');
        }});

        settingsOverlay.addEventListener('click', (e) => {{
            if (e.target === settingsOverlay) {{
                settingsOverlay.classList.remove('active');
            }}
        }});

        // Font size
        let savedFontSize = localStorage.getItem('aiml-fontsize') || '16';
        document.documentElement.style.setProperty('--font-size-base', savedFontSize + 'px');
        fontSizeSlider.value = savedFontSize;
        fontSizeValue.textContent = savedFontSize + 'px';

        fontSizeSlider.addEventListener('input', (e) => {{
            const size = e.target.value;
            document.documentElement.style.setProperty('--font-size-base', size + 'px');
            fontSizeValue.textContent = size + 'px';
            localStorage.setItem('aiml-fontsize', size);
        }});

        // Sidebar width
        let savedSidebarWidth = localStorage.getItem('aiml-sidebar') || '320';
        document.documentElement.style.setProperty('--sidebar-width', savedSidebarWidth + 'px');
        document.querySelectorAll('[data-sidebar]').forEach(btn => {{
            btn.classList.toggle('active', btn.getAttribute('data-sidebar') === savedSidebarWidth);
            btn.addEventListener('click', () => {{
                const w = btn.getAttribute('data-sidebar');
                document.documentElement.style.setProperty('--sidebar-width', w + 'px');
                localStorage.setItem('aiml-sidebar', w);
                document.querySelectorAll('[data-sidebar]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            }});
        }});

        // Init
        updateActiveTocLink();
    </script>
</body>
</html>'''


def md_to_html(md_path: str, html_path: Optional[str] = None):
    md_file = Path(md_path)
    if not md_file.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)

    if html_path is None:
        html_path = md_file.with_suffix(".html")

    md_dir = md_file.parent
    md_text = md_file.read_text(encoding="utf-8")

    content, toc_entries = parse_markdown_to_html(md_text, md_dir)
    toc_html = build_toc_html(toc_entries)
    final_html = build_full_html(content, toc_html)

    html_file = Path(html_path)
    html_file.write_text(final_html, encoding="utf-8")

    print(f"HTML generated: {html_path}")
    print(f"TOC entries: {len(toc_entries)}")
    print(f"File size: {html_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <input.md> [output.html]")
        sys.exit(1)

    input_md = sys.argv[1]
    output_html = sys.argv[2] if len(sys.argv) > 2 else None
    md_to_html(input_md, output_html)
