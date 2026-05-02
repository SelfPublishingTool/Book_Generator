#!/usr/bin/env python3
"""Fix all image_path references in book.json by mapping recipes to their
correct images from 'images ok/' based on fuzzy title matching with titles.txt."""

import json, os, shutil, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_PATH = os.path.join(BASE_DIR, 'work', 'book.json')
TITLES_PATH = os.path.join(BASE_DIR, 'titles.txt')
OK_DIR = os.path.join(BASE_DIR, 'images ok')
IMG_DIR = os.path.join(BASE_DIR, 'images')

# Load data
with open(BOOK_PATH) as f:
    book = json.load(f)

# Parse titles.txt
img_titles = {}
with open(TITLES_PATH) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(': ', 1)
        if len(parts) == 2:
            num = int(parts[0])
            img_titles[num] = parts[1]

# Build mapping using fuzzy sequential matching
titles_list = [(n, t) for n, t in sorted(img_titles.items())]
book_list = [(r['number'], r['title']) for r in book['recipes']]

def similar(a, b):
    def words(s):
        s = s.lower()
        s = re.sub(r'[^a-z0-9 ]', ' ', s)
        return set(w for w in s.split() if len(w) > 2)
    wa = words(a)
    wb = words(b)
    if not wa or not wb:
        return False
    overlap = len(wa & wb) / min(len(wa), len(wb))
    return overlap >= 0.5

ti = 0
bi = 0
mapping = {}  # book_recipe_number -> img_ok_number or None

while bi < len(book_list):
    bnum, btitle = book_list[bi]
    if ti < len(titles_list):
        tnum, ttitle = titles_list[ti]
        if similar(btitle, ttitle):
            mapping[bnum] = tnum
            ti += 1
            bi += 1
        else:
            mapping[bnum] = None
            bi += 1
    else:
        mapping[bnum] = None
        bi += 1

# Step 1: Copy correct images from "images ok" to "images"
print("=== COPYING IMAGES ===")
for bnum, img_num in sorted(mapping.items()):
    dest = os.path.join(IMG_DIR, f'recipe_{bnum}.png')
    if img_num is not None:
        src = os.path.join(OK_DIR, f'{img_num}.png')
        if os.path.exists(src):
            shutil.copy2(src, dest)
            print(f'  ✓ images ok/{img_num}.png → images/recipe_{bnum}.png')
        else:
            print(f'  ✗ images ok/{img_num}.png NOT FOUND')
    else:
        print(f'  ⊘ Recipe {bnum}: no source image (new recipe)')

# Step 2: Update book.json image_path
print("\n=== UPDATING BOOK.JSON ===")
changes = 0
for r in book['recipes']:
    rnum = r['number']
    img_num = mapping.get(rnum)
    if img_num is not None:
        new_path = f'images/recipe_{rnum}.png'
    else:
        new_path = None
    
    old_path = r.get('image_path')
    if old_path != new_path:
        print(f'  Recipe {rnum}: {old_path} → {new_path}')
        r['image_path'] = new_path
        changes += 1

print(f'\nTotal changes: {changes}')

# Save updated book.json
with open(BOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(book, f, indent=2, ensure_ascii=False)
print(f'Saved updated book.json')

# Summary
matched = sum(1 for v in mapping.values() if v is not None)
unmatched = [k for k, v in mapping.items() if v is None]
print(f'\nMatched: {matched} recipes with images')
print(f'No image: {unmatched}')
