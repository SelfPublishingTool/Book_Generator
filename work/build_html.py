#!/usr/bin/env python3
"""Build the full HTML cookbook from parsed JSON."""
import json, html, re
from pathlib import Path

book = json.loads(Path('book.json').read_text(encoding='utf-8'))

def esc(s):
    return html.escape(s, quote=True) if s else ''

# Convert markdown-ish text helpers
def smart_html(s):
    """Escape and convert basic markdown like italic _x_ or **x** to HTML."""
    s = esc(s)
    # bold
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    # italic
    s = re.sub(r'(^|\W)\*(.+?)\*(?=\W|$)', r'\1<em>\2</em>', s)
    return s

# Helper for chapter cover pages
def chapter_cover(num_label, ch_title, ch_sub, ch_quote, recipe_count=None, color_class='chapter-green'):
    extra = f'<p class="chapter-cover-count">{recipe_count} recipes</p>' if recipe_count else ''
    return f'''<div class="page chapter-cover {color_class}">
  <div class="chapter-cover-inner">
    <p class="chapter-cover-eyebrow">{esc(num_label)}</p>
    <h1 class="chapter-cover-title">{esc(ch_title)}</h1>
    <div class="chapter-cover-divider"></div>
    <p class="chapter-cover-subtitle">{esc(ch_sub)}</p>
    {extra}
  </div>
</div>'''

# Recipe card builder
def render_recipe(r):
    ps = r.get('protein_source','')
    # Split emoji from text
    m = re.match(r'^([\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF☀-➿]+\s*\+?\s*[\U0001F300-\U0001FAFF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF☀-➿]*)\s*(.+)$', ps)
    if m:
        ps_emoji = m.group(1).strip()
        ps_text = m.group(2).strip()
    else:
        ps_emoji = ''
        ps_text = ps
    # Extract protein grams from nutrition
    nut = r.get('nutrition','')
    pg_match = re.search(r'Protein:\s*(\d+)g', nut)
    protein_g = pg_match.group(1) + 'g' if pg_match else ''
    # Build nutrition stats
    stats = []
    for label_re, label in [(r'Calories:\s*(\d+)', 'Calories'),
                             (r'Protein:\s*(\d+)g?', 'Protein'),
                             (r'Carbs:\s*(\d+)g?', 'Carbs'),
                             (r'Fat:\s*(\d+)g?', 'Fat')]:
        mm = re.search(label_re, nut)
        if mm:
            v = mm.group(1)
            unit = '' if label == 'Calories' else 'g'
            stats.append((label, v + unit))
    nut_extra = r.get('nutrition_extra','')
    stats_html = ''.join(f'<div class="nut-stat"><span class="nut-val">{esc(v)}</span><span class="nut-lbl">{esc(l)}</span></div>' for l,v in stats)
    ing_items = ''.join(f'<li>{smart_html(i)}</li>' for i in r['ingredients'])
    inst_items = ''.join(f'<li>{smart_html(i)}</li>' for i in r['instructions'])
    
    # Smart shortening logic
    ing_count = len(r['ingredients'])
    inst_len = sum(len(i) for i in r['instructions'])
    card_classes = ["recipe-card"]
    if ing_count > 12 or inst_len > 500:
        card_classes.append("recipe-card-compact")
    elif ing_count > 8 or inst_len > 350:
        card_classes.append("recipe-card-medium")
        
    storage = r.get('storage')
    storage_html = f'<div class="recipe-storage"><span class="storage-label">Storage</span><span class="storage-text">{smart_html(storage)}</span></div>' if storage else ''
    cook_label = r.get('cook_label', 'Cook')
    img_path = r.get('image_path', '')
    img_html = f'<img src="{esc(img_path)}" class="recipe-image" />' if img_path else '<div class="recipe-image-placeholder">No Image</div>'
    
    return f'''<article class="{" ".join(card_classes)}">
  <header class="recipe-header">
    <div class="recipe-id">{r['number']:02d} • RECIPE</div>
    <h3 class="recipe-title">{esc(r['title'])}</h3>
    <div class="recipe-meta">
      <span class="badge">{esc(ps_emoji)} {esc(ps_text)}</span>
      <span class="badge">Yield · {esc(r['yield'])}</span>
      <span class="badge">Prep · {esc(r['prep'])}</span>
      <span class="badge">{esc(cook_label)} · {esc(r['cook'])}</span>
    </div>
  </header>
  {img_html}
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
        <span class="nut-title">Nutrition Facts</span>
        {f'<span class="nut-extra">{esc(nut_extra)}</span>' if nut_extra else ''}
      </div>
      <div class="nut-stats">{stats_html}</div>
    </div>
    {storage_html}
  </footer>
</article>'''

# Helper to chunk recipe lists into pairs
def chunk_pairs(seq, size=2):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

# ---------------- Build HTML ----------------
parts = []

# 1. Title page
parts.append(f'''<div class="page title-page">
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
</div>''')

# 2. Copyright / disclaimer page
discl_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in book['disclaimer'])
parts.append(f'''<div class="page legal-page" data-no-toc="true">
  <div class="legal-inner">
    <p class="copyright-line">{smart_html(book['copyright'])}</p>
    <hr class="legal-rule">
    <h2 class="legal-h">Disclaimer</h2>
    {discl_paras}
  </div>
</div>''')

