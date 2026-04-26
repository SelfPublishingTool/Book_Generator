#!/usr/bin/env python3
"""Parse the cookbook markdown into structured JSON."""
import json
import re
from pathlib import Path

src = Path('/sessions/charming-exciting-noether/mnt/outputs/work/book_fixed.md').read_text(encoding='utf-8')
lines = src.splitlines()

def section_block(start, end):
    """Return a list of non-empty + sep-aware lines from [start, end)."""
    return lines[start:end]

# --- Identify all section starts ---
h1_starts = [i for i, l in enumerate(lines) if l.startswith('# ')]
h1_starts.append(len(lines))  # sentinel

book = {
    'title': None, 'subtitle': None, 'author': None,
    'copyright': None, 'disclaimer': [],
    'toc_lines': [],
    'introduction': {'title': None, 'subtitle': None, 'paragraphs': []},
    'chapter1': {'title': None, 'subtitle': None, 'sections': []},  # sections: [{heading, paragraphs/list/table}]
    'recipes': [],   # all 101
    'mealplan': {'title': None, 'subtitle': None, 'intro_paragraphs': [], 'how_to_read': [], 'weeks': []},
    'bonus': {'title': None, 'bonuses': []},
    'appendix_a': {'title': None, 'sub': None, 'intro': '', 'rows': []},
    'appendix_b': {'title': None, 'sub': None, 'foods': [], 'volume': [], 'weight': [], 'oven': []},
    'conclusion': {'title': None, 'subtitle': None, 'paragraphs': []},
    'review_section': {'title': None, 'paragraphs': []},
}

# --- Parse front matter (lines 0..47) ---
# 0: # Super Easy ...
# 2: ## subtitle
# 4: By Priscilla Quinn
# 6: © Copyright ...
# 8..: disclaimer
# 18: ## TABLE OF CONTENTS
# 19..47: TOC items

book['title'] = lines[0][2:].strip()
book['subtitle'] = lines[2][3:].strip()
book['author'] = lines[4].strip()
book['copyright'] = lines[6].strip()
# Disclaimer paragraphs from line 8 to line before TOC (line 18)
i = 8
while i < 18:
    if lines[i].strip():
        book['disclaimer'].append(lines[i].strip())
    i += 1

# TOC entries: lines 20..47 (skip the header at 18)
for i in range(20, 48):
    s = lines[i].strip()
    if s:
        book['toc_lines'].append(s)

# --- Parse INTRODUCTION (48..91) ---
intro_h1_idx = 48
# Line 48: # INTRODUCTION
# Line 50: ## You Didn't Fail. Your Schedule Did.
book['introduction']['title'] = 'Introduction'
book['introduction']['subtitle'] = lines[50][3:].strip()
i = 52
paras = []
while i < 92:
    s = lines[i]
    if s.strip():
        paras.append(s.strip())
    i += 1
book['introduction']['paragraphs'] = paras

# --- Parse CHAPTER 1 (92..193) ---
# 92: # CHAPTER 1
# 94: ## The Prep-Once System
# 96, 104, 120, 124, 136, 144, 158: ### subsection
book['chapter1']['title'] = 'Chapter 1'
book['chapter1']['subtitle'] = lines[94][3:].strip()
# Find subsections
sub_starts = [i for i, l in enumerate(lines[:194]) if l.startswith('### ') and i >= 95]
sub_starts.append(194)
sections = []
for k in range(len(sub_starts)-1):
    s_idx = sub_starts[k]
    e_idx = sub_starts[k+1]
    heading = lines[s_idx][4:].strip()
    body_lines = []
    for j in range(s_idx+1, e_idx):
        body_lines.append(lines[j])
    sections.append({'heading': heading, 'body': body_lines})
book['chapter1']['sections'] = sections

