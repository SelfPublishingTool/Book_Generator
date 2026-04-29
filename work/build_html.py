#!/usr/bin/env python3
"""Build the full HTML cookbook from parsed JSON — v3:
- 2 columns recipes (cards side-by-side)
- SVG illustrations per protein source
- Single Copyright page (text at body size)
- Theme color #fdc705 (golden yellow)
- Convert-to-PDF button (window.print() with @page portrait)
- Live auto-fit JS to prevent overflow / cut-off
- No hardcoded inner heights"""
import json, html, re, time
from pathlib import Path

# Use absolute paths relative to the script's directory
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

# ---------------- SVG illustrations per protein source ----------------
SVG_ILLUSTRATIONS = {
    'eggs': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgE" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff7d6"/><stop offset="1" stop-color="#fde08a"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgE)"/><g transform="translate(48 32)"><ellipse cx="0" cy="40" rx="32" ry="40" fill="#ffffff" stroke="#bfa54a" stroke-width="1.5"/><circle cx="-2" cy="36" r="14" fill="#fdc705"/><circle cx="-4" cy="34" r="5" fill="#ffe27a" opacity="0.85"/></g><g transform="translate(120 50)"><ellipse cx="0" cy="32" rx="28" ry="34" fill="#ffffff" stroke="#bfa54a" stroke-width="1.5"/><circle cx="0" cy="30" r="11" fill="#fdc705"/></g><g transform="translate(178 28)" opacity="0.9"><ellipse cx="0" cy="34" rx="22" ry="28" fill="#ffffff" stroke="#bfa54a" stroke-width="1.5"/><circle cx="0" cy="30" r="9" fill="#fdc705"/></g><g stroke="#a48126" stroke-width="0.8" fill="none" opacity="0.4"><path d="M10 95 q 100 -10 200 0"/></g></svg>''',

    'chicken': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgC" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff0c2"/><stop offset="1" stop-color="#f0c46c"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgC)"/><g transform="translate(110 65)"><ellipse cx="0" cy="0" rx="80" ry="22" fill="#3a2a1a" opacity="0.18"/><path d="M -55 0 q -10 -34 28 -38 q 18 -2 25 6 q 12 -18 32 -10 q 22 8 18 28 q 14 8 14 18 q 0 12 -22 14 q -45 4 -85 -2 q -18 -4 -10 -16z" fill="#c97a3a"/><path d="M -55 0 q -10 -34 28 -38 q 18 -2 25 6 q 12 -18 32 -10 q 22 8 18 28 q 14 8 14 18 q 0 12 -22 14 q -45 4 -85 -2 q -18 -4 -10 -16z" fill="none" stroke="#7a4a1d" stroke-width="1.2"/><path d="M -32 -10 q 8 -8 22 -6 M 6 -16 q 6 -6 18 -2 M -10 4 q 6 -2 14 0" stroke="#7a4a1d" stroke-width="1" fill="none" opacity="0.5"/><circle cx="-25" cy="-12" r="2" fill="#7a4a1d" opacity="0.5"/><circle cx="6" cy="-8" r="2" fill="#7a4a1d" opacity="0.5"/></g><g stroke="#a07a3e" stroke-width="0.8" fill="none" opacity="0.45"><path d="M 8 22 q 12 -6 22 0 M 184 22 q 12 -6 22 0"/></g></svg>''',

    'fish': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgF" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#ffe9a3"/><stop offset="1" stop-color="#f0bc4d"/></linearGradient><linearGradient id="salmon" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#ff9c7a"/><stop offset="1" stop-color="#e36a48"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgF)"/><g transform="translate(112 60)"><ellipse cx="0" cy="3" rx="80" ry="14" fill="#3a2810" opacity="0.18"/><path d="M -78 0 q 10 -32 60 -32 q 50 0 70 12 l 18 -8 q 8 -2 8 6 v 22 q 0 8 -8 6 l -18 -8 q -20 12 -70 12 q -50 0 -60 -32 z" fill="url(#salmon)" stroke="#a3432a" stroke-width="1.2"/><path d="M -60 -8 q 10 4 24 0 M -50 8 q 10 -4 24 0 M -30 -10 q 10 4 24 0 M -20 8 q 10 -4 24 0 M 0 -10 q 10 4 24 0 M 10 8 q 10 -4 24 0" stroke="#fff" stroke-width="1.2" fill="none" opacity="0.7"/><circle cx="-58" cy="-8" r="3" fill="#3a2810"/></g><g stroke="#a07a3e" stroke-width="0.8" fill="none" opacity="0.4"><path d="M 0 95 q 110 -10 220 0"/><path d="M 12 100 q 100 -8 198 0"/></g></svg>''',

    'beef': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgB" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#ffe19a"/><stop offset="1" stop-color="#e3a854"/></linearGradient><linearGradient id="meat" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#a93e2e"/><stop offset="1" stop-color="#6f1f15"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgB)"/><g transform="translate(110 60)"><ellipse cx="0" cy="3" rx="80" ry="16" fill="#3a1a0e" opacity="0.18"/><path d="M -70 -22 q -10 -10 0 -18 q 18 -10 50 -8 q 40 0 60 8 q 18 6 18 22 q 8 4 8 16 q 0 14 -16 16 q -30 6 -70 6 q -36 -2 -54 -6 q -14 -4 -10 -18 q -8 -8 -2 -16 q 4 -4 16 -2 z" fill="url(#meat)" stroke="#4a1610" stroke-width="1.2"/><path d="M -50 -16 q 12 -2 24 4 M -16 -20 q 16 -2 24 0 M 18 -14 q 14 0 22 6 M -40 0 q 16 -2 22 4 M -8 -2 q 14 -2 22 4" stroke="#fff" stroke-width="1.4" fill="none" opacity="0.55"/><ellipse cx="-46" cy="-12" rx="10" ry="6" fill="#fff" opacity="0.18"/><ellipse cx="20" cy="-8" rx="14" ry="6" fill="#fff" opacity="0.18"/></g></svg>''',

    'legumes': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgL" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#ffeeb6"/><stop offset="1" stop-color="#dba840"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgL)"/><g transform="translate(0 50)"><g fill="#5b3a18"><ellipse cx="36" cy="22" rx="11" ry="8"/><ellipse cx="60" cy="14" rx="10" ry="7"/><ellipse cx="84" cy="22" rx="11" ry="8"/></g><g fill="#a4541f"><ellipse cx="48" cy="34" rx="10" ry="7"/><ellipse cx="72" cy="36" rx="10" ry="7"/><ellipse cx="92" cy="38" rx="11" ry="8"/></g><g fill="#fdc705"><ellipse cx="108" cy="20" rx="10" ry="7"/><ellipse cx="130" cy="14" rx="9" ry="6"/><ellipse cx="120" cy="36" rx="10" ry="7"/></g><g fill="#7a5710"><ellipse cx="146" cy="22" rx="10" ry="7"/><ellipse cx="168" cy="14" rx="9" ry="6"/><ellipse cx="158" cy="36" rx="10" ry="7"/><ellipse cx="184" cy="38" rx="9" ry="6"/></g><g fill="#3c2810"><ellipse cx="20" cy="38" rx="10" ry="7"/><ellipse cx="200" cy="22" rx="10" ry="7"/></g><g fill="#fff" opacity="0.35"><circle cx="34" cy="20" r="2"/><circle cx="58" cy="12" r="2"/><circle cx="106" cy="18" r="2"/><circle cx="144" cy="20" r="2"/><circle cx="166" cy="12" r="2"/></g></g></svg>''',

    'dairy': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgD" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff8de"/><stop offset="1" stop-color="#f5d77a"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgD)"/><g transform="translate(60 28)"><path d="M 0 0 h 50 v 6 q 0 6 -6 6 h -38 q -6 0 -6 -6 z" fill="#fdc705" stroke="#a08220" stroke-width="1"/><rect x="6" y="12" width="38" height="46" rx="3" fill="#ffffff" stroke="#bfa54a" stroke-width="1"/><circle cx="14" cy="28" r="3" fill="#fde08a"/><circle cx="32" cy="36" r="4" fill="#fde08a"/><circle cx="20" cy="46" r="2.5" fill="#fde08a"/><circle cx="36" cy="50" r="2" fill="#fde08a"/></g><g transform="translate(135 40)"><ellipse cx="0" cy="38" rx="40" ry="6" fill="#1f2418" opacity="0.12"/><rect x="-30" y="-2" width="60" height="40" rx="6" fill="#fafafa" stroke="#bfa54a" stroke-width="1.2"/><rect x="-30" y="-2" width="60" height="14" rx="6" fill="#fdc705"/><circle cx="-12" cy="22" r="3" fill="#fde08a"/><circle cx="6" cy="26" r="2.5" fill="#fde08a"/><circle cx="14" cy="20" r="2" fill="#fde08a"/></g></svg>''',

    'mixed': '''<svg viewBox="0 0 220 110" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="bgM" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff3c5"/><stop offset="1" stop-color="#e9b94a"/></linearGradient></defs><rect width="220" height="110" fill="url(#bgM)"/><g transform="translate(110 60)"><circle cx="0" cy="0" r="46" fill="#fffaee" stroke="#a8821c" stroke-width="1.5"/><circle cx="0" cy="0" r="36" fill="#fffdf3" stroke="#a8821c" stroke-width="0.8"/><path d="M -28 -8 q 0 -16 14 -18 q 14 0 18 12 q -2 14 -16 16 q -14 0 -16 -10 z" fill="#7d5530"/><circle cx="-22" cy="-10" r="2.5" fill="#fff" opacity="0.5"/><g fill="#a07c2e"><ellipse cx="14" cy="-14" rx="8" ry="5" transform="rotate(-20 14 -14)"/><ellipse cx="22" cy="-6" rx="7" ry="4" transform="rotate(15 22 -6)"/></g><g fill="#cf5732"><ellipse cx="6" cy="14" rx="6" ry="4"/><ellipse cx="-12" cy="18" rx="6" ry="4"/><ellipse cx="20" cy="14" rx="5" ry="3.5"/></g><g fill="#fdc705"><circle cx="-2" cy="24" r="3"/><circle cx="14" cy="22" r="2.5"/></g></g><g stroke="#a07c2e" stroke-width="0.8" fill="none" opacity="0.4"><path d="M 4 96 q 110 -10 212 0"/></g></svg>''',
}