# 3. TOC page (placeholder; filled in by JS)
parts.append('''<div class="page toc-page" data-no-toc="true">
  <header class="toc-header">
    <p class="toc-eyebrow">Cookbook</p>
    <h2 class="toc-title">Table of Contents</h2>
    <div class="toc-rule"></div>
  </header>
  <nav id="toc-nav" class="toc-list"></nav>
</div>
<div class="page toc-page-2" data-no-toc="true">
  <nav id="toc-nav-2" class="toc-list"></nav>
</div>''')

# 4. Introduction (multi-page, allow natural overflow into a 2nd page)
intro = book['introduction']
intro_paras_html = ''.join(f'<p>{smart_html(p)}</p>' for p in intro['paragraphs'])
# Split intro into pages with different thresholds
intro_pages = []
buf = ""
is_first_page = True
threshold = 1000 # Much smaller for the first page with header

for p in intro['paragraphs']:
    add = f'<p>{smart_html(p)}</p>'
    if len(buf) + len(add) > threshold and buf:
        intro_pages.append(buf)
        buf = add
        is_first_page = False
        threshold = 2200 # Normal limit for subsequent pages
    else:
        buf += add
if buf: intro_pages.append(buf)

# First page has the title block
first_intro = f'''<div class="page intro-page">
  <header class="chapter-head">
    <p class="chapter-eyebrow">Introduction</p>
    <h1 class="chapter-h1">{esc(intro['subtitle'])}</h1>
    <div class="chapter-rule"></div>
  </header>
  <div class="prose" style="max-height: 5in !important; overflow: hidden !important;">{intro_pages[0]}</div>
</div>'''
parts.append(first_intro)
for extra in intro_pages[1:]:
    parts.append(f'''<div class="page intro-page-cont">
  <div class="prose" style="max-height: 6in !important; overflow: hidden !important;">{extra}</div>
</div>''')

# 5. Chapter 1 — The Prep-Once System
ch1 = book['chapter1']
parts.append(chapter_cover('Chapter 1', ch1['subtitle'], 'The Foundation', 'Everything you need before the first cook', color_class='chapter-green'))

# Render all sections; auto-paginate roughly
def render_ch1_body_lines(body_lines):
    """Convert body lines to HTML, handling tables and paragraphs."""
    out = []
    i = 0
    while i < len(body_lines):
        l = body_lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        # Detect markdown table block
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
                head = rows[0]
                body = rows[1:]
                thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
                tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

# Group ch1 sections to fit ~2 per page
ch1_blocks = []
for sec in ch1['sections']:
    body_html = render_ch1_body_lines(sec['body'])
    ch1_blocks.append(f'<section class="prep-section"><h2 class="prep-h2">{esc(sec["heading"])}</h2><div class="prose">{body_html}</div></section>')

# Manually paginate: known content - 7 sections in chapter 1
# Page 1: How Much Protein + The 6 Protein Sources
# Page 2: The Simple Plate Formula + The Sunday Method + Fridge vs Freezer
# Page 3: The High-Protein Pantry Staples + Quick Reference table
ch1_pages = [
    [0, 1],
    [2, 3, 4],
    [5],
    [6],
]
for plist in ch1_pages:
    content = ''.join(ch1_blocks[i] for i in plist)
    parts.append(f'<div class="page ch1-page"><div class="prose" style="max-height: 6in !important; overflow: hidden !important;">{content}</div></div>')

# 6. Chapters 2-8: chapter cover + recipe pages (2 per page)
chapter_recipe_groups = {}
for r in book['recipes']:
    chapter_recipe_groups.setdefault(r['chapter'], []).append(r)

chapter_meta_lookup = {c['title']: c for c in book['chapters_meta']}

# Color rotation for chapter covers
ch_colors = {
    'Chapter 2': 'chapter-green',
    'Chapter 3': 'chapter-olive',
    'Chapter 4': 'chapter-forest',
    'Chapter 5': 'chapter-sage',
    'Chapter 6': 'chapter-warm',
    'Chapter 7': 'chapter-rose',
    'Chapter 8': 'chapter-cream',
}

for ch_title in ['Chapter 2', 'Chapter 3', 'Chapter 4', 'Chapter 5', 'Chapter 6', 'Chapter 7', 'Chapter 8']:
    meta = chapter_meta_lookup[ch_title]
    rs = chapter_recipe_groups[ch_title]
    parts.append(chapter_cover(ch_title, meta['subtitle'], meta['quote'], '', recipe_count=len(rs), color_class=ch_colors[ch_title]))
    # 2 recipes per page
    for pair in chunk_pairs(rs, 2):
        cards = ''.join(render_recipe(r) for r in pair)
        # If only 1 recipe (last page of odd chapter), add a single-recipe class
        cls = 'recipe-page-pair' if len(pair) == 2 else 'recipe-page-single'
        parts.append(f'<div class="page recipe-page {cls}" data-chapter="{esc(ch_title)}">{cards}</div>')

# 7. Chapter 9 — Meal Plan
mp = book['mealplan']
parts.append(chapter_cover('Chapter 9', mp['subtitle'], mp['quote'], '', color_class='chapter-olive'))