# --- Parse all 101 RECIPES ---
recipe_starts = [i for i, l in enumerate(lines) if re.match(r'^### Recipe \d+ ', l)]
chapter_recipe_ranges = [
    (194, 743, 'Chapter 2', 'Breakfasts', 'Start the Day on Autopilot'),
    (743, 1553, 'Chapter 3', 'Lunches', 'Make It Once. Carry It All Week.'),
    (1553, 2609, 'Chapter 4', 'Dinners', 'The Meal That Ends the Day Right'),
    (2609, 3075, 'Chapter 5', 'Snacks & Mini Meals', 'Crush Cravings Before They Crush Your Progress'),
    (3075, 3647, 'Chapter 6', 'Soups & Stews', 'The Best Meal You Can Make in Bulk'),
    (3647, 3947, 'Chapter 7', 'High-Protein Treats', 'Because "Never Eat Dessert" Is Not a Plan'),
    (3947, 4153, 'Chapter 8', 'Sauces, Marinades & Dressings', 'The Chapter No Competitor Has'),
]

book['chapters_meta'] = []
for cs, ce, ch_title, ch_sub, ch_quote in chapter_recipe_ranges:
    book['chapters_meta'].append({
        'title': ch_title, 'subtitle': ch_sub, 'quote': ch_quote,
        'recipe_range': (cs, ce),
    })

def parse_recipe(start, next_start):
    block = lines[start:next_start]
    # First line: "### Recipe N — Title"
    m = re.match(r'^### Recipe (\d+) [—\-] (.+)$', block[0])
    if not m:
        m = re.match(r'^### Recipe (\d+)\s*[—\-]\s*(.+)$', block[0])
    num = int(m.group(1))
    title = m.group(2).strip()
    # Second non-empty: meta line
    meta_idx = None
    for i, l in enumerate(block[1:], 1):
        if l.strip().startswith('Protein Source:'):
            meta_idx = i
            break
    meta_line = block[meta_idx].strip()
    # parse meta: "Protein Source: 🥚 Eggs | Yield: 12 muffins (3 per serving) | Prep: 10 min | Cook: 22 min"
    parts = [p.strip() for p in meta_line.split('|')]
    meta = {}
    for p in parts:
        if ':' in p:
            k, v = p.split(':', 1)
            meta[k.strip()] = v.strip()
    # Find ingredients block: "Ingredients:" header
    def find_label(lab, after=0):
        for i in range(after, len(block)):
            if block[i].strip().rstrip(':') == lab.rstrip(':'):
                return i
            if block[i].strip().startswith(lab):
                return i
        return None
    ing_idx = find_label('Ingredients:', meta_idx+1)
    inst_idx = find_label('Instructions:', ing_idx+1) if ing_idx else None
    nut_idx = None
    for i in range(inst_idx+1 if inst_idx else 0, len(block)):
        if block[i].strip().startswith('Nutrition Facts'):
            nut_idx = i
            break
    # Ingredients: lines between ing_idx+1 and inst_idx, non-empty as items
    ingredients = []
    for i in range((ing_idx or 0)+1, inst_idx or len(block)):
        s = block[i].strip()
        if s:
            ingredients.append(s)
    # Instructions: lines between inst_idx+1 and nut_idx
    instructions = []
    for i in range((inst_idx or 0)+1, nut_idx or len(block)):
        s = block[i].strip()
        if s:
            instructions.append(s)
    # Nutrition: line after nut_idx label (might be on next non-empty line)
    nutrition_line = ''
    nutrition_label_extra = ''
    if nut_idx is not None:
        # The label might be "Nutrition Facts (per serving):" or include detail
        label = block[nut_idx].strip()
        # Look for an extra parenthetical
        m2 = re.search(r'Nutrition Facts\s*\((.*?)\)', label)
        if m2:
            nutrition_label_extra = m2.group(1)
        # Find next non-empty after nut_idx
        for i in range(nut_idx+1, len(block)):
            s = block[i].strip()
            if s:
                nutrition_line = s
                break
    # Storage note: check last few instructions for storage line
    storage = None
    if instructions:
        last = instructions[-1]
        if last.lower().startswith('store ') or 'store in the fridge' in last.lower() or 'store in an airtight' in last.lower():
            storage = last
            instructions = instructions[:-1]
    return {
        'number': num,
        'title': title,
        'protein_source': meta.get('Protein Source', ''),
        'yield': meta.get('Yield', ''),
        'prep': meta.get('Prep', ''),
        'cook': meta.get('Cook', meta.get('Chill', meta.get('Freeze',''))),
        'cook_label': 'Cook' if 'Cook' in meta else ('Chill' if 'Chill' in meta else ('Freeze' if 'Freeze' in meta else 'Cook')),
        'ingredients': ingredients,
        'instructions': instructions,
        'nutrition': nutrition_line,
        'nutrition_extra': nutrition_label_extra,
        'storage': storage,
    }