PROTEIN_KEYWORDS = [
    ('eggs', ['egg', 'eggs']),
    ('chicken', ['chicken', 'poultry', 'turkey', 'pork']),
    ('fish', ['fish', 'salmon', 'tuna', 'shrimp', 'cod']),
    ('beef', ['beef']),
    ('legumes', ['legume', 'legumes']),
    ('dairy', ['dairy', 'cheese', 'yogurt']),
]

def pick_illustration(protein_source_text):
    s = (protein_source_text or '').lower()
    matches = []
    for key, kws in PROTEIN_KEYWORDS:
        for kw in kws:
            pos = s.find(kw)
            if pos >= 0:
                matches.append((pos, key))
                break
    if matches:
        matches.sort()
        return SVG_ILLUSTRATIONS[matches[0][1]]
    return SVG_ILLUSTRATIONS['mixed']

# ---------------- Helpers ----------------
def chapter_cover(num_label, ch_title, ch_sub, ch_quote, recipe_count=None, color_class='cover-night'):
    extra = f'<p class="chapter-cover-count">{recipe_count} recipes</p>' if recipe_count else ''
    return f'''<div class="page chapter-cover {color_class}">
  <div class="page-content">
    <div class="chapter-cover-inner">
      <p class="chapter-cover-eyebrow">{esc(num_label)}</p>
      <h1 class="chapter-cover-title">{esc(ch_title)}</h1>
      <div class="chapter-cover-divider"></div>
      <p class="chapter-cover-subtitle">{esc(ch_sub)}</p>
      {extra}
    </div>
  </div>
</div>'''

def render_recipe(r):
    ps = r.get('protein_source','')
    m = re.match(r'^([\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF☀-➿]+\s*\+?\s*[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF☀-➿]*)\s*(.+)$', ps)
    if m:
        ps_emoji = m.group(1).strip()
        ps_text = m.group(2).strip()
    else:
        ps_emoji = ''
        ps_text = ps
    nut = r.get('nutrition','')
    pg_match = re.search(r'Protein:\s*(\d+)g', nut)
    protein_g = pg_match.group(1) + 'g' if pg_match else ''
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
    nut_extra = r.get('nutrition_extra','')
    stats_html = ''.join(f'<div class="nut-stat"><span class="nut-val">{esc(v)}</span><span class="nut-lbl">{esc(l)}</span></div>' for l,v in stats)
    ing_items = ''.join(f'<li>{smart_html(i)}</li>' for i in r['ingredients'])
    inst_items = ''.join(f'<li>{smart_html(i)}</li>' for i in r['instructions'])
    storage = r.get('storage')
    storage_html = f'<div class="recipe-storage"><span class="storage-label">Storage</span><span class="storage-text">{smart_html(storage)}</span></div>' if storage else ''
    cook_label = r.get('cook_label', 'Cook')
    
    # Image logic: Use image_path if it exists, else fallback to SVG
    img_path = r.get('image_path')
    if img_path:
        illustration = f'<img src="{esc(img_path)}?v={int(time.time())}" class="recipe-img" alt="{esc(r["title"])}">'
    else:
        illustration = pick_illustration(ps)

    return f'''<article class="recipe-card" data-recipe="{r['number']}">
  <div class="recipe-illustration">
    {illustration}
    <div class="recipe-num-badge">{r['number']:02d}</div>
    {f'<div class="recipe-protein-badge">{esc(protein_g)} protein</div>' if protein_g else ''}
  </div>
  <header class="recipe-header">
    <h3 class="recipe-title">{esc(r['title'])}</h3>
    <div class="recipe-meta">
      <span class="badge badge-protein-src">{esc(ps_emoji)} {esc(ps_text)}</span>
      <span class="badge badge-yield">Yield · {esc(r['yield'])}</span>
      <span class="badge badge-prep">Prep · {esc(r['prep'])}</span>
      <span class="badge badge-cook">{esc(cook_label)} · {esc(r['cook'])}</span>
    </div>
  </header>
  <div class="recipe-body">
    <section class="recipe-ingredients">
      <h4 class="section-h">Ingredients</h4>
      <ul class="ingredients-list">{ing_items}</ul>
    </section>
    <section class="recipe-instructions">
      <h4 class="section-h">Instructions</h4>
      <ol class="instructions-list">{inst_items}</ol>
    </section>
  </div>
  <footer class="recipe-footer">
    <div class="nutrition-box">
      <div class="nut-head">
        <span class="nut-title">Nutrition</span>
        {f'<span class="nut-extra">{esc(nut_extra)}</span>' if nut_extra else ''}
      </div>
      <div class="nut-stats">{stats_html}</div>
    </div>
    {storage_html}
  </footer>
</article>'''