# Intro page for meal plan: includes intro paras + how to read
intro_html = ''.join(f'<p>{smart_html(p)}</p>' for p in mp['intro_paragraphs'])
htr_html = ''.join(f'<li>{smart_html(p)}</li>' for p in mp['how_to_read'])
parts.append(f'''<div class="page mealplan-intro">
  <header class="chapter-head">
    <h2 class="chapter-h1">{esc(mp['subtitle'])}</h2>
    <p class="chapter-h2">{esc(mp['quote'])}</p>
    <div class="chapter-rule"></div>
  </header>
  <div class="prose">{intro_html}</div>
  <h3 class="prose-h3">How to Read the Plan</h3>
  <ul class="checklist">{htr_html}</ul>
</div>''')

# Each week: 1 page if compact
def render_week_body(body_lines):
    out = []
    i = 0
    while i < len(body_lines):
        l = body_lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        # Sub-headings inside week (e.g., "Sunday Prep Guide:", "Daily Meal Plan:", "Weekly Win Journal", etc.)
        if l.endswith(':') and not l.startswith('|') and not l.startswith(' '):
            out.append(f'<h4 class="week-h">{esc(l[:-1])}</h4>')
            i += 1
            continue
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
                # First non-empty row is header
                head = rows[0]
                body = rows[1:]
                thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
                tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data-table compact"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            # Special highlighted line "Objective: ..."
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
  <header class="week-header">
    <h2 class="week-title">{esc(w['title'])}</h2>
    <div class="week-rule"></div>
  </header>
  <div class="prose week-body" style="max-height: 6.2in; overflow: hidden;">{body_html}</div>
</div>''')

# 8. Chapter 10 — Bonus Toolkit
parts.append(chapter_cover('Chapter 10', 'Your Bonus Toolkit', 'Beyond the recipes — the tools that make the system stick', '', color_class='chapter-rose'))

def render_bonus_body(body_lines):
    out = []
    i = 0
    while i < len(body_lines):
        l = body_lines[i].rstrip()
        if not l.strip():
            i += 1; continue
        if l.startswith('### '):
            out.append(f'<h3 class="bonus-h3">{esc(l[4:].strip())}</h3>')
            i += 1
            continue
        # uppercase section labels (LIFESTYLE, FOOD PREFERENCES, etc.)
        if l == l.upper() and len(l) > 3 and re.match(r'^[A-Z &]+$', l):
            out.append(f'<h4 class="bonus-h4">{esc(l)}</h4>')
            i += 1
            continue
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
                head = rows[0]
                body = rows[1:]
                thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
                tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
                out.append(f'<table class="data-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            # Score buckets, restaurant blocks
            if re.match(r'^\d+[–\-]\d+ points', l):
                out.append(f'<p class="score-bucket">{smart_html(l)}</p>')
            elif l.endswith(':') and len(l) < 60 and not l.startswith('✅') and not l.startswith('❌'):
                out.append(f'<h4 class="bonus-q">{esc(l[:-1])}</h4>')
            elif l.startswith('✅') or l.startswith('❌') or l.startswith('Protein hack'):
                cls = 'pos' if l.startswith('✅') else ('neg' if l.startswith('❌') else 'hack')
                out.append(f'<p class="hint hint-{cls}">{smart_html(l)}</p>')
            elif re.match(r'^[A-Z][^.]*$', l) and len(l) < 30 and i+1 < len(body_lines) and body_lines[i+1].strip().startswith('✅'):
                # restaurant name header
                out.append(f'<h5 class="restaurant-name">{esc(l)}</h5>')
            else:
                out.append(f'<p>{smart_html(l)}</p>')
            i += 1
    return ''.join(out)

for b in book['bonus']['bonuses']:
    title = b['title']
    body_html = render_bonus_body(b['body_lines'])
    # Split by character length into pages with different thresholds
    chunks = []
    cur = ""
    is_first_bonus_page = True
    threshold = 1000 # Smaller for the first page with bonus header
    
    # Split body_html into top-level elements
    elems = re.findall(r'<(?:h\d|p|table|ul|ol)[^>]*>.*?</(?:h\d|p|table|ul|ol)>', body_html, re.DOTALL)
    if not elems:
        elems = [body_html]
    for el in elems:
        if len(cur) + len(el) > threshold and cur:
            chunks.append(cur); cur = el
            is_first_bonus_page = False
            threshold = 2000
        else:
            cur += el
    if cur: chunks.append(cur)
    # First page has the bonus title
    parts.append(f'''<div class="page bonus-page">
  <header class="bonus-header">
    <p class="bonus-eyebrow">Bonus Toolkit</p>
    <h2 class="bonus-h2">{esc(title)}</h2>
    <div class="bonus-rule"></div>
  </header>
  <div class="prose bonus-body" style="max-height: 5in !important; overflow: hidden !important;">{chunks[0]}</div>
</div>''')
    for ch in chunks[1:]:
        parts.append(f'<div class="page bonus-page-cont"><div class="prose bonus-body" style="max-height: 6in !important; overflow: hidden !important;">{ch}</div></div>')

# 9. Appendix A
appA = book['appendix_a']
parts.append(chapter_cover('Appendix A', appA['sub'], 'All 101 recipes — calories, protein, carbs, and fat per serving', '', color_class='chapter-cream'))

# Build the table; first row is header
rows = appA['rows']
header = rows[0]
body_rows = rows[1:]
# Split into pages of ~30 rows each
def render_app_table(header, rows, title=''):
    thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in header) + '</tr>'
    tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in rows)
    title_html = f'<h3 class="app-h">{esc(title)}</h3>' if title else ''
    return f'{title_html}<table class="data-table app-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>'

# Chunk into 10-row pages for absolute safety in Landscape
chunk = 10
chunks = [body_rows[i:i+chunk] for i in range(0, len(body_rows), chunk)]
for k, c in enumerate(chunks):
    title_html = ''
    if k == 0:
        title_html = f'''<header class="chapter-head">
  <p class="chapter-eyebrow">Appendix A</p>
  <h2 class="chapter-h1">{esc(appA['sub'])}</h2>
  <div class="chapter-rule"></div>