all_recipes = []
recipe_starts_with_end = recipe_starts + [len(lines)]
for k in range(len(recipe_starts)):
    s = recipe_starts[k]
    # determine end: next recipe start OR start of next chapter (h1)
    next_h1 = next((h for h in h1_starts if h > s), None)
    next_recipe = recipe_starts[k+1] if k+1 < len(recipe_starts) else None
    candidates = [x for x in [next_h1, next_recipe] if x is not None]
    e = min(candidates)
    rec = parse_recipe(s, e)
    # Determine which chapter this recipe is in
    for ch in book['chapters_meta']:
        cs, ce = ch['recipe_range']
        if cs <= s < ce:
            rec['chapter'] = ch['title']
            break
    all_recipes.append(rec)
book['recipes'] = all_recipes

# --- Parse CHAPTER 9 (Meal Plan) ---
# Line 4152: # CHAPTER 9
# 4154: ## The 30-Day Meal Plan
# 4156: ### Zero Guesswork. Every Single Day.
# 4162: ### How to Read the Plan
# 4172: ## WEEK 1 — Build the Habit
# 4217: ## WEEK 2 — Find Your Rhythm
# 4260: ## WEEK 3 — Add Variety
# 4305: ## WEEK 4 — Make It Yours
# Ends at line 4341 (# CHAPTER 10)
mp = book['mealplan']
mp['title'] = 'Chapter 9'
mp['subtitle'] = 'The 30-Day Meal Plan'
mp['quote'] = 'Zero Guesswork. Every Single Day.'
# Lines 4156..4172: intro + how to read
intro_paras = []
htr = []
in_htr = False
for i in range(4157, 4172):
    s = lines[i].strip()
    if not s: continue
    if s.startswith('### How to Read'):
        in_htr = True
        continue
    if in_htr:
        htr.append(s)
    else:
        intro_paras.append(s)
mp['intro_paragraphs'] = intro_paras
mp['how_to_read'] = htr

week_starts = [i for i, l in enumerate(lines) if re.match(r'^## WEEK \d', l)]
week_starts.append(4341)
weeks = []
for k in range(len(week_starts)-1):
    s = week_starts[k]
    e = week_starts[k+1]
    title = lines[s][3:].strip()
    body = lines[s+1:e]
    weeks.append({'title': title, 'body_lines': body})
mp['weeks'] = weeks

# --- Parse CHAPTER 10 (Bonus Toolkit) ---
# Line 4341: # CHAPTER 10
# Line 4343: ## Your Bonus Toolkit
# Line 4345: ## BONUS 1 ...
book['bonus']['title'] = 'Chapter 10 — Your Bonus Toolkit'
bonus_starts = [i for i, l in enumerate(lines) if re.match(r'^## BONUS \d', l)]
bonus_starts.append(4682)  # appendix start
bonuses = []
for k in range(len(bonus_starts)-1):
    s = bonus_starts[k]
    e = bonus_starts[k+1]
    title = lines[s][3:].strip()
    body = lines[s+1:e]
    bonuses.append({'title': title, 'body_lines': body})
book['bonus']['bonuses'] = bonuses

