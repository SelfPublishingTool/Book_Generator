#!/usr/bin/env python3
"""Build Kindle-optimized HTML from book.json for Amazon KDP.

Output: High_Protein_Meal_Prep_Cookbook_Kindle.html (in root dir)
Single self-contained file — images embedded as base64 JPEG data URIs.
Upload this HTML directly to KDP (no ZIP needed).

Key differences from paperback build:
- Reflowable layout (no fixed 8.5x11 pages)
- epub:type TOC for Kindle navigation panel
- No JavaScript (Kindle doesn't execute it)
- Single-column recipe layout
- em-based typography (no pt units)
"""
import json, html, re, base64, io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

book = json.loads((BASE_DIR / 'book.json').read_text(encoding='utf-8'))


def esc(s):
    return html.escape(s, quote=True) if s else ''

def smart_html(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(^|\W)\*(.+?)\*(?=\W|$)', r'\1<em>\2</em>', s)
    return s

# ─── CSS ───────────────────────────────────────────────────────────────────────
css = """
/* === Kindle-safe reset === */
body {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1em;
  line-height: 1.6;
  color: #1a1a1a;
  margin: 0;
  padding: 0;
}

/* === Title page === */
.title-page {
  text-align: center;
  padding: 3em 1em;
}
.book-title {
  font-size: 2em;
  font-weight: bold;
  line-height: 1.2;
  margin: 0 0 0.5em;
}
.book-subtitle {
  font-size: 1em;
  font-style: italic;
  color: #444;
  margin: 0 0 2em;
}
.book-author {
  font-size: 1.1em;
  font-weight: bold;
  margin: 0;
}
.title-divider {
  border: none;
  border-top: 2px solid #c69c00;
  width: 60px;
  margin: 1.5em auto;
}

/* === Copyright === */
.copyright-page {
  font-size: 0.85em;
  line-height: 1.5;
  padding: 2em 0;
}
.copyright-page h2 {
  font-size: 1em;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  text-align: center;
  margin-bottom: 1em;
}

/* === TOC === */
nav#toc {
  padding: 1em 0;
}
nav#toc h2 {
  font-size: 1.4em;
  text-align: center;
  margin-bottom: 0.8em;
  color: #c69c00;
}
nav#toc ol {
  list-style: none;
  padding: 0;
  margin: 0;
}
nav#toc ol li {
  margin-bottom: 0.5em;
  border-bottom: 1px dotted #ccc;
  padding-bottom: 0.4em;
}
nav#toc ol li a {
  text-decoration: none;
  color: #1a1a1a;
  font-size: 0.95em;
}
nav#toc ol li a:hover {
  color: #c69c00;
}
nav#toc ol li.toc-chapter {
  font-weight: bold;
  font-size: 1em;
}
nav#toc ol li.toc-chapter a {
  font-size: 1em;
}

/* === Chapter headings === */
.chapter-section {
  padding: 1em 0;
}
.chapter-eyebrow {
  font-size: 0.8em;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  color: #c69c00;
  font-family: Arial, sans-serif;
  margin: 0 0 0.3em;
}
h1.chapter-title {
  font-size: 1.8em;
  font-weight: bold;
  line-height: 1.2;
  margin: 0 0 0.3em;
  color: #1a1a1a;
}
.chapter-subtitle {
  font-size: 1.1em;
  font-style: italic;
  color: #555;
  margin: 0 0 0.5em;
}
.chapter-rule {
  border: none;
  border-top: 2px solid #c69c00;
  width: 50px;
  margin: 0.5em 0 1.2em;
}
.chapter-intro {
  margin: 1em 0 1.5em;
}
.chapter-intro p {
  margin: 0 0 0.8em;
  text-align: justify;
}

/* === Chapter strategy box === */
.strategy-box {
  border: 1px solid #c69c00;
  padding: 0.8em 1em;
  margin: 1em 0;
  background: #fffdf0;
}
.strategy-box h3 {
  font-size: 0.8em;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #c69c00;
  margin: 0 0 0.5em;
  font-family: Arial, sans-serif;
}
.strategy-box ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.strategy-box ul li {
  font-size: 0.9em;
  padding: 0.2em 0 0.2em 1.2em;
  position: relative;
}
.strategy-box ul li::before {
  content: "*";
  position: absolute;
  left: 0;
  color: #c69c00;
  font-weight: bold;
}

/* === Prose === */
.prose p {
  margin: 0 0 0.8em;
  text-align: justify;
}
.prose p strong { color: #7a5f00; }

/* === CH1 sections === */
.ch1-section {
  margin: 1.2em 0;
}
.ch1-section h2 {
  font-size: 1.2em;
  color: #7a5f00;
  border-bottom: 1px solid #e0d5b0;
  padding-bottom: 0.2em;
  margin-bottom: 0.6em;
}

/* === Tables === */
table.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: Arial, sans-serif;
  font-size: 0.85em;
  margin: 0.8em 0;
}
table.data-table th {
  background: #c69c00;
  color: #fff;
  text-align: left;
  padding: 5px 8px;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
table.data-table td {
  padding: 4px 8px;
  border-bottom: 1px solid #e0d5b0;
  vertical-align: top;
}
table.data-table tbody tr:nth-child(even) td {
  background: #fdf9ed;
}

/* === Recipe card === */
.recipe {
  border: 1px solid #e0d5b0;
  border-left: 4px solid #c69c00;
  padding: 1em;
  margin: 1.5em 0;
  page-break-inside: avoid;
}
.recipe-img {
  width: 100%;
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 0 0.8em;
}
.recipe-badge-num {
  display: inline-block;
  background: #1a1a1a;
  color: #c69c00;
  font-weight: bold;
  font-size: 0.85em;
  padding: 2px 8px;
  border-radius: 3px;
  margin-right: 0.4em;
  font-family: Georgia, serif;
}
.recipe-title {
  font-size: 1.3em;
  font-weight: bold;
  margin: 0.3em 0 0.5em;
  line-height: 1.2;
}
.recipe-meta {
  font-family: Arial, sans-serif;
  font-size: 0.8em;
  color: #555;
  margin: 0 0 0.8em;
}
.recipe-meta span {
  display: inline-block;
  margin-right: 0.8em;
  background: #fdf3d0;
  border: 1px solid #e0d5b0;
  padding: 2px 6px;
  border-radius: 3px;
}
.recipe-meta .meta-protein {
  background: #fff5ce;
  border-color: #c69c00;
  color: #1a1a1a;
}
.recipe-section-head {
  font-family: Arial, sans-serif;
  font-size: 0.75em;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #c69c00;
  border-bottom: 1px solid #c69c00;
  padding-bottom: 2px;
  margin: 0.8em 0 0.4em;
}
.ingredients-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.5em;
  font-size: 0.9em;
}
.ingredients-list li {
  padding: 0.15em 0 0.15em 1em;
  position: relative;
}
.ingredients-list li::before {
  content: "•";
  color: #c69c00;
  position: absolute;
  left: 0;
}
.instructions-list {
  padding-left: 1.4em;
  margin: 0 0 0.5em;
  font-size: 0.9em;
}
.instructions-list li {
  margin-bottom: 0.35em;
}
.instructions-list li::marker { color: #7a5f00; }

/* === Nutrition box === */
.nutrition-box {
  background: #1a1a1a;
  color: #c69c00;
  padding: 0.5em 0.8em;
  margin: 0.8em 0 0.5em;
  font-family: Arial, sans-serif;
}
.nutrition-box-title {
  font-size: 0.75em;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: bold;
  margin: 0 0 0.3em;
}
.nutrition-grid {
  display: table;
  width: 100%;
  font-size: 0.9em;
}
.nutrition-row {
  display: table-row;
}
.nutrition-cell {
  display: table-cell;
  padding: 2px 8px 2px 0;
  color: #fff;
}
.nutrition-cell strong {
  display: block;
  font-size: 1.1em;
  color: #fde08a;
}
.nutrition-label {
  font-size: 0.7em;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #c69c00;
}

.storage-note {
  font-size: 0.8em;
  color: #555;
  font-style: italic;
  border-left: 2px solid #c69c00;
  padding: 0.2em 0.6em;
  margin-top: 0.4em;
}
.storage-label {
  font-style: normal;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.75em;
  color: #7a5f00;
}

/* === Meal plan === */
.week-title {
  font-size: 1.4em;
  color: #7a5f00;
  margin: 1.5em 0 0.3em;
}
.week-rule {
  border: none;
  border-top: 2px solid #c69c00;
  width: 50px;
  margin: 0.2em 0 0.8em;
}
.week-objective {
  background: #fff5ce;
  border-left: 3px solid #c69c00;
  padding: 0.4em 0.8em;
  font-style: italic;
  font-size: 0.9em;
  margin: 0.4em 0;
}
.week-callout {
  background: #f7f0e0;
  border-left: 3px solid #7a5f00;
  padding: 0.4em 0.8em;
  font-style: italic;
  font-size: 0.9em;
  margin: 0.4em 0;
}
.week-h {
  font-family: Arial, sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.85em;
  color: #7a5f00;
  font-weight: bold;
  margin: 0.8em 0 0.3em;
  border-bottom: 1px solid #c69c00;
  padding-bottom: 2px;
}

/* === Bonus === */
.bonus-section {
  margin: 1.5em 0;
}
.bonus-section h2 {
  font-size: 1.3em;
  color: #1a1a1a;
  margin-bottom: 0.5em;
}
.bonus-h3 { font-size: 1.1em; color: #7a5f00; margin: 0.8em 0 0.3em; }
.bonus-h4 {
  font-family: Arial, sans-serif;
  font-size: 0.8em;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #7a5f00;
  font-weight: bold;
  margin: 0.8em 0 0.3em;
}
.bonus-q { font-weight: bold; font-size: 0.95em; margin: 0.8em 0 0.3em; }
.hint {
  font-family: Arial, sans-serif;
  font-size: 0.88em;
  border-radius: 4px;
  padding: 4px 8px;
  margin: 0.25em 0;
  border: 1px solid transparent;
}
.hint-pos  { background: #fff5ce; border-left: 3px solid #c69c00; }
.hint-neg  { background: #fff0f0; border-left: 3px solid #c05050; color: #700; }
.hint-hack { background: #fdfaf0; border-left: 3px solid #7a5f00; font-style: italic; }
.hint-session { background: #f0f5ff; border-left: 3px solid #2196f3; font-weight: bold; }
.hint-level { background: #f9f0ff; border-left: 3px solid #9c27b0; font-weight: 800; text-transform: uppercase; }
.score-bucket {
  background: #c69c00;
  color: #fff;
  font-weight: bold;
  text-transform: uppercase;
  padding: 5px 10px;
  font-size: 0.9em;
  margin: 0.8em 0;
  font-family: Arial, sans-serif;
}
.quiz-opts { margin: 0.4em 0 0.8em; }
.quiz-opt {
  border: 1px solid #e0d5b0;
  padding: 4px 8px;
  margin-bottom: 4px;
  font-size: 0.85em;
  background: #fdfaf0;
}
.restaurant-name {
  font-size: 1.1em;
  font-weight: bold;
  color: #1a1a1a;
  margin: 0.8em 0 0.2em;
  border-bottom: 1px solid #e0d5b0;
  padding-bottom: 2px;
}

/* === Appendix === */
.appendix-section { padding: 1em 0; }
.conv-grid { margin: 1em 0; }
.conv-card {
  border: 1px solid #e0d5b0;
  padding: 0.8em;
  margin-bottom: 1em;
  background: #fdfaf0;
}
.conv-card h3 {
  font-size: 1.1em;
  color: #7a5f00;
  margin: 0 0 0.4em;
}

/* === Conclusion / review === */
.conclusion-section { padding: 1em 0; }
.review-section { text-align: center; padding: 2em 0; }
.end-mark {
  margin-top: 2em;
  letter-spacing: 0.3em;
  color: #7a5f00;
  font-family: Arial, sans-serif;
  font-size: 0.9em;
}

/* === Page break hints for Kindle === */
.chapter-section { page-break-before: always; }
.title-page { page-break-after: always; }
nav#toc { page-break-after: always; }
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────
def render_table(rows):
    if not rows:
        return ''
    head = rows[0]; body = rows[1:]
    thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
    tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
    return f'<table class="data-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>'

def render_body_lines_generic(lines):
    """Render a list of body text lines — handles markdown tables and paragraphs."""
    out = []
    i = 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.strip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rl = lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|$', rl):
                    cells = [c.strip() for c in rl.split('|')[1:-1]]
                    if any(c for c in cells):
                        rows.append(cells)
                i += 1
            out.append(render_table(rows))
        else:
            out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

def render_ch1_section(sec):
    body_html = render_body_lines_generic(sec['body'])
    return f'<div class="ch1-section"><h2>{esc(sec["heading"])}</h2><div class="prose">{body_html}</div></div>'

def render_week_body(lines):
    out = []
    i = 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.strip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rl = lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|$', rl):
                    cells = [c.strip() for c in rl.split('|')[1:-1]]
                    if any(c for c in cells):
                        rows.append(cells)
                i += 1
            out.append(render_table(rows))
        elif l.endswith(':') and not l.startswith('|') and not l.startswith(' '):
            out.append(f'<p class="week-h">{esc(l[:-1])}</p>')
            i += 1
        elif l.startswith('Objective:'):
            out.append(f'<p class="week-objective">{smart_html(l)}</p>')
            i += 1
        elif l.startswith('Swap It this week:') or l.startswith('Beyond Week'):
            out.append(f'<p class="week-callout">{smart_html(l)}</p>')
            i += 1
        else:
            out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

def render_bonus_body(lines):
    out = []
    i = 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.startswith('### '):
            out.append(f'<p class="bonus-h3">{esc(l[4:].strip())}</p>')
            i += 1
        elif l == l.upper() and len(l) > 3 and re.match(r'^[A-Z &]+$', l):
            out.append(f'<p class="bonus-h4">{esc(l)}</p>')
            i += 1
        elif l.strip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rl = lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|$', rl):
                    cells = [c.strip() for c in rl.split('|')[1:-1]]
                    if any(c for c in cells):
                        rows.append(cells)
                i += 1
            out.append(render_table(rows))
        elif re.match(r'^\d+[–\-]\d+ points', l):
            out.append(f'<p class="score-bucket">{smart_html(l)}</p>')
            i += 1
        elif l.endswith(':') and len(l) < 60 and not any(l.startswith(x) for x in ['✅','❌','Session','⏱️']):
            out.append(f'<p class="bonus-q">{esc(l[:-1])}</p>')
            i += 1
        elif any(l.startswith(x) for x in ['✅','❌','Protein hack','Pro Tip','Session','Session A','Session B','BEGINNER','INTERMEDIATE','ADVANCED']):
            cls = 'hack'
            if l.startswith('✅'): cls = 'pos'
            elif l.startswith('❌'): cls = 'neg'
            elif 'Session' in l: cls = 'session'
            elif any(x in l for x in ['BEGINNER','INTERMEDIATE','ADVANCED']): cls = 'level'
            display_l = l
            if 'Session' in l and not l.startswith('⏱️'): display_l = '⏱️ ' + l
            elif any(x in l for x in ['BEGINNER','INTERMEDIATE','ADVANCED']) and not l.startswith('💪'): display_l = '💪 ' + l
            out.append(f'<p class="hint hint-{cls}">{smart_html(display_l)}</p>')
            i += 1
        elif re.search(r'[abc]\) .*\| [abc]\) ', l):
            opts = [o.strip() for o in l.split('|')]
            opts_html = ''.join(f'<td class="quiz-opt">{smart_html(o)}</td>' for o in opts)
            out.append(f'<table class="quiz-opts-table"><tr>{opts_html}</tr></table>')
            i += 1
        elif len(l) < 40 and i+1 < len(lines) and any(lines[i+1].strip().startswith(x) for x in ['✅','❌','Protein hack']):
            out.append(f'<p class="restaurant-name">{esc(l)}</p>')
            i += 1
        else:
            out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

def render_recipe(r):
    # Parse nutrition
    nut = r.get('nutrition', '')
    stats = []
    for label_re, label in [(r'Calories:\s*(\d+)', 'Cal'),
                             (r'Protein:\s*(\d+)g?', 'Protein'),
                             (r'Carbs:\s*(\d+)g?', 'Carbs'),
                             (r'Fat:\s*(\d+)g?', 'Fat')]:
        mm = re.search(label_re, nut)
        if mm:
            v = mm.group(1)
            unit = '' if label == 'Cal' else 'g'
            stats.append((label, v + unit))

    nut_cells = ''.join(
        f'<td class="nutrition-cell"><strong>{esc(v)}</strong><span class="nutrition-label">{esc(l)}</span></td>'
        for l, v in stats
    )
    nut_html = f'''<div class="nutrition-box">
  <div class="nutrition-box-title">Nutrition {esc(r.get("nutrition_extra",""))}</div>
  <table class="nutrition-grid" style="width:100%;border-collapse:collapse;">
    <tr>{nut_cells}</tr>
  </table>
</div>'''

    storage = r.get('storage', '')
    storage_html = f'<div class="storage-note"><span class="storage-label">Storage:</span> {smart_html(storage)}</div>' if storage else ''

    img_path = r.get('image_path', '')
    img_html = f'<img src="{esc(img_path)}" class="recipe-img" alt="{esc(r["title"])}">' if img_path else ''

    # Protein source — strip emoji prefix for cleaner display
    ps = r.get('protein_source', '')
    m = re.match(r'^([\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF☀-➿]+\s*\+?\s*[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF☀-➿]*)\s*(.+)$', ps)
    ps_emoji = m.group(1).strip() if m else ''
    ps_text  = m.group(2).strip() if m else ps

    ing_items  = ''.join(f'<li>{smart_html(i)}</li>' for i in r['ingredients'])
    inst_items = ''.join(f'<li>{smart_html(i)}</li>' for i in r['instructions'])
    cook_label = r.get('cook_label', 'Cook')

    return f'''<article id="recipe-{r['number']}" class="recipe">
  {img_html}
  <span class="recipe-badge-num">{r['number']:02d}</span>
  <h3 class="recipe-title">{esc(r['title'])}</h3>
  <div class="recipe-meta">
    <span class="meta-protein">{esc(ps_emoji)} {esc(ps_text)}</span>
    <span>Yield: {esc(r['yield'])}</span>
    <span>Prep: {esc(r['prep'])}</span>
    <span>{esc(cook_label)}: {esc(r['cook'])}</span>
  </div>
  <p class="recipe-section-head">Ingredients</p>
  <ul class="ingredients-list">{ing_items}</ul>
  <p class="recipe-section-head">Instructions</p>
  <ol class="instructions-list">{inst_items}</ol>
  {nut_html}
  {storage_html}
</article>'''

# ─── Chapter strategy bullets ─────────────────────────────────────────────────
STRATEGIES = {
    'Introduction': ['Master the Protein Leverage Protocol', 'Eliminate Decision Fatigue', 'Set Up Your Fail-Safe Infrastructure'],
    'Chapter 1':    ['Audit Your Kitchen Tools', 'Master Sunday Prep Sessions', 'Learn the 4-Day Fridge Rule'],
    'Chapter 2':    ['Stabilize Morning Blood Sugar', 'Prep Grab-and-Go Egg Bites', 'Hit 25g Protein Before Your First Meeting'],
    'Chapter 3':    ['Build Resilient Salad Jars', 'Beat the 3:00 PM Slump', 'Reclaim 5 Hours of Your Work Week'],
    'Chapter 4':    ['Master Sheet-Pan Efficiency', 'Support Overnight Recovery', 'Minimize Post-Work Cooking Friction'],
    'Chapter 5':    ['Create a Tactical Snack Defense', 'Bridge the Gap Between Meals', 'Optimize Your Satiety-to-Calorie Ratio'],
    'Chapter 6':    ['Build a Freezer Library', 'Master High-Volume Satiety', 'Experience One-Pot Simplicity'],
    'Chapter 7':    ['Enjoy Metabolic Dessert Hacks', 'Experience Guilt-Free Consistency', 'Satisfy Cravings with Real Food'],
    'Chapter 8':    ['Build Your Flavor Infrastructure', 'Master High-Protein Bases', 'Control Your Satiety with Custom Sauces'],
    'Chapter 9':    ['Navigate the 21-Day Roadmap', 'Master the Art of the Batch', 'Follow the Shopping Blueprint'],
    'Chapter 10':   ['Survive Any Restaurant Menu', 'Apply Real-World Efficiency Hacks', 'Build Your High-Protein Pantry'],
}

def strategy_box(key):
    items = STRATEGIES.get(key, ['Maximize Protein Intake', 'Maintain Low-Carb Consistency', 'Automate Your Weekly Success'])
    lis = ''.join(f'<li>{esc(s)}</li>' for s in items)
    return f'<div class="strategy-box"><h3>Chapter Strategy</h3><ul>{lis}</ul></div>'

# ─── Build TOC entries list (populated as we build content) ───────────────────
toc_entries = []  # list of (id, label, level)  level: 1=chapter, 2=sub

# ─── Build body ───────────────────────────────────────────────────────────────
sections = []

# 1. Title page
sections.append(f'''<section class="title-page" epub:type="titlepage" id="title-page">
  <h1 class="book-title">{esc(book['title'])}</h1>
  <hr class="title-divider">
  <p class="book-subtitle">{esc(book['subtitle'])}</p>
  <hr class="title-divider">
  <p class="book-author">{esc(book['author'].replace("By ",""))}</p>
</section>''')

# 2. Copyright page
discl = ''.join(f'<p>{smart_html(p)}</p>' for p in book['disclaimer'])
sections.append(f'''<section class="copyright-page" epub:type="copyright-page" id="copyright-page">
  <h2>Copyright</h2>
  <p>{smart_html(book['copyright'])}</p>
  {discl}
</section>''')

# TOC placeholder — will be inserted after we collect all entries
TOC_PLACEHOLDER = '<!-- TOC_PLACEHOLDER -->'
sections.append(TOC_PLACEHOLDER)

# 4. Introduction
intro = book['introduction']
toc_entries.append(('introduction', 'Introduction — ' + intro['subtitle'], 1))
intro_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in intro['paragraphs'])
sections.append(f'''<section class="chapter-section" epub:type="chapter" id="introduction">
  <p class="chapter-eyebrow">Introduction</p>
  <h1 class="chapter-title">{esc(intro['subtitle'])}</h1>
  <hr class="chapter-rule">
  {strategy_box('Introduction')}
  <div class="prose">{intro_paras}</div>
</section>''')

# 5. Chapter 1
ch1 = book['chapter1']
toc_entries.append(('ch-1', 'Chapter 1 — ' + ch1['subtitle'], 1))
ch1_sections_html = ''.join(render_ch1_section(s) for s in ch1['sections'])
sections.append(f'''<section class="chapter-section" epub:type="chapter" id="ch-1">
  <p class="chapter-eyebrow">Chapter 1</p>
  <h1 class="chapter-title">{esc(ch1['subtitle'])}</h1>
  <hr class="chapter-rule">
  {strategy_box('Chapter 1')}
  {ch1_sections_html}
</section>''')

# 6. Recipe chapters (2-8)
chapter_recipe_groups = {}
for r in book['recipes']:
    chapter_recipe_groups.setdefault(r['chapter'], []).append(r)

chapter_meta_lookup = {c['title']: c for c in book['chapters_meta']}
chapter_nums = {
    'Chapter 2': 2, 'Chapter 3': 3, 'Chapter 4': 4,
    'Chapter 5': 5, 'Chapter 6': 6, 'Chapter 7': 7, 'Chapter 8': 8,
}

for ch_key in ['Chapter 2','Chapter 3','Chapter 4','Chapter 5','Chapter 6','Chapter 7','Chapter 8']:
    meta = chapter_meta_lookup[ch_key]
    rs = chapter_recipe_groups[ch_key]
    num = chapter_nums[ch_key]
    sec_id = f'ch-{num}'
    label = f'{ch_key} — {meta["subtitle"]}'
    toc_entries.append((sec_id, label, 1))

    intro_paras_html = ''
    if meta.get('intro'):
        intro_paras_html = ''.join(f'<p>{smart_html(p.strip())}</p>' for p in meta['intro'].split('\n\n') if p.strip())

    recipes_html = ''.join(render_recipe(r) for r in rs)

    sections.append(f'''<section class="chapter-section" epub:type="chapter" id="{sec_id}">
  <p class="chapter-eyebrow">{esc(ch_key)}</p>
  <h1 class="chapter-title">{esc(meta['subtitle'])}</h1>
  {f'<p class="chapter-subtitle">{esc(meta.get("quote",""))}</p>' if meta.get('quote') else ''}
  <hr class="chapter-rule">
  {strategy_box(ch_key)}
  <div class="chapter-intro prose">{intro_paras_html}</div>
  {recipes_html}
</section>''')

# 7. Meal Plan (Chapter 9)
mp = book['mealplan']
toc_entries.append(('ch-9', 'Chapter 9 — ' + mp['subtitle'], 1))
mp_intro_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in mp.get('intro_paragraphs', []))
mp_htr = ''.join(f'<li>{smart_html(p)}</li>' for p in mp.get('how_to_read', []))
mp_intro_block = ''
if mp.get('intro'):
    mp_intro_block = ''.join(f'<p>{smart_html(p.strip())}</p>' for p in mp['intro'].split('\n\n') if p.strip())

weeks_html = ''
for w in mp['weeks']:
    body_html = render_week_body(w['body_lines'])
    weeks_html += f'''<div class="week-section">
  <h2 class="week-title">{esc(w['title'])}</h2>
  <hr class="week-rule">
  <div class="prose">{body_html}</div>
</div>'''

sections.append(f'''<section class="chapter-section" epub:type="chapter" id="ch-9">
  <p class="chapter-eyebrow">Chapter 9</p>
  <h1 class="chapter-title">{esc(mp['subtitle'])}</h1>
  <hr class="chapter-rule">
  {strategy_box('Chapter 9')}
  <div class="chapter-intro prose">{mp_intro_block}</div>
  <div class="prose">{mp_intro_paras}</div>
  {f'<ul>{mp_htr}</ul>' if mp_htr else ''}
  {weeks_html}
</section>''')

# 8. Bonus Toolkit (Chapter 10)
bonus = book['bonus']
toc_entries.append(('ch-10', 'Chapter 10 — Your Bonus Toolkit', 1))
bonus_intro = ''
if bonus.get('intro'):
    bonus_intro = ''.join(f'<p>{smart_html(p.strip())}</p>' for p in bonus['intro'].split('\n\n') if p.strip())

bonuses_html = ''
for b in bonus['bonuses']:
    body_html = render_bonus_body(b['body_lines'])
    bonuses_html += f'''<div class="bonus-section">
  <h2>{esc(b['title'])}</h2>
  <div class="prose">{body_html}</div>
</div>'''

sections.append(f'''<section class="chapter-section" epub:type="chapter" id="ch-10">
  <p class="chapter-eyebrow">Chapter 10</p>
  <h1 class="chapter-title">Your Bonus Toolkit</h1>
  <hr class="chapter-rule">
  {strategy_box('Chapter 10')}
  <div class="chapter-intro prose">{bonus_intro}</div>
  {bonuses_html}
</section>''')

# 9. Appendix A
appA = book['appendix_a']
toc_entries.append(('appendix-a', 'Appendix A — ' + appA['sub'], 1))
rows = appA['rows']
app_a_chunks = [rows[1:][i:i+50] for i in range(0, len(rows[1:]), 50)]
app_a_html = ''
for k, chunk in enumerate(app_a_chunks):
    app_a_html += render_table([rows[0]] + chunk)

sections.append(f'''<section class="chapter-section appendix-section" epub:type="appendix" id="appendix-a">
  <p class="chapter-eyebrow">Appendix A</p>
  <h1 class="chapter-title">{esc(appA['sub'])}</h1>
  <hr class="chapter-rule">
  <p class="prose"><em>{smart_html(appA['intro'])}</em></p>
  {app_a_html}
</section>''')

# 10. Appendix B
appB = book['appendix_b']
toc_entries.append(('appendix-b', 'Appendix B — Protein Content & Conversion Charts', 1))

foods_header = appB['foods'][0]; foods_body = appB['foods'][1:]
foods_html = render_table([foods_header] + foods_body)

def render_conv_table_kindle(label, rows):
    head = rows[0]; body = rows[1:]
    tbl = render_table(rows)
    return f'<div class="conv-card"><h3>{esc(label)}</h3>{tbl}</div>'

vol_html  = render_conv_table_kindle('Volume', appB['volume'])
wt_html   = render_conv_table_kindle('Weight', appB['weight'])
oven_html = render_conv_table_kindle('Oven Temperature', appB['oven'])

sections.append(f'''<section class="chapter-section appendix-section" epub:type="appendix" id="appendix-b">
  <p class="chapter-eyebrow">Appendix B</p>
  <h1 class="chapter-title">Protein Content of 50 Common Foods</h1>
  <hr class="chapter-rule">
  {foods_html}
  <h2 style="margin-top:1.5em;">Measurement Conversion Charts</h2>
  <div class="conv-grid">{vol_html}{wt_html}{oven_html}</div>
</section>''')

# 11. Conclusion
conc = book['conclusion']
toc_entries.append(('conclusion', 'Conclusion — ' + conc['subtitle'], 1))
conc_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in conc['paragraphs'])
sections.append(f'''<section class="chapter-section conclusion-section" epub:type="chapter" id="conclusion">
  <p class="chapter-eyebrow">Conclusion</p>
  <h1 class="chapter-title">{esc(conc['subtitle'])}</h1>
  <hr class="chapter-rule">
  <div class="prose">{conc_paras}</div>
</section>''')


# ─── Build TOC nav ─────────────────────────────────────────────────────────────
toc_items = ''
for entry_id, label, level in toc_entries:
    css_class = 'toc-chapter' if level == 1 else 'toc-sub'
    toc_items += f'<li class="{css_class}"><a href="#{esc(entry_id)}">{esc(label)}</a></li>\n'

toc_nav = f'''<nav epub:type="toc" id="toc">
  <h2>Table of Contents</h2>
  <ol>
{toc_items}  </ol>
</nav>'''

# Replace placeholder
body_html = '\n'.join(s if s != TOC_PLACEHOLDER else toc_nav for s in sections)

BROWSER_TOOLBAR = '''<div class="toolbar" id="kindle-toolbar" data-preview-only>
  <a class="toolbar-link" href="High_Protein_Meal_Prep_Cookbook.html">Paperback</a>
  <button id="btnPreview" onclick="document.body.classList.toggle('kindle-device');this.textContent=document.body.classList.contains('kindle-device')?'Exit Preview':'Kindle Preview'">Kindle Preview</button>
</div>
<div class="kindle-frame" id="kindleFrame" data-preview-only>
  <div class="kindle-screen" id="kindleScreen"></div>
  <button class="kindle-nav kindle-prev" onclick="kindleNav(-1)">‹</button>
  <button class="kindle-nav kindle-next" onclick="kindleNav(1)">›</button>
</div>
<script data-preview-only>
(function(){
  var pages=[], cur=0;
  function buildPages(){
    pages=[];
    var sects=document.querySelectorAll('.chapter-section,.title-page,.copyright-page,nav#toc');
    sects.forEach(function(s){pages.push(s);});
    showPage(0);
  }
  function showPage(i){
    cur=Math.max(0,Math.min(i,pages.length-1));
    var scr=document.getElementById('kindleScreen');
    if(!scr)return;
    scr.innerHTML='';
    var cl=pages[cur].cloneNode(true);
    cl.style.pageBreakBefore='auto';
    scr.appendChild(cl);
  }
  window.kindleNav=function(d){showPage(cur+d);};

  /* Download a clean version: strip all preview-only elements and toolbar CSS */
  window.downloadClean=function(){
    var clone=document.documentElement.cloneNode(true);
    /* Remove all elements marked data-preview-only */
    clone.querySelectorAll('[data-preview-only]').forEach(function(el){el.remove();});
    /* Remove the toolbar CSS block from <style> */
    clone.querySelectorAll('style').forEach(function(st){
      st.textContent=st.textContent.replace(/\\/\\*\\s*===\\s*Toolbar[\\s\\S]*$/, '');
    });
    /* Remove kindle-device class if active */
    clone.querySelector('body').classList.remove('kindle-device');
    var html='<?xml version="1.0" encoding="UTF-8"?>\\n<!DOCTYPE html>\\n'+clone.outerHTML;
    var blob=new Blob([html],{type:'text/html;charset=utf-8'});
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='High_Protein_Meal_Prep_Cookbook_Kindle.html';
    a.click();
    URL.revokeObjectURL(a.href);
  };

  document.addEventListener('DOMContentLoaded',buildPages);
})();
</script>'''

BROWSER_TOOLBAR_CSS = '''
/* === Toolbar (preview-only — stripped on download) === */
.toolbar {
  position: fixed; top: 14px; right: 14px; z-index: 1000;
  display: flex; gap: 8px;
  font-family: Arial, 'Helvetica Neue', sans-serif;
}
.toolbar-link, .toolbar button {
  display: inline-flex; align-items: center;
  border: 1px solid #e0d5b0; background: #fff; color: #1a1a1a;
  padding: 8px 14px; border-radius: 6px;
  font-size: 10pt; font-weight: 600;
  text-decoration: none; cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.15s, background 0.15s;
}
.toolbar-link:hover, .toolbar button:hover {
  transform: translateY(-1px);
}
@media print {
  .toolbar { display: none !important; }
  .kindle-frame { display: none !important; }
}

/* === Kindle Device Preview === */
.kindle-frame {
  display: none;
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  z-index: 900;
  justify-content: center; align-items: center;
}
body.kindle-device .kindle-frame { display: flex; }
body.kindle-device > *:not(.kindle-frame):not(.toolbar):not(script) { display: none; }
.kindle-screen {
  width: 600px; max-height: 800px; overflow-y: auto;
  background: #fff; border-radius: 4px;
  padding: 2em 1.5em;
  box-shadow: 0 0 0 18px #222, 0 0 0 22px #111, 0 20px 60px rgba(0,0,0,0.5);
  font-family: Georgia, serif; font-size: 0.95em; line-height: 1.6;
}
.kindle-nav {
  position: fixed; top: 50%; transform: translateY(-50%);
  width: 54px; height: 54px; border-radius: 50%;
  background: rgba(255,255,255,0.15); border: none;
  color: #fff; font-size: 28px; cursor: pointer;
  transition: background 0.2s;
  z-index: 950;
}
.kindle-nav:hover { background: rgba(255,255,255,0.3); }
.kindle-prev { left: 20px; }
.kindle-next { right: 20px; }
'''

# ─── Final HTML ────────────────────────────────────────────────────────────────
html_out = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{esc(book['title'])}</title>
<style>
{css}
{BROWSER_TOOLBAR_CSS}
</style>
</head>
<body>
{BROWSER_TOOLBAR}
{body_html}
</body>
</html>'''

# Images remain as external links to keep HTML light; use create_kindle_zip.py for submission.

# ─── Strip emoji (KDP rejects them — triggers LucidaGrande-Bold error) ─────────
EMOJI_MAP = {
    '🥚': '', '🐔': '', '🐟': '', '🐄': '', '🫘': '', '🧀': '', '🐖': '',
    '✅': '[OK]', '❌': '[X]', '⏱️': '', '⏱': '', '💪': '',
    '✓': '*',  '✕': 'x',
    '📖': '', '📱': '', '⬇': '',
}
for emoji, replacement in EMOJI_MAP.items():
    html_out = html_out.replace(emoji, replacement)
# Catch any remaining emoji
html_out = re.sub(r'[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u27BF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]', '', html_out)
print('Emoji stripped')

out = ROOT_DIR / 'High_Protein_Meal_Prep_Cookbook_Kindle.html'
out.write_text(html_out, encoding='utf-8')
print('Wrote', out)
print(f'Size: {len(html_out)/1e6:.1f} MB')
print('TOC entries:', len(toc_entries))
print('Recipes:', len(book['recipes']))