</header>
<p class="prose"><em>{smart_html(appA['intro'])}</em></p>'''
    table_html = render_app_table(header, c)
    parts.append(f'<div class="page appendix-page"><div class="prose" style="max-height: 5.5in !important; overflow: hidden !important;">{title_html}{table_html}</div></div>')

# 10. Appendix B
appB = book['appendix_b']
parts.append(chapter_cover('Appendix B', appB['sub'], 'Reference for everyday cooking', '', color_class='chapter-sage'))

# Foods table — split if needed
foods_header = appB['foods'][0]
foods_body = appB['foods'][1:]
food_chunks = [foods_body[i:i+10] for i in range(0, len(foods_body), 10)]
for k, c in enumerate(food_chunks):
    title_html = ''
    if k == 0:
        title_html = f'''<header class="chapter-head">
  <p class="chapter-eyebrow">Appendix B</p>
  <h2 class="chapter-h1">Protein Content of 50 Common Foods</h2>
  <div class="chapter-rule"></div>
</header>'''
    table_html = render_app_table(foods_header, c)
    parts.append(f'<div class="page appendix-page">{title_html}{table_html}</div>')

# Conversion charts — all on one page
def render_conv_table(label, rows):
    head = rows[0]
    body = rows[1:]
    thead = '<tr>' + ''.join(f'<th>{smart_html(c)}</th>' for c in head) + '</tr>'
    tbody = ''.join('<tr>' + ''.join(f'<td>{smart_html(c)}</td>' for c in r) + '</tr>' for r in body)
    return f'<div class="conv-card"><h3 class="conv-h">{esc(label)}</h3><table class="data-table conv-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>'

vol_html = render_conv_table('Volume', appB['volume'])
wt_html = render_conv_table('Weight', appB['weight'])
oven_html = render_conv_table('Oven Temperature', appB['oven'])
parts.append(f'''<div class="page appendix-page conv-page">
  <header class="chapter-head">
    <p class="chapter-eyebrow">Appendix B</p>
    <h2 class="chapter-h1">Measurement Conversion Charts</h2>
    <div class="chapter-rule"></div>
  </header>
  <div class="conv-grid">
    {vol_html}
    {wt_html}
    {oven_html}
  </div>
</div>''')

# 11. Conclusion
conc = book['conclusion']
conc_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in conc['paragraphs'])
parts.append(f'''<div class="page conclusion-page">
  <header class="chapter-head">
    <p class="chapter-eyebrow">Conclusion</p>
    <h1 class="chapter-h1">{esc(conc['subtitle'])}</h1>
    <div class="chapter-rule"></div>
  </header>
  <div class="prose">{conc_paras}</div>
</div>''')

# 12. Review section
review = book['review_section']
rev_paras = ''.join(f'<p>{smart_html(p)}</p>' for p in review['paragraphs'])
parts.append(f'''<div class="page review-page">
  <header class="chapter-head">
    <h2 class="chapter-h1">{esc(review['title'])}</h2>
    <div class="chapter-rule"></div>
  </header>
  <div class="prose">{rev_paras}</div>
  <div class="end-mark">— End —</div>
</div>''')

body_html = '\n'.join(parts)

# ----------- CSS + JS -----------
css = r'''
:root{
  --green:#2c5f3f;
  --green-light:#7fa68a;
  --green-soft:#e8f0e9;
  --olive:#5b6b3e;
  --sage:#a3b18a;
  --cream:#f7f1e3;
  --cream-2:#fdf9ee;
  --beige:#efe6d2;
  --rose:#b85f5f;
  --warm:#a06840;
  --forest:#1f3d2c;
  --ink:#1d2a22;
  --ink-soft:#3a4a40;
  --muted:#6e7a70;
  --line:#d8d2c2;
  --paper:#fffdf7;
  --paper-2:#fdfaf2;
  --gold:#a07c2e;
  --shadow:0 0.5px 0 rgba(0,0,0,0.04), 0 6px 18px rgba(20,40,30,0.06);
}

*{box-sizing:border-box;}
html,body{
  margin:0;padding:0;
  background:#e7e3d4;
  color:var(--ink);
  font-family: 'Source Serif Pro', 'Cormorant Garamond', 'Georgia', 'Times New Roman', serif;
  line-height:1.45;
  -webkit-print-color-adjust:exact;
  print-color-adjust:exact;
}
.book{
  display:flex;flex-direction:column;align-items:center;
  padding:24px 0;gap:18px;
}

/* Page - Landscape */
.page{
  width:11in;
  height:8.5in;
  background:var(--paper);
  position:relative;
  padding:0.7in 0.8in 0.9in 0.8in;
  overflow:hidden;
  page-break-after:always;
  break-after:page;
  box-shadow:var(--shadow);
  background-image:
    radial-gradient(120% 50% at 50% 0%, rgba(220,200,160,0.05) 0%, rgba(255,253,247,0) 60%);
}
.page.title-page,
.page.chapter-cover{
  padding:0;
}