def chunk_pairs(seq, size=2):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

# ---------------- Build HTML body ----------------
parts = []

# 1. Title page
parts.append(f'''<div class="page title-page" data-no-toc="true">
  <div class="page-content">
    <div class="title-page-inner">
      <p class="tp-eyebrow">Priscilla Quinn</p>
      <div class="tp-divider"></div>
      <h1 class="tp-title">{esc(book['title'])}</h1>
      <p class="tp-subtitle">{esc(book['subtitle'])}</p>
      <div class="tp-icon-row">
        <span class="tp-icon">🥚</span><span class="tp-icon">🐔</span><span class="tp-icon">🐟</span><span class="tp-icon">🐄</span><span class="tp-icon">🫘</span><span class="tp-icon">🧀</span>
      </div>
      <p class="tp-author">By <strong>{esc(book['author'].replace('By ',''))}</strong></p>
    </div>
  </div>
</div>''')

# 2. Copyright page (single heading, body-size text)
discl_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in book['disclaimer'])
parts.append(f'''<div class="page legal-page" data-no-toc="true">
  <div class="page-content">
    <div class="legal-inner">
      <h2 class="legal-h">Copyright</h2>
      <p>{smart_html(book['copyright'])}</p>
      {discl_paras}
    </div>
  </div>
</div>''')

parts.append('''<div class="page toc-page" data-no-toc="true">
  <div class="page-content">
    <header class="toc-header">
      <p class="toc-eyebrow">Cookbook</p>
      <h2 class="toc-title">Table of Contents</h2>
      <div class="toc-rule"></div>
    </header>
    <nav id="toc-nav" class="toc-list"></nav>
  </div>
</div>''')

# 4. Introduction
intro = book['introduction']
# Force page break before any short "label:" paragraph (sub-section heading
# that introduces a list of items) so labels stay with their content.
intro_pages = []
buf = ''
def _is_label(p):
    return len(p) < 80 and p.rstrip().endswith(':')
for i, p in enumerate(intro['paragraphs']):
    add = f'<p>{smart_html(p)}</p>'
    next_is_label = (i + 1 < len(intro['paragraphs']) and _is_label(intro['paragraphs'][i+1]))
    # Split around 3200 characters to keep pages balanced
    if (len(buf) > 3200 and (next_is_label or _is_label(p))) and buf:
        intro_pages.append(buf); buf = add
    else:
        buf += add
if buf: intro_pages.append(buf)

parts.append(f'''<div class="page intro-page">
  <div class="page-content">
    <header class="chapter-head">
      <p class="chapter-eyebrow">Introduction</p>
      <h1 class="chapter-h1">{esc(intro['subtitle'])}</h1>
      <div class="chapter-rule"></div>
    </header>
    <div class="prose">{intro_pages[0]}</div>
  </div>
</div>''')
for extra in intro_pages[1:]:
    parts.append(f'''<div class="page intro-page-cont">
  <div class="page-content">
    <div class="prose">{extra}</div>
  </div>
</div>''')

# 5. Chapter 1
ch1 = book['chapter1']
parts.append(chapter_cover('Chapter 1', ch1['subtitle'], 'The Foundation', '', color_class='cover-night'))

def render_ch1_body_lines(body_lines):
    out = []
    i = 0
    while i < len(body_lines):
        l = body_lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(body_lines) and body_lines[i].strip().startswith('|'):
                rl = body_lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|$', rl):
                    cells = [c.strip() for c in rl.split('|')[1:-1]]
                    if any(c for c in cells):
                        rows.append(cells)
                i += 1
            if rows:
                head = rows[0]; body = rows[1:]
                thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
                tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

ch1_blocks = []
for sec in ch1['sections']:
    body_html = render_ch1_body_lines(sec['body'])
    ch1_blocks.append(f'<section class="prep-section"><h2 class="prep-h2">{esc(sec["heading"])}</h2><div class="prose">{body_html}</div></section>')

ch1_pages = [[0], [1], [2, 3], [4, 5]]
for plist in ch1_pages:
    content = ''.join(ch1_blocks[i] for i in plist)
    parts.append(f'<div class="page ch1-page"><div class="page-content"><div class="page-frame">{content}</div></div></div>')

# 6. Chapters 2-8 with 2-column recipe pages
chapter_recipe_groups = {}
for r in book['recipes']:
    chapter_recipe_groups.setdefault(r['chapter'], []).append(r)
chapter_meta_lookup = {c['title']: c for c in book['chapters_meta']}

ch_covers = {
    'Chapter 2': 'cover-charcoal',
    'Chapter 3': 'cover-coffee',
    'Chapter 4': 'cover-night',
    'Chapter 5': 'cover-olive',
    'Chapter 6': 'cover-rust',
    'Chapter 7': 'cover-burgundy',
    'Chapter 8': 'cover-ink',
}

for ch_title in ['Chapter 2','Chapter 3','Chapter 4','Chapter 5','Chapter 6','Chapter 7','Chapter 8']:
    meta = chapter_meta_lookup[ch_title]
    rs = chapter_recipe_groups[ch_title]
    parts.append(chapter_cover(ch_title, meta['subtitle'], meta['quote'], '', recipe_count=len(rs), color_class=ch_covers[ch_title]))
    for pair in chunk_pairs(rs, 2):
        cards = ''.join(render_recipe(r) for r in pair)
        cls = 'recipe-page-pair' if len(pair) == 2 else 'recipe-page-single'
        parts.append(f'<div class="page recipe-page {cls}" data-chapter="{esc(ch_title)}"><div class="page-content"><div class="recipe-grid">{cards}</div></div></div>')

# 7. Meal Plan
mp = book['mealplan']
parts.append(chapter_cover('Chapter 9', mp['subtitle'], mp['quote'], '', color_class='cover-coffee'))

intro_html = ''.join(f'<p>{smart_html(p)}</p>' for p in mp['intro_paragraphs'])
htr_html = ''.join(f'<li>{smart_html(p)}</li>' for p in mp['how_to_read'])
parts.append(f'''<div class="page mealplan-intro">
  <div class="page-content">
    <header class="chapter-head">
      <h2 class="chapter-h1">{esc(mp['subtitle'])}</h2>
      <p class="chapter-h2">{esc(mp['quote'])}</p>
      <div class="chapter-rule"></div>
    </header>
    <div class="prose">{intro_html}</div>
    <h3 class="prose-h3">How to Read the Plan</h3>
    <ul class="checklist">{htr_html}</ul>
  </div>
</div>''')

def render_week_body(body_lines):
    out = []
    i = 0
    while i < len(body_lines):
        l = body_lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.endswith(':') and not l.startswith('|') and not l.startswith(' '):
            out.append(f'<h4 class="week-h">{esc(l[:-1])}</h4>')
            i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(body_lines) and body_lines[i].strip().startswith('|'):
                rl = body_lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|$', rl):
                    cells = [c.strip() for c in rl.split('|')[1:-1]]
                    if any(c for c in cells):
                        rows.append(cells)
                i += 1
            if rows:
                head = rows[0]; body = rows[1:]
                thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
                tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data-table compact"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            if l.startswith('Objective:'):
                out.append(f'<p class="week-objective">{smart_html(l)}</p>')
            elif l.startswith('Swap It this week:') or l.startswith('Beyond Week'):
                out.append(f'<p class="week-callout">{smart_html(l)}</p>')
            else:
                out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