# --- Parse APPENDIX A (4682..4792) ---
# Line 4682: # APPENDIX A
# Line 4684: ## Full Nutritional Index
# Line 4686: All 101 recipes...
# Lines 4687+ : table
book['appendix_a']['title'] = 'Appendix A'
book['appendix_a']['sub'] = 'Full Nutritional Index'
book['appendix_a']['intro'] = lines[4686].strip()
# Parse the markdown table from 4687 to 4793
table_rows = []
for i in range(4687, 4793):
    l = lines[i].strip()
    if l.startswith('|') and not re.match(r'^\|[\s:|-]+\|$', l):
        cells = [c.strip().replace('\\#', '#') for c in l.split('|')[1:-1]]
        # skip empty header rows
        if any(c for c in cells):
            table_rows.append(cells)
# First cell row is the header "[#, Recipe, Cal, Protein, Carbs, Fat]"
book['appendix_a']['rows'] = table_rows

# --- Parse APPENDIX B ---
# Line 4793: # APPENDIX B
# Line 4795: ## Protein Content of 50 Common Foods & Measurement Conversion Charts
# Line 4797: ### Protein Content of 50 Common Foods
# Lines after: table for foods
# Line 4853: ### Measurement Conversion Charts
# Sections: Volume, Weight, Oven Temperature
ab = book['appendix_b']
ab['title'] = 'Appendix B'
ab['sub'] = 'Protein Content of 50 Common Foods & Measurement Conversion Charts'

def parse_pipe_table(idx_start, idx_end):
    rows = []
    for i in range(idx_start, idx_end):
        l = lines[i].strip()
        if l.startswith('|') and not re.match(r'^\|[\s:|-]+\|$', l):
            cells = [c.strip() for c in l.split('|')[1:-1]]
            if any(c for c in cells):
                rows.append(cells)
    return rows

ab['foods'] = parse_pipe_table(4799, 4853)
# Find sub-tables for Volume, Weight, Oven
# Volume: starts after "Volume" label (around 4856)
def find_section_after(label, start):
    for i in range(start, len(lines)):
        if lines[i].strip() == label:
            return i
    return None

vol_idx = find_section_after('Volume', 4853)
wt_idx = find_section_after('Weight', 4853)
oven_idx = find_section_after('Oven Temperature', 4853)
end_idx = h1_starts[-2] if len(h1_starts) >= 2 else len(lines)  # before # CONCLUSION
# Find # CONCLUSION
conc_idx = next(i for i, l in enumerate(lines) if l.startswith('# CONCLUSION'))

ab['volume'] = parse_pipe_table(vol_idx, wt_idx)
ab['weight'] = parse_pipe_table(wt_idx, oven_idx)
ab['oven'] = parse_pipe_table(oven_idx, conc_idx)

# --- Parse CONCLUSION ---
# Line 4895: # CONCLUSION
# Line 4897: ## You Have the System Now
# until ## Leave a Review
review_idx = next(i for i, l in enumerate(lines) if l.startswith('## Leave a Review'))
book['conclusion']['title'] = 'Conclusion'
book['conclusion']['subtitle'] = lines[4897][3:].strip()
paras = []
for i in range(4898, review_idx):
    s = lines[i].strip()
    if s:
        paras.append(s)
book['conclusion']['paragraphs'] = paras

# --- Parse Review section ---
book['review_section']['title'] = lines[review_idx][3:].strip()
paras = []
for i in range(review_idx+1, len(lines)):
    s = lines[i].strip()
    if s:
        paras.append(s)
book['review_section']['paragraphs'] = paras

# Save JSON
out = Path('/sessions/charming-exciting-noether/mnt/outputs/work/book.json')
out.write_text(json.dumps(book, indent=2, ensure_ascii=False))
print('Wrote', out)
print('Recipes parsed:', len(book['recipes']))
print('First recipe sample:')
print(json.dumps(book['recipes'][0], indent=2, ensure_ascii=False))
print('---')
print(json.dumps(book['recipes'][50], indent=2, ensure_ascii=False))
print('---')
print(json.dumps(book['recipes'][100], indent=2, ensure_ascii=False))