/* Page number */
.page::after{
  content: attr(data-page);
  position:absolute;
  bottom:0.35in;
  left:50%;
  transform:translateX(-50%);
  font-family:'Source Sans Pro','Inter','Helvetica Neue',sans-serif;
  font-size:9pt;
  color:var(--muted);
  letter-spacing:0.18em;
}
.page.title-page::after,
.page.chapter-cover::after,
.page.legal-page::after{ content:none; }

/* Title page */
.title-page{
  background: linear-gradient(160deg, var(--green) 0%, var(--forest) 70%);
  color:#f4ecd6;
  display:flex;align-items:center;justify-content:center;
}
.title-page-inner{
  text-align:center;width:78%;
  padding:0.8in;
  border:1px solid rgba(244,236,214,0.3);
  background: rgba(0,0,0,0.05);
  border-radius:6px;
}
.tp-eyebrow{
  text-transform:uppercase;letter-spacing:0.4em;
  font-size:11pt;color:#d8c896;font-weight:600;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  margin:0 0 1em;
}
.tp-divider{
  width:60px;height:2px;background:#d8c896;margin:0 auto 1.2em;
}
.tp-title{
  font-family:'Cormorant Garamond','Playfair Display','Georgia',serif;
  font-size:46pt;line-height:1.05;font-weight:700;
  margin:0 0 0.6em;color:#f4ecd6;
  letter-spacing:-0.01em;
}
.tp-subtitle{
  font-style:italic;font-size:15pt;line-height:1.45;
  color:#e8dcb6;margin:0 0 2em;
}
.tp-icon-row{font-size:24pt;letter-spacing:0.5em;margin:1.5em 0 2em;}
.tp-author{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:16pt;letter-spacing:0.2em;text-transform:uppercase;
  color:#d8c896;margin:0;
}
.tp-author strong{color:#fff;}

/* Legal page */
.legal-page{padding:1in 0.9in;}
.legal-inner{font-size:9.5pt;line-height:1.55;color:var(--ink-soft);}
.copyright-line{
  font-family:'Source Sans Pro',sans-serif;text-align:center;
  font-size:10pt;color:var(--muted);letter-spacing:0.05em;
}
.legal-rule{
  border:none;border-top:1px solid var(--line);
  margin:1.4em 0;width:80px;margin-left:auto;margin-right:auto;
}
.legal-h{
  text-align:center;font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.3em;font-size:10pt;
  color:var(--green);font-weight:700;margin:0 0 1.2em;
}
.legal-page p{margin:0 0 0.7em;text-align:justify;}

/* TOC */
.toc-page,.toc-page-2{padding:0.8in 0.85in;}
.toc-header{margin-bottom:1.3em;text-align:center;}
.toc-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.35em;
  color:var(--green);font-size:9.5pt;margin:0 0 0.5em;font-weight:600;
}
.toc-title{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:30pt;font-weight:700;margin:0;color:var(--ink);
}
.toc-rule{
  width:64px;height:2px;background:var(--green);margin:0.7em auto 0;
}
.toc-list{display:flex;flex-direction:column;gap:0.18em;}
.toc-list a{
  display:flex;align-items:baseline;gap:0.4em;
  text-decoration:none;color:var(--ink);
  padding:0.18em 0;border-bottom:1px dotted transparent;
}
.toc-list .toc-text{
  flex:1 1 auto;
  background-image: linear-gradient(to right, var(--line) 50%, transparent 50%);
  background-size: 6px 1px;
  background-position: 0 calc(100% - 0.18em);
  background-repeat: repeat-x;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.toc-list .toc-text-inner{
  background:var(--paper);
  padding-right:0.4em;
}
.toc-list .toc-num{
  font-family:'Source Sans Pro',sans-serif;
  font-size:10pt;color:var(--muted);min-width:1.4em;text-align:right;
  background:var(--paper);padding-left:0.4em;
}
.toc-list .toc-h1{font-weight:700;font-size:12pt;margin-top:0.55em;}
.toc-list .toc-h1 .toc-text-inner{color:var(--green);text-transform:uppercase;letter-spacing:0.08em;}
.toc-list .toc-h2{font-size:11pt;padding-left:0.5em;}
.toc-list .toc-h2 .toc-text-inner{font-style:italic;}
.toc-list .toc-h3{font-size:9.5pt;padding-left:1.1em;color:var(--ink-soft);}

/* Chapter heads (regular) */
.chapter-head{margin:0 0 1.3em;}
.chapter-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.35em;
  color:var(--green);font-size:10pt;font-weight:600;margin:0 0 0.5em;
}
.chapter-h1{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:36pt;font-weight:700;line-height:1.1;
  margin:0 0 0.5em;color:var(--ink);
}
.chapter-h2{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:24pt;font-style:italic;color:var(--muted);margin:0 0 0.4em;
}
.chapter-rule{width:64px;height:2px;background:var(--green);margin:0.4em 0 0;}