for w in mp['weeks']:
    body_html = render_week_body(w['body_lines'])
    parts.append(f'''<div class="page week-page">
  <div class="page-content">
    <header class="week-header">
      <h2 class="week-title">{esc(w['title'])}</h2>
      <div class="week-rule"></div>
    </header>
    <div class="prose week-body">{body_html}</div>
  </div>
</div>''')

# 8. Bonus Toolkit
parts.append(chapter_cover('Chapter 10', 'Your Bonus Toolkit', 'Beyond the recipes', '', color_class='cover-burgundy'))

def render_bonus_body(body_lines):
    out = []
    i = 0
    while i < len(body_lines):
        l = body_lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.startswith('### '):
            out.append(f'<h3 class="bonus-h3">{esc(l[4:].strip())}</h3>')
            i += 1; continue
        if l == l.upper() and len(l) > 3 and re.match(r'^[A-Z &]+$', l):
            out.append(f'<h4 class="bonus-h4">{esc(l)}</h4>')
            i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(body_lines) and body_lines[i].strip().startswith('|'):
                rl = body_lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|$', rl):
                    cells = [c.strip() for c in rl.split('|')[1:-1]]
                    if any(c for c in cells):
                        rows.append(cells)
                i += 1
            if rows:
                head = rows[0]; body = rows[1:]
                thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
                tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            if re.match(r'^\d+[–\-]\d+ points', l):
                out.append(f'<p class="score-bucket">{smart_html(l)}</p>')
            elif l.endswith(':') and len(l) < 60 and not any(l.startswith(x) for x in ['✅','❌','Session','⏱️']):
                out.append(f'<h4 class="bonus-q">{esc(l[:-1])}</h4>')
            elif any(l.startswith(x) for x in ['✅','❌','Protein hack','Pro Tip','Session','Session A','Session B','BEGINNER','INTERMEDIATE','ADVANCED']):
                cls = 'hack'
                if l.startswith('✅'): cls = 'pos'
                elif l.startswith('❌'): cls = 'neg'
                elif 'Session' in l: cls = 'session'
                elif any(x in l for x in ['BEGINNER','INTERMEDIATE','ADVANCED']): cls = 'level'
                
                # Add icons for workout
                display_l = l
                if 'Session' in l and not l.startswith('⏱️'): display_l = '⏱️ ' + l
                elif any(x in l for x in ['BEGINNER','INTERMEDIATE','ADVANCED']) and not l.startswith('💪'): display_l = '💪 ' + l
                
                out.append(f'<p class="hint hint-{cls}">{smart_html(display_l)}</p>')
            elif re.match(r'^[A-Z][^.]*$', l) and len(l) < 30 and i+1 < len(body_lines) and body_lines[i+1].strip().startswith('✅'):
                out.append(f'<h5 class="restaurant-name">{esc(l)}</h5>')
            else:
                out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

for b in book['bonus']['bonuses']:
    title = b['title']
    body_html = render_bonus_body(b['body_lines'])
    elems = re.findall(r'<(?:h\d|p|table|ul|ol)[^>]*>.*?</(?:h\d|p|table|ul|ol)>', body_html, re.DOTALL)
    if not elems: elems = [body_html]
    chunks = []; cur = ''
    for el in elems:
        if len(cur) + len(el) > 1800 and cur:
            chunks.append(cur); cur = el
        else:
            cur += el
    if cur: chunks.append(cur)
    parts.append(f'''<div class="page bonus-page">
  <div class="page-content">
    <header class="bonus-header">
      <p class="bonus-eyebrow">Bonus Toolkit</p>
      <h2 class="bonus-h2">{esc(title)}</h2>
      <div class="bonus-rule"></div>
    </header>
    <div class="prose bonus-body">{chunks[0]}</div>
  </div>
</div>''')
    for ch in chunks[1:]:
        parts.append(f'<div class="page bonus-page-cont"><div class="page-content"><div class="prose bonus-body">{ch}</div></div></div>')

# 9. Appendix A
appA = book['appendix_a']
parts.append(chapter_cover('Appendix A', appA['sub'], 'All 101 recipes', '', color_class='cover-ink'))

rows = appA['rows']
header = rows[0]; body_rows = rows[1:]

def render_app_table(header, rows):
    thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in header) + '</tr>'
    tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="data-table app-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>'

chunks_a = [body_rows[i:i+30] for i in range(0, len(body_rows), 30)]
for k, c in enumerate(chunks_a):
    title_html = ''
    if k == 0:
        title_html = f'''<header class="chapter-head">
  <p class="chapter-eyebrow">Appendix A</p>
  <h2 class="chapter-h1">{esc(appA['sub'])}</h2>
  <div class="chapter-rule"></div>
</header>
<p class="prose"><em>{smart_html(appA['intro'])}</em></p>'''
    table_html = render_app_table(header, c)
    parts.append(f'<div class="page appendix-page"><div class="page-content">{title_html}{table_html}</div></div>')

# 10. Appendix B
appB = book['appendix_b']
parts.append(chapter_cover('Appendix B', appB['sub'], 'Reference for everyday cooking', '', color_class='cover-olive'))

foods_header = appB['foods'][0]; foods_body = appB['foods'][1:]
food_chunks = [foods_body[i:i+32] for i in range(0, len(foods_body), 32)]
for k, c in enumerate(food_chunks):
    title_html = ''
    if k == 0:
        title_html = f'''<header class="chapter-head">
  <p class="chapter-eyebrow">Appendix B</p>
  <h2 class="chapter-h1">Protein Content of 50 Common Foods</h2>
  <div class="chapter-rule"></div>
</header>'''
    table_html = render_app_table(foods_header, c)
    parts.append(f'<div class="page appendix-page"><div class="page-content">{title_html}{table_html}</div></div>')

def render_conv_table(label, rows):
    head = rows[0]; body = rows[1:]
    thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
    tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
    return f'<div class="conv-card"><h3 class="conv-h">{esc(label)}</h3><table class="data-table conv-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>'

vol_html = render_conv_table('Volume', appB['volume'])
wt_html = render_conv_table('Weight', appB['weight'])
oven_html = render_conv_table('Oven Temperature', appB['oven'])
parts.append(f'''<div class="page appendix-page conv-page">
  <div class="page-content">
    <header class="chapter-head">
      <p class="chapter-eyebrow">Appendix B</p>
      <h2 class="chapter-h1">Measurement Conversion Charts</h2>
      <div class="chapter-rule"></div>
    </header>
    <div class="conv-grid">{vol_html}{wt_html}{oven_html}</div>
  </div>
</div>''')

# 11. Conclusion
conc = book['conclusion']
conc_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in conc['paragraphs'])
parts.append(f'''<div class="page conclusion-page">
  <div class="page-content">
    <header class="chapter-head">
      <p class="chapter-eyebrow">Conclusion</p>
      <h1 class="chapter-h1">{esc(conc['subtitle'])}</h1>
      <div class="chapter-rule"></div>
    </header>
    <div class="prose">{conc_paras}</div>
  </div>
</div>''')

# 12. Review section
review = book['review_section']
rev_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in review['paragraphs'])
parts.append(f'''<div class="page review-page">
  <div class="page-content">
    <header class="chapter-head">
      <h2 class="chapter-h1">{esc(review['title'])}</h2>
      <div class="chapter-rule"></div>
    </header>
    <div class="prose">{rev_paras}</div>
    <div class="end-mark">— End —</div>
  </div>
</div>''')

body_html = '\n'.join(parts)

# ----------- CSS -----------
css = r'''
:root{
  --primary:#fdc705;
  --primary-dark:#c69c00;
  --primary-light:#fde58c;
  --primary-soft:#fff5ce;
  --primary-bg:#fffaeb;
  --ink:#1d1812;
  --ink-soft:#3a3325;
  --muted:#7a6c52;
  --line:#e7dfc4;
  --paper:#ffffff;
  --paper-2:#ffffff;
  --cream:#f7eecf;
  --cream-2:#fcf6e0;
  --beige:#efe6cc;
  --rose:#b85f5f;
  --night:#1a1a1a;
  --coffee:#3a2a1a;
  --olive:#3d3a1a;
  --rust:#5b3214;
  --burgundy:#4a1c1c;
  --ink-deep:#0e1010;
  --shadow:0 0.5px 0 rgba(0,0,0,0.04), 0 6px 18px rgba(40,30,10,0.08);
}

*{box-sizing:border-box;}
html,body{
  margin:0;padding:0;
  background:#e7e0c8;
  color:var(--ink);
  font-family:'Source Serif Pro','Cormorant Garamond','Georgia','Times New Roman',serif;
  line-height:1.45;
  -webkit-print-color-adjust:exact;
  print-color-adjust:exact;
}
.book{
  display:flex;flex-direction:column;align-items:center;
  padding:24px 0 80px;gap:18px;
}

/* PAGE — fixed 8.5x11 portrait, no inner hardcoded heights */
.page{
  width:8.5in;
  height:11in;
  min-height:11in;
  max-height:11in;
  background:var(--paper);
  position:relative;
  overflow:hidden;
  page-break-after:always;
  break-after:page;
  box-shadow:var(--shadow);
  display: block;
}
.page.title-page,
.page.chapter-cover{padding:0;}
/* KDP 8.5×11 paperback margins (revised, more efficient — still KDP-compliant):
   top/left/right 0.5in (above the 0.5in minimum required), bottom 0.75in to
   reserve space for the page number + 5mm safety. Gutter on bound side is also
   0.5in which is KDP-safe up to 300 pages. */
.page{ --bottom-safe: 0.75in; --page-margin: 0.5in; }
.page-content{
  width:100%;
  height:100%;
  padding:var(--page-margin) var(--page-margin) var(--bottom-safe) var(--page-margin);
  display:flex;flex-direction:column;
  /* top center keeps left/right margins symmetric when auto-fit scales the content */
  transform-origin:top center;
}
.page.title-page .page-content,
.page.chapter-cover .page-content{padding:0;}

.page::after{
  content:attr(data-page);
  position:absolute;
  bottom:0.35in;left:50%;transform:translateX(-50%);
  font-family:'Source Sans Pro','Inter','Helvetica Neue',sans-serif;
  font-size:9pt;color:var(--muted);letter-spacing:0.18em;
  z-index:5;
}
.page.title-page::after,
.page.chapter-cover::after,
.page.legal-page::after{content:none;}

/* Overflow flag (preview only) */
.page[data-overflow="true"]::before{
  content:'CONTENT TIGHT';
  position:absolute;top:8px;right:8px;
  background:#ffe3a0;color:#7a4f17;font-size:7pt;font-weight:700;
  padding:2px 6px;border-radius:4px;letter-spacing:0.1em;
  font-family:'Source Sans Pro',sans-serif;z-index:10;
}

/* Title page */
.title-page{
  background:linear-gradient(160deg,#1a1a1a 0%,#0e1010 80%);
  color:#fdc705;
}
.title-page .page-content{align-items:center;justify-content:center;}
.title-page-inner{
  text-align:center;width:78%;
  padding:0.8in;
  border:1px solid rgba(253,199,5,0.35);
  background:rgba(255,255,255,0.02);
  border-radius:6px;
}
.tp-eyebrow{
  text-transform:uppercase;letter-spacing:0.4em;
  font-size:11pt;color:var(--primary);font-weight:600;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  margin:0 0 1em;
}
.tp-divider{width:60px;height:2px;background:var(--primary);margin:0 auto 1.2em;}
.tp-title{
  font-family:'Cormorant Garamond','Playfair Display','Georgia',serif;
  font-size:42pt;line-height:1.05;font-weight:700;
  margin:0 0 0.6em;color:#fff7d6;letter-spacing:-0.01em;
}
.tp-subtitle{font-style:italic;font-size:13pt;line-height:1.45;color:#f0e2a8;margin:0 0 2em;}
.tp-icon-row{font-size:22pt;letter-spacing:0.5em;margin:1.5em 0 2em;}
.tp-author{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:14pt;letter-spacing:0.2em;text-transform:uppercase;
  color:var(--primary);margin:0;
}
.tp-author strong{color:#fff;}

/* Copyright page */
.legal-inner{font-size:11.2pt;line-height:1.5;color:var(--ink);}
.legal-h{
  text-align:center;font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.3em;font-size:11pt;
  color:var(--primary-dark);font-weight:700;margin:0 0 1.4em;
}
.legal-page p{
  margin:0 0 0.7em;
  text-align:justify;
  font-size:11.2pt;
  line-height:1.5;
}
.toc-header{margin-bottom:0.7em;text-align:center;}
.toc-eyebrow{
  text-transform:uppercase;letter-spacing:0.12em;font-size:8pt;
  color:var(--primary-dark);margin-bottom:0.2em;font-weight:700;
}
.toc-title{
  font-family:'Cormorant Garamond',serif;font-size:20pt;margin:0;
  color:var(--ink);font-weight:700;
}
.toc-rule{width:40px;height:2px;background:var(--primary);margin:0.3em auto 0;}
.toc-list{
  display:block !important;
  column-count:1 !important;
  column-gap:0.3in !important;
  margin-top:1em;
}
.toc-list a{
  display:flex;align-items:baseline;gap:0.3em;
  break-inside: avoid;
  margin-bottom: 8px;
  text-decoration:none;color:var(--ink);
  min-width:0;
  padding:0.12em 0;
}
.toc-list .toc-text{
  flex:1 1 auto;
  background-image:linear-gradient(to right,var(--line) 50%,transparent 50%);
  background-size:6px 1px;
  background-position:0 calc(100% - 0.18em);
  background-repeat:repeat-x;
  white-space:normal !important; /* Fix: allow wrap */
  overflow:hidden;
}
.toc-list .toc-text-inner{background:var(--paper);padding-right:0.4em;}
.toc-list .toc-num{
  font-family:'Source Sans Pro',sans-serif;
  font-size:9pt;color:var(--muted);min-width:1.2em;text-align:right;
  background:var(--paper);padding-left:0.3em;
}
.toc-list .toc-h1{font-weight:700;font-size:9pt;margin-top:0.35em;}
.toc-list .toc-h1 .toc-text-inner{color:var(--primary-dark);text-transform:uppercase;letter-spacing:0.02em;}
.toc-list .toc-h2{font-size:8.5pt;padding-left:0.1em;}
.toc-list .toc-h2 .toc-text-inner{font-style:italic;}
.toc-list .toc-h3{font-size:7.5pt;padding-left:0.3em;color:var(--ink-soft);opacity:0.9;}

/* Chapter heads */
.chapter-head{margin:0 0 1.3em;}
.chapter-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.35em;
  color:var(--primary-dark);font-size:10pt;font-weight:600;margin:0 0 0.5em;
}
.chapter-h1{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:26pt;font-weight:700;line-height:1.1;
  margin:0 0 0.5em;color:var(--ink);
}
.chapter-h2{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:14pt;font-style:italic;color:var(--muted);margin:0 0 0.4em;
}
.chapter-rule{width:64px;height:2px;background:var(--primary);margin:0.4em 0 0;}

/* Chapter cover — solid #fdc705 with black text for high contrast */
.chapter-cover{color:var(--ink);background:#fdc705;}
.chapter-cover .page-content{align-items:center;justify-content:center;}
.chapter-cover-inner{
  text-align:center;padding:1in;width:100%;
  border-top:1px solid rgba(0,0,0,0.4);
  border-bottom:1px solid rgba(0,0,0,0.4);
  margin:0.8in 0.8in;
}
.chapter-cover-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.5em;
  font-size:11pt;color:#1a1a1a;font-weight:700;margin:0 0 1em;
}
.chapter-cover-title{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:48pt;font-weight:700;line-height:1.05;
  margin:0 0 0.5em;color:#0e0e0e;letter-spacing:-0.01em;
}
.chapter-cover-divider{width:80px;height:2px;background:#1a1a1a;margin:0.8em auto;}
.chapter-cover-subtitle{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:14pt;font-style:italic;color:#2a2418;margin:0;
}
.chapter-cover-count{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.4em;
  margin:1.4em 0 0;font-size:10pt;color:#1a1a1a;font-weight:700;
}
/* All chapter cover variants share #fdc705 background; class names kept for compatibility */
.chapter-cover.cover-night,
.chapter-cover.cover-charcoal,
.chapter-cover.cover-coffee,
.chapter-cover.cover-olive,
.chapter-cover.cover-rust,
.chapter-cover.cover-burgundy,
.chapter-cover.cover-ink{background:#fdc705;}

/* Prose */
.prose p{margin:0 0 0.6em;text-align:justify;font-size:11.2pt;line-height:1.5;}
.prose p strong{color:var(--primary-dark);}
.prose-h3{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:15pt;color:var(--primary-dark);margin:1em 0 0.4em;font-weight:700;
}

/* Chapter 1 */
.page-frame{display:flex;flex-direction:column;gap:1em;}
.prep-section{padding:0.5em 0;}
.prep-h2{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:16pt;font-weight:700;color:var(--primary-dark);
  margin:0 0 0.5em;border-bottom:1px solid var(--line);padding-bottom:0.3em;
}
.prep-section .prose p{font-size:12pt;line-height:1.5;margin-bottom:0.45em;}

/* Tables */
.data-table{
  width:100%;border-collapse:collapse;font-size:9.5pt;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  margin:0.4em 0 0.8em;
}
.data-table th{
  background:var(--primary);color:var(--ink);text-align:left;
  padding:6px 10px;font-weight:700;letter-spacing:0.04em;
  font-size:9pt;text-transform:uppercase;
}
.data-table td{
  padding:5px 10px;border-bottom:1px solid var(--line);
  vertical-align:top;
}
.data-table tbody tr:nth-child(even) td{background:var(--cream-2);}
.data-table.compact th, .data-table.compact td{padding:3px 7px;font-size:8.5pt;}

/* RECIPE PAGE — 2 columns side by side, same KDP margins as content pages */
.recipe-page .page-content{padding:0.85in var(--page-margin) 0.55in;}
.recipe-page::before{
  content:attr(data-chapter);
  position:absolute;top:0.35in;right:var(--page-margin);
  font-family:'Source Sans Pro',sans-serif;
  font-size:8.5pt;letter-spacing:0.3em;text-transform:uppercase;color:var(--muted);
  z-index:5;
}
.recipe-grid{
  display:grid;
  /* minmax(0, 1fr) prevents card content from making one column wider than the other */
  grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  /* 1fr row fills the entire available vertical space — cards stretch to full height */
  grid-template-rows:1fr;
  gap:0.18in;
  flex:1 1 auto;min-height:0;
  width:100%;
}
.recipe-page-single .recipe-grid{grid-template-columns:minmax(0,1fr);}
.recipe-grid .recipe-card{height:100%;}
.recipe-page-single .recipe-card{max-width:62%;margin:0 auto;}

.recipe-card{
  background:var(--paper-2);
  border:1px solid var(--line);
  border-radius:8px;
  display:flex;flex-direction:column;
  overflow:hidden;
  position:relative;
}
.recipe-card::after{
  content:'';position:absolute;left:0;top:0;bottom:0;width:4px;
  background:linear-gradient(180deg,var(--primary) 0%,var(--primary-dark) 100%);
  z-index:2;
}

/* Illustration banner */
.recipe-illustration{
  position:relative;height:1.9in;flex:0 0 auto;
  border-bottom:1px solid var(--line);
  background:var(--cream);
  overflow:hidden;
}
.recipe-illustration svg, .recipe-img{display:block;width:100%;height:100%;object-fit:cover;}
.recipe-num-badge{
  position:absolute;top:8px;left:8px;
  width:34px;height:34px;background:var(--ink);color:var(--primary);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:13pt;font-weight:700;
  box-shadow:0 2px 6px rgba(0,0,0,0.25), inset 0 0 0 2px rgba(253,199,5,0.4);
}
.recipe-protein-badge{
  position:absolute;top:8px;right:8px;
  background:var(--primary);color:var(--ink);
  font-family:'Source Sans Pro',sans-serif;
  font-size:8pt;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;
  padding:4px 8px;border-radius:12px;
  box-shadow:0 2px 6px rgba(0,0,0,0.18);
}

.recipe-header{
  padding:8px 10px 4px 12px;
  border-bottom:1px solid var(--line);
}
.recipe-title{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:14pt;font-weight:700;color:var(--ink);
  margin:0 0 4px;line-height:1.1;
}
.recipe-meta{display:flex;flex-wrap:wrap;gap:3px;}
.badge{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:6.8pt;font-weight:600;
  padding:2px 6px;border-radius:9px;
  border:1px solid var(--line);background:var(--cream);
  color:var(--ink-soft);letter-spacing:0.02em;text-transform:uppercase;
  white-space:nowrap;
}
.badge-protein-src{background:var(--primary-soft);border-color:var(--primary);color:var(--ink);}
.badge-yield{background:var(--cream);}
.badge-prep{background:#fff0c2;border-color:var(--primary);color:#5a4106;}
.badge-cook{background:var(--primary-light);border-color:var(--primary);color:#5a4106;}

.recipe-body{
  flex:1 1 auto;min-height:0;
  display:flex;flex-direction:column;gap:6px;
  padding:8px 10px 6px 12px;
}
.section-h{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:8pt;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;
  color:var(--primary-dark);margin:0 0 3px;
  border-bottom:1px solid var(--primary);padding-bottom:2px;
}
.ingredients-list,.instructions-list{
  margin:0;padding-left:1em;font-size:11pt;line-height:1.42;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;color:var(--ink-soft);
}
.ingredients-list{list-style:none;padding-left:0;}
.ingredients-list li{
  position:relative;padding-left:0.8em;margin-bottom:5px;
}
.ingredients-list li::before{
  content:'';position:absolute;left:0;top:0.5em;width:4px;height:4px;
  background:var(--primary);border-radius:50%;
}
.instructions-list{padding-left:1.3em;}
.instructions-list li{
  margin-bottom:6px;padding-left:0.15em;
}
.instructions-list li::marker{color:var(--primary-dark);font-weight:700;}

.recipe-footer{
  padding:6px 10px 8px 12px;
  display:flex;flex-direction:column;gap:5px;
  border-top:1px solid var(--line);
  background:var(--cream);
  /* Fixed min-height keeps nutrition-box anchored at the top (alignment "a pari") */
  min-height:1.30in;
  justify-content:flex-start;
}
.recipe-footer .nutrition-box{flex:0 0 auto;}
.recipe-footer .recipe-storage{margin-top:auto;}
.nutrition-box{
  background:var(--ink);color:var(--primary);
  border-radius:5px;padding:5px 8px;
  display:flex;flex-direction:column;gap:3px;
}
.nut-head{
  display:flex;justify-content:space-between;align-items:baseline;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
}
.nut-title{font-weight:700;font-size:8pt;letter-spacing:0.18em;text-transform:uppercase;color:var(--primary);}
.nut-extra{font-size:6.8pt;font-style:italic;color:#d8c466;}
.nut-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;}
.nut-stat{
  display:flex;flex-direction:column;align-items:center;
  background:rgba(253,199,5,0.1);border-radius:3px;padding:2px 0;
}
.nut-val{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:12pt;font-weight:700;color:#fff;line-height:1;
}
.nut-lbl{
  font-family:'Source Sans Pro',sans-serif;font-size:6.5pt;
  color:var(--primary);letter-spacing:0.15em;text-transform:uppercase;margin-top:1px;
}
.recipe-storage{
  display:flex;gap:5px;align-items:center;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:7.5pt;color:var(--muted);font-style:italic;line-height:1.32;
  border-left:2px solid var(--primary);padding:1px 0 1px 6px;
  /* Same height across paired cards regardless of text wrap */
  min-height:0.5in;height:0.5in;
}
.recipe-storage .storage-text{flex:1 1 auto;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
.storage-label{
  font-style:normal;color:var(--ink);font-weight:700;
  text-transform:uppercase;letter-spacing:0.1em;font-size:7pt;
  background:var(--primary);padding:1px 5px;border-radius:3px;flex:0 0 auto;
}

/* Meal plan */
.mealplan-intro .page-content,
.week-page .page-content{padding:0.7in 0.75in 0.85in;}
.mealplan-intro .chapter-h1{font-size:22pt;}
.checklist{padding-left:1.2em;font-family:'Source Sans Pro',sans-serif;font-size:10pt;}
.checklist li{margin-bottom:5px;}
.week-header{margin-bottom:0.6em;}
.week-title{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:24pt;color:var(--primary-dark);margin:0;font-weight:700;
}
.week-rule{width:80px;height:2px;background:var(--primary);margin-top:0.4em;}
.week-body p{font-size:10pt;line-height:1.45;}
.week-h{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  text-transform:uppercase;letter-spacing:0.18em;font-size:9.5pt;
  color:var(--primary-dark);font-weight:700;margin:0.7em 0 0.3em;
  border-bottom:1px solid var(--primary);padding-bottom:3px;
}
.week-objective{
  background:var(--primary-soft);border-left:3px solid var(--primary);
  padding:6px 10px;font-style:italic;font-size:9.5pt;margin:0.4em 0 0.6em;
  font-family:'Source Sans Pro',sans-serif;color:var(--ink);
}
.week-callout{
  background:var(--cream);border-left:3px solid var(--primary-dark);
  padding:6px 10px;font-style:italic;font-size:9.5pt;margin:0.4em 0;
  font-family:'Source Sans Pro',sans-serif;color:var(--ink-soft);
}

/* Bonus */
.bonus-header{margin:0 0 1.2em;padding:0;}
.bonus-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.35em;
  color:var(--primary-dark);font-size:9.5pt;font-weight:600;margin:0 0 0.5em;
}
.bonus-h2{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:22pt;color:var(--ink);font-weight:700;margin:0;line-height:1.1;
}
.bonus-rule{width:80px;height:2px;background:var(--primary);margin:0.4em 0 0;}
.bonus-h3{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:14pt;color:var(--primary-dark);margin:0.8em 0 0.3em;font-weight:700;
}
.bonus-h4{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  text-transform:uppercase;letter-spacing:0.25em;font-size:9.5pt;
  color:var(--primary-dark);margin:0.9em 0 0.3em;font-weight:700;
}
.bonus-q{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:10pt;font-weight:600;color:var(--ink);margin:0.5em 0 0.2em;
}
.bonus-body{margin-top:1em;}
.bonus-page-cont .bonus-body{margin-top:0;}
.bonus-body p{font-size:9.8pt;line-height:1.45;margin-bottom:0.4em;}
.score-bucket{
  background:var(--primary);color:var(--ink);
  font-family:'Source Sans Pro',sans-serif;font-weight:700;
  letter-spacing:0.18em;text-transform:uppercase;
  padding:6px 10px;border-radius:4px;font-size:10pt;
  margin:0.6em 0 0.3em !important;
}
.hint{
  font-family:'Source Sans Pro',sans-serif;font-size:9.5pt;
  border-radius:4px;padding:5px 10px;margin:3px 0 !important;
}
.hint-pos{background:var(--primary-soft);border-left:3px solid var(--primary);color:var(--ink);}
.hint-neg{background:#fbe8e8;border-left:3px solid var(--rose);color:#5a1f1f;}
.hint-hack{background:var(--primary-light);border-left:3px solid var(--primary-dark);color:#4a3406;font-style:italic;}
.hint-session{background:#e3f2fd;border-left:3px solid #2196f3;font-weight:700;margin-top:0.8em !important;}
.hint-level{background:#f3e5f5;border-left:3px solid #9c27b0;font-weight:800;text-transform:uppercase;letter-spacing:0.05em;margin-top:1.2em !important;}
.restaurant-name{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:13pt;font-weight:700;color:var(--primary-dark);
  margin:0.7em 0 0.2em;border-bottom:1px solid var(--line);padding-bottom:2px;
}

/* Appendix */
.appendix-page .page-content{padding:0.7in 0.75in 0.85in;}
.app-table th, .app-table td{font-size:8.5pt;padding:4px 8px;}
.conv-grid{display:grid;grid-template-columns:1fr 1fr;gap:0.3in;}
.conv-card{background:var(--cream-2);border:1px solid var(--line);border-radius:6px;padding:0.18in;}
.conv-card:first-child{grid-column:1 / 3;}
.conv-h{
  font-family:'Cormorant Garamond','Georgia',serif;
  color:var(--primary-dark);font-size:14pt;margin:0 0 0.3em;font-weight:700;
}
.conv-table th{font-size:8.5pt;}
.conv-table td{font-size:9.5pt;}

/* Conclusion / review */
.conclusion-page .page-content{padding:0.85in 0.85in;}
.conclusion-page .prose p{font-size:11.5pt;line-height:1.55;}
.review-page .page-content{padding:0.85in 0.85in;text-align:center;}
.review-page .prose p{font-size:11pt;line-height:1.55;text-align:left;}
.end-mark{
  margin-top:1.5em;text-align:center;letter-spacing:0.4em;
  color:var(--primary-dark);font-family:'Source Sans Pro',sans-serif;
  font-size:10pt;font-weight:600;
}

/* Toolbar */
.toolbar{
  position:fixed;top:14px;right:14px;z-index:1000;
  display:flex;gap:8px;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
}
.toolbar button{
  border:1px solid var(--line);
  background:var(--paper);
  color:var(--ink);
  padding:8px 14px;
  border-radius:6px;
  font-size:10pt;font-weight:600;
  cursor:pointer;
  box-shadow:0 4px 12px rgba(0,0,0,0.1);
  transition:transform 0.15s, background 0.15s;
}
.toolbar button:hover{transform:translateY(-1px);}
.toolbar button.primary{background:var(--primary);color:var(--ink);border-color:var(--primary-dark);}
.toolbar .status{
  align-self:center;
  font-size:9pt;color:var(--muted);
  background:var(--paper);
  padding:6px 10px;border-radius:6px;
  border:1px solid var(--line);
  box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

/* PRINT — explicit portrait, no toolbar, no overflow indicator */
@page{
  size:letter portrait !important;
  margin:0 !important;
  bleed:0;
}
@media print{
  html,body{
    background:#fff;
    width:8.5in !important;
    height:11in !important;
    margin:0 !important;
    padding:0 !important;
  }
  .book{padding:0;gap:0;width:8.5in;}
  .page{
    box-shadow:none;
    margin:0;
    width:8.5in;
    height:11in;
    page-break-after:always;
  }
  .toolbar{display:none !important;}
  .page[data-overflow]::before{display:none !important;}
}
'''