/* Chapter cover (full bleed) */
.chapter-cover{
  display:flex;align-items:center;justify-content:center;
  color:#f4ecd6;
}
.chapter-cover-inner{
  text-align:center;padding:0.8in 1.2in;width:100%;
  border-top:1px solid rgba(244,236,214,0.3);
  border-bottom:1px solid rgba(244,236,214,0.3);
  margin:0;
}
.chapter-cover-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.5em;
  font-size:11pt;color:#d8c896;font-weight:600;margin:0 0 1em;
}
.chapter-cover-title{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:48pt;font-weight:700;line-height:1.05;
  margin:0 0 0.5em;color:#f4ecd6;letter-spacing:-0.01em;
}
.chapter-cover-divider{width:80px;height:2px;background:#d8c896;margin:0.8em auto;}
.chapter-cover-subtitle{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:14pt;font-style:italic;color:#e8dcb6;margin:0;
}
.chapter-cover-count{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.4em;
  margin:1.4em 0 0;font-size:10pt;color:#d8c896;
}
.chapter-cover.chapter-green{background:linear-gradient(160deg,#2c5f3f 0%,#1f3d2c 80%);}
.chapter-cover.chapter-olive{background:linear-gradient(160deg,#5b6b3e 0%,#3b4a28 80%);}
.chapter-cover.chapter-forest{background:linear-gradient(160deg,#2a4a3a 0%,#0e261a 80%);}
.chapter-cover.chapter-sage{background:linear-gradient(160deg,#7d9166 0%,#4f6043 80%);}
.chapter-cover.chapter-warm{background:linear-gradient(160deg,#7c4f31 0%,#3f2615 80%);}
.chapter-cover.chapter-rose{background:linear-gradient(160deg,#8b3f3f 0%,#4a1c1c 80%);}
.chapter-cover.chapter-cream{background:linear-gradient(160deg,#a07c2e 0%,#5a4416 80%);}

/* Prose */
.prose{
  max-height: 6.2in; /* Global safety limit */
  overflow: hidden;
  padding-bottom: 0.6in;
}
.prose p{margin:0 0 0.6em;text-align:justify;font-size:12pt;line-height:1.55;overflow-wrap: break-word;}
.prose p strong{color:var(--green);}
.prose-h3{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:15pt;color:var(--green);margin:1em 0 0.4em;font-weight:700;
}
.intro-page .prose, .bonus-page .prose{
  max-height: 4.8in; /* Even smaller for pages with headers */
}
.intro-page .chapter-h1{font-size:24pt;}
.intro-page-cont{padding-top:0.85in;}

/* Chapter 1 */
.ch1-page{padding:0.7in 0.7in 0.85in;}
.page-frame{display:flex;flex-direction:column;gap:1em;}
.prep-section{padding:0.5em 0;}
.prep-h2{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:16pt;font-weight:700;color:var(--green);
  margin:0 0 0.5em;border-bottom:1px solid var(--line);padding-bottom:0.3em;
}
.prep-section .prose p{font-size:10.5pt;line-height:1.5;margin-bottom:0.45em;}

/* Tables */
.data-table{
  width:100%;border-collapse:collapse;font-size:9.5pt;
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  margin:0.4em 0 0.8em;
}
.data-table th{
  background:var(--green);color:#fff;text-align:left;
  padding:6px 10px;font-weight:600;letter-spacing:0.04em;
  font-size:9pt;text-transform:uppercase;
}
.data-table td{
  padding:5px 10px;border-bottom:1px solid var(--line);
  vertical-align:top;
}
.data-table tbody tr:nth-child(even) td{background:var(--cream-2);}
.data-table.compact th, .data-table.compact td{padding:3px 7px;font-size:8.5pt;}

/* Recipe page - 2 Columns Grid Landscape */
.recipe-page{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5in;
  padding: 0.6in 0.8in 0.8in;
  height: 8.5in;
}

.recipe-card{
  position: relative;
  background: transparent;
  display: flex;
  flex-direction: column;
  height: 7.1in;
  overflow: hidden;
}

.recipe-card::before{
  content:'';
  position:absolute;left:0;top:0;width:100%;height:3px;
  background: var(--green);
}

.recipe-header{
  margin-top: 10px;
  margin-bottom: 0.6rem;
}

.recipe-id{
  font-family: 'Source Sans Pro', sans-serif;
  font-size: 8pt;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--muted);
  margin-bottom: 4px;
}

.recipe-title{
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: 18pt;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.2rem;
  line-height: 1.1;
}

.recipe-meta{display:flex;flex-wrap:wrap;gap:4px;}
.badge{
  font-family:'Source Sans Pro',sans-serif;
  font-size:7pt;font-weight:600;
  padding:2px 7px;border-radius:10px;
  border:1px solid var(--line);background:var(--cream);
  color:var(--ink-soft);text-transform:uppercase;
}

.recipe-image {
  width: 100%;
  height: 4in;
  object-fit: cover;
  border-radius: 4px;
  margin: 0.4rem 0;
}

.recipe-image-placeholder {
  width: 100%;
  height: 4in;
  background: var(--cream-2);
  border: 1px dashed var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10pt;
  color: var(--muted);
  margin: 0.4rem 0;
}

.recipe-body{
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 4.8in;
  overflow: hidden;
}

.section-h{
  font-family:'Source Sans Pro',sans-serif;
  font-size:8pt;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
  color:var(--green);margin:0 0 4px;border-bottom:1px solid var(--green-light);
  padding-bottom:2px;
}

.ingredients-list, .instructions-list{
  margin:0;padding-left:1.1rem;font-size:10pt;line-height:1.25;
  font-family:'Source Sans Pro',sans-serif;color:var(--ink-soft);
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Smart Shortening Classes */
.recipe-card-medium .ingredients-list,
.recipe-card-medium .instructions-list {
  font-size: 9pt;
  line-height: 1.15;
}
.recipe-card-medium .recipe-image {
  height: 3.2in;
}

.recipe-card-compact .ingredients-list,
.recipe-card-compact .instructions-list {
  font-size: 8.5pt;
  line-height: 1.1;
}
.recipe-card-compact .recipe-image {
  height: 2.8in;
}
.recipe-card-compact .recipe-title {
  font-size: 16pt;
}

.recipe-footer{
  margin-top: auto;
  display:flex;flex-direction:column;gap:4px;
}

.nutrition-box{
  background: var(--green);
  color: white;
  border-radius: 6px;
  padding: 8px 12px;
}

.nut-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.nut-title {
  font-size: 8pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.nut-extra {
  font-size: 7.5pt;
  opacity: 0.8;
}

.nut-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.nut-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nut-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 14pt;
  font-weight: 700;
}

.nut-lbl {
  font-size: 6pt;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.7;
}

.recipe-storage{
  font-size: 8.5pt;
  line-height: 1.4;
  color: var(--muted);
  font-style: italic;
  border-left: 2px solid var(--green-light);
  padding-left: 8px;
}
.storage-label{
  font-style:normal;color:var(--green);font-weight:700;
  text-transform:uppercase;letter-spacing:0.12em;font-size:7.5pt;
  background:var(--green-soft);padding:1px 6px;border-radius:4px;flex:0 0 auto;
}

/* Meal plan */
.mealplan-intro,.week-page{padding:0.7in 0.75in 0.85in;}
.mealplan-intro .chapter-h1{font-size:22pt;}
.checklist{padding-left:1.2em;font-family:'Source Sans Pro',sans-serif;font-size:10pt;}
.checklist li{margin-bottom:5px;}
.week-header{margin-bottom:0.6em;}
.week-title{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:24pt;color:var(--green);margin:0;font-weight:700;
}
.week-rule{width:80px;height:2px;background:var(--green);margin-top:0.4em;}
.week-body p{font-size:10pt;line-height:1.45;}
.week-h{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  text-transform:uppercase;letter-spacing:0.18em;font-size:9.5pt;
  color:var(--green);font-weight:700;margin:0.7em 0 0.3em;
  border-bottom:1px solid var(--green-light);padding-bottom:3px;
}
.week-objective{
  background:var(--green-soft);border-left:3px solid var(--green);
  padding:6px 10px;font-style:italic;font-size:9.5pt;margin:0.4em 0 0.6em;
  font-family:'Source Sans Pro',sans-serif;color:var(--ink-soft);
}
.week-callout{
  background:var(--cream);border-left:3px solid var(--gold);
  padding:6px 10px;font-style:italic;font-size:9.5pt;margin:0.4em 0;
  font-family:'Source Sans Pro',sans-serif;color:var(--ink-soft);
}

/* Bonus */
.bonus-page,.bonus-page-cont{padding:0.7in 0.75in 0.85in;}
.bonus-eyebrow{
  font-family:'Source Sans Pro',sans-serif;
  text-transform:uppercase;letter-spacing:0.35em;
  color:var(--green);font-size:9.5pt;font-weight:600;margin:0 0 0.5em;
}
.bonus-h2{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:22pt;color:var(--ink);font-weight:700;margin:0;
}
.bonus-rule{width:80px;height:2px;background:var(--green);margin:0.4em 0 1em;}
.bonus-h3{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:14pt;color:var(--green);margin:0.8em 0 0.3em;font-weight:700;
}
.bonus-h4{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  text-transform:uppercase;letter-spacing:0.25em;font-size:9.5pt;
  color:var(--green);margin:0.9em 0 0.3em;font-weight:700;
}
.bonus-q{
  font-family:'Source Sans Pro','Helvetica Neue',sans-serif;
  font-size:10pt;font-weight:600;color:var(--ink);margin:0.5em 0 0.2em;
}
.bonus-body p{font-size:9.8pt;line-height:1.45;margin-bottom:0.4em;}
.score-bucket{
  background:var(--green);color:#fff;
  font-family:'Source Sans Pro',sans-serif;font-weight:700;
  letter-spacing:0.18em;text-transform:uppercase;
  padding:6px 10px;border-radius:4px;font-size:10pt;
  margin:0.6em 0 0.3em !important;
}
.hint{
  font-family:'Source Sans Pro',sans-serif;font-size:9.5pt;
  border-radius:4px;padding:5px 10px;margin:3px 0 !important;
}
.hint-pos{background:#e8f0e9;border-left:3px solid var(--green);color:var(--ink);}
.hint-neg{background:#fbe8e8;border-left:3px solid var(--rose);color:#5a1f1f;}
.hint-hack{background:#fdeed3;border-left:3px solid var(--gold);color:#5a3e0c;font-style:italic;}
.restaurant-name{
  font-family:'Cormorant Garamond','Georgia',serif;
  font-size:13pt;font-weight:700;color:var(--green);
  margin:0.7em 0 0.2em;border-bottom:1px solid var(--line);padding-bottom:2px;
}

/* Appendix */
.appendix-page{padding:0.7in 0.75in 0.85in;}
.app-table th, .app-table td{font-size:8.5pt;padding:4px 8px;}
.app-h{
  font-family:'Cormorant Garamond','Georgia',serif;
  color:var(--green);font-size:14pt;margin:0.3em 0;
}
.conv-grid{
  display:grid;grid-template-columns:1fr 1fr;gap:0.3in;
}
.conv-card{
  background:var(--cream-2);border:1px solid var(--line);
  border-radius:6px;padding:0.18in;
}
.conv-card:first-child{grid-column:1 / 3;}
.conv-h{
  font-family:'Cormorant Garamond','Georgia',serif;
  color:var(--green);font-size:14pt;margin:0 0 0.3em;font-weight:700;
}
.conv-table th{font-size:8.5pt;}
.conv-table td{font-size:9.5pt;}

/* Conclusion */
.conclusion-page{padding:0.85in 0.85in;}
.conclusion-page .prose p{font-size:11.5pt;line-height:1.55;}
.review-page{padding:0.85in 0.85in;text-align:center;}
.review-page .prose p{font-size:11pt;line-height:1.55;text-align:left;}
.end-mark{
  margin-top:1.5em;text-align:center;letter-spacing:0.4em;
  color:var(--green);font-family:'Source Sans Pro',sans-serif;
  font-size:10pt;font-weight:600;
}

/* Print Landscape */
@page{ size:11in 8.5in; margin:0; }
@media print{
  html,body{background:#fff;}
  .book{padding:0;gap:0;}
  .page{box-shadow:none;margin:0;width:11in;height:8.5in;}
  .page::after{content: attr(data-page);}
}
'''

js = r'''
(function(){
  function build(){
    var pages = document.querySelectorAll('.page');
    var idx = 0;
    pages.forEach(function(p){
      idx += 1;
      p.setAttribute('data-page', idx);
    });
    var entries = [];
    pages.forEach(function(p){
      if(p.hasAttribute('data-no-toc')) return;
      var pageNum = p.getAttribute('data-page');
      // Choose the most representative heading on the page
      // priority: chapter-cover-title > chapter-h1 > recipe-title (skipped) > h2
      var heading = p.querySelector('.chapter-cover-title');
      if(heading){
        var ey = p.querySelector('.chapter-cover-eyebrow');
        var sub = p.querySelector('.chapter-cover-subtitle');
        var label = (ey ? ey.textContent.trim() + ' — ' : '') + heading.textContent.trim();
        entries.push({level:1, text: label, page: pageNum, id: ensureId(p)});
        if(sub){ /* skip subtitle in TOC for clarity */ }
        return;
      }
      var h1 = p.querySelector('.chapter-h1');
      if(h1){
        var ey2 = p.querySelector('.chapter-eyebrow');
        var label2 = (ey2 ? ey2.textContent.trim() + ' — ' : '') + h1.textContent.trim();
        entries.push({level:1, text: label2, page: pageNum, id: ensureId(p)});
        return;
      }
      // Week page
      var wt = p.querySelector('.week-title');
      if(wt){
        entries.push({level:2, text: wt.textContent.trim(), page: pageNum, id: ensureId(p)});
        return;
      }
      // Bonus page
      var bh = p.querySelector('.bonus-h2');
      if(bh){
        entries.push({level:2, text: bh.textContent.trim(), page: pageNum, id: ensureId(p)});
        return;
      }
    });
    // Render TOC
    var tocA = document.getElementById('toc-nav');
    var tocB = document.getElementById('toc-nav-2');
    if(!tocA) return;
    tocA.innerHTML = ''; if(tocB) tocB.innerHTML = '';
    var firstHalf, secondHalf;
    var split = Math.ceil(entries.length / 2);
    firstHalf = entries.slice(0, split);
    secondHalf = entries.slice(split);
    function pushTo(target, list){
      list.forEach(function(e){
        var a = document.createElement('a');
        a.href = '#' + e.id;
        a.className = 'toc-h' + e.level;
        a.innerHTML = '<span class="toc-text"><span class="toc-text-inner">' + escapeHtml(e.text) + '</span></span><span class="toc-num">' + e.page + '</span>';
        target.appendChild(a);
      });
    }
    pushTo(tocA, firstHalf);
    if(tocB) pushTo(tocB, secondHalf);
    // Hide second TOC page if empty
    if(tocB && secondHalf.length === 0){
      var p2 = tocB.closest('.page');
      if(p2) p2.style.display = 'none';
    }
  }
  function ensureId(el){
    if(!el.id){ el.id = 'p-' + Math.random().toString(36).slice(2,9); }
    return el.id;
  }
  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c];});
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
'''

# Compose final HTML
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

out1 = Path('../High_Protein_Meal_Prep_Cookbook.html')
out1.write_text(html_out, encoding='utf-8')
print(f'SAVED TO WORKSPACE: {out1.absolute()}')

# Also save to original Claude folder to be sure
out2 = Path('/Users/michael/Desktop/Self Publishing/Libri in HTML - Claude/High_Protein_Meal_Prep_Cookbook/High_Protein_Meal_Prep_Cookbook.html')
try:
    out2.write_text(html_out, encoding='utf-8')
    print(f'SAVED TO CLAUDE FOLDER: {out2.absolute()}')
except Exception as e:
    print(f'COULD NOT SAVE TO CLAUDE FOLDER: {e}')

# Quick sanity counts
import re as _re
print('Page divs:', html_out.count('class="page'))
print('Recipe cards:', html_out.count('class="recipe-card'))