# ----------- JS: TOC + auto-fit AI + PDF button -----------
js = r'''
(function(){
  function $(s,r){return (r||document).querySelector(s);}
  function $$(s,r){return Array.from((r||document).querySelectorAll(s));}
  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c];});
  }
  function ensureId(el){
    if(!el.id){ el.id = 'p-' + Math.random().toString(36).slice(2,9); }
    return el.id;
  }

  // Live overflow guard: shrink content via transform: scale() — works with pt units
  // (font-size % does not cascade to pt-sized children, so we use transform).
  // The page number footer sits at bottom: 0.35in. We reserve a SAFE-ZONE at the
  // bottom of every page (>= 5mm above the page number) where content must not enter.
  function fitOnePage(page){
    var content = page.querySelector('.page-content');
    if(!content) return;
    content.style.transform = '';
    content.style.transformOrigin = 'top center';
    page.removeAttribute('data-overflow');
    
    var pageH = page.offsetHeight;
    var natural = content.scrollHeight;
    // Threshold: page height minus 0.5in safety buffer for the page number
    var threshold = pageH - 48; 
    if(natural <= threshold) return;
    
    var scale = threshold / natural;
    var floor = 0.75;
    if(scale < floor){
      page.setAttribute('data-overflow', 'true');
      scale = floor;
    }
    content.style.transform = 'scale(' + scale.toFixed(4) + ')';
  }
  // Per-card auto-fit: when a recipe-body's ingredients+instructions exceed
  // the available flex space, scale the body so steps don't disappear behind
  // the nutrition footer. Uses transform: scale() with top-center origin so
  // the scaled content stays horizontally centered in the card.
  function fitOneCard(card){
    var body = card.querySelector('.recipe-body');
    if(!body) return;
    body.style.transform = '';
    body.style.transformOrigin = 'top center';
    var natural = body.scrollHeight;
    var avail = body.clientHeight;
    if(natural <= avail + 1) return;
    var scale = avail / natural;
    var floor = 0.62;
    if(scale < floor){ scale = floor; }
    body.style.transform = 'scale(' + scale.toFixed(4) + ')';
  }
  function fitAllPages(){
    $$('.page').forEach(fitOnePage);
    $$('.recipe-card').forEach(fitOneCard);
  }

  // Page numbering: front matter (title, copyright, TOC — anything with
  // data-no-toc) is unnumbered; counting starts at the Introduction.
  function numberPages(){
    var n = 0;
    $$('.page').forEach(function(p){
      if(p.hasAttribute('data-no-toc')){
        p.removeAttribute('data-page');
      } else {
        n += 1;
        p.setAttribute('data-page', n);
      }
    });
  }

  function buildTOC(){
    var pages = $$('.page');
    var entries = [];
    var pageNum = 0;
    pages.forEach(function(p){
      var isFront = p.hasAttribute('data-no-toc');
      if(!isFront) pageNum++;
      
      // Look for headings in sequence of priority
      var h1 = p.querySelector('.chapter-cover-title, .chapter-h1, .bonus-h2, .week-title');
      if(h1) {
          var ey = p.querySelector('.chapter-cover-eyebrow, .chapter-eyebrow, .bonus-eyebrow');
          var text = h1.textContent.trim();
          if(ey) text = ey.textContent.trim() + ' — ' + text;
          entries.push({level:1, text:text, page:isFront ? '' : pageNum, id:ensureId(p)});
          return;
      }
    });
    var tocA = $('#toc-nav');
    if(!tocA) return;
    tocA.innerHTML='';
    entries.forEach(function(e){
        var a = document.createElement('a');
        a.href = '#' + e.id;
        a.className = 'toc-h' + e.level;
        a.innerHTML = '<span class="toc-text"><span class="toc-text-inner">' + escapeHtml(e.text) + '</span></span><span class="toc-num">' + e.page + '</span>';
        tocA.appendChild(a);
    });
  }

  function makeToolbar(){
    var bar = document.createElement('div');
    bar.className = 'toolbar';
    bar.innerHTML = ''
      + '<span class="status" id="fitStatus">Checking layout…</span>'
      + '<button id="btnFit" title="Re-run live overflow check">↻ Re-check fit</button>'
      + '<button class="primary" id="btnPDF" title="Save as PDF (8.5 × 11 in portrait)">📄 Convert to PDF</button>';
    document.body.appendChild(bar);
    $('#btnPDF').addEventListener('click', function(){
      fitAllPages();
      window.print();
    });
    $('#btnFit').addEventListener('click', function(){
      $('#fitStatus').textContent = 'Re-fitting…';
      requestAnimationFrame(function(){ fitAllPages(); updateStatus(); });
    });
  }

  function updateStatus(){
    var s = $('#fitStatus');
    if(!s) return;
    var total = $$('.page').length;
    var overflowed = $$('.page[data-overflow="true"]').length;
    if(overflowed === 0){
      s.textContent = '✓ All ' + total + ' pages fit';
      s.style.color = '#1d1812';
    } else {
      s.textContent = '⚠ ' + overflowed + '/' + total + ' tight pages';
      s.style.color = '#c69c00';
    }
  }

  function debounce(fn, ms){
    var t;
    return function(){
      clearTimeout(t);
      var args = arguments;
      t = setTimeout(function(){ fn.apply(null, args); }, ms);
    };
  }

  function init(){
    numberPages();
    fitAllPages();
    buildTOC();
    numberPages();
    makeToolbar();
    updateStatus();

    if(document.fonts && document.fonts.ready){
      document.fonts.ready.then(function(){ fitAllPages(); updateStatus(); });
    }
    window.addEventListener('resize', debounce(function(){ fitAllPages(); updateStatus(); }, 200));
    window.addEventListener('beforeprint', function(){ fitAllPages(); });
    var mo = new MutationObserver(debounce(function(){ fitAllPages(); updateStatus(); }, 250));
    mo.observe(document.body, {childList:true, subtree:true, characterData:true});
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
'''

html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(book['title'])}</title>
<style>{css}</style>
</head>
<body>
<main class="book">
{body_html}
</main>
<script>{js}</script>
</body>
</html>'''

out = ROOT_DIR / 'High_Protein_Meal_Prep_Cookbook.html'
out.write_text(html_out, encoding='utf-8')
print('Wrote', out, 'size:', len(html_out), 'bytes')
print('Pages:', html_out.count('class="page'))
print('Recipe cards:', html_out.count('class="recipe-card"'))
