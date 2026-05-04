#!/usr/bin/env python3
"""Create Kindle submission ZIP for Amazon KDP.

Packages:
  High_Protein_Meal_Prep_Cookbook_Kindle.html   (reflowable HTML)
  images/recipe_*.jpg                            (optimized JPEG, max 1280px)

Images are converted PNG → JPEG (quality 82, max 1280px wide) on-the-fly to
keep ZIP under ~20 MB. KDP Kindle max is 650 MB but smaller = faster delivery.

Output: High_Protein_Meal_Prep_Cookbook_Kindle.zip  (in root dir)

Usage:
  python3 work/create_kindle_zip.py
"""
import io, zipfile
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR  = BASE_DIR.parent

html_src  = ROOT_DIR / 'High_Protein_Meal_Prep_Cookbook_Kindle.html'
images_dir = ROOT_DIR / 'images'
out_zip   = ROOT_DIR / 'High_Protein_Meal_Prep_Cookbook_Kindle.zip'

KINDLE_MAX_WIDTH  = 1280   # px — matches largest Kindle screen (Fire HD 10)
JPEG_QUALITY      = 82     # 82 = good visual quality, ~4-10× smaller than PNG

if not html_src.exists():
    print('ERROR: Kindle HTML not found. Run build_kindle.py first.')
    raise SystemExit(1)

# The HTML references images/recipe_N.png — rewrite to images/recipe_N.jpg in the ZIP copy
html_text = html_src.read_text(encoding='utf-8')
html_text_for_zip = html_text.replace('images/recipe_', 'images/recipe_').replace('.png"', '.jpg"')

print('Building Kindle ZIP...')
total_orig = 0
total_new  = 0

with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    # HTML (with .png → .jpg refs patched)
    zf.writestr(html_src.name, html_text_for_zip.encode('utf-8'))
    print(f'  + {html_src.name}')

    # Images: convert PNG → JPEG on-the-fly
    png_files = sorted(images_dir.glob('recipe_*.png')) if images_dir.exists() else []
    for png in png_files:
        orig_size = png.stat().st_size
        total_orig += orig_size

        img = Image.open(png).convert('RGB')
        if img.width > KINDLE_MAX_WIDTH:
            ratio = KINDLE_MAX_WIDTH / img.width
            img = img.resize((KINDLE_MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
        jpg_bytes = buf.getvalue()
        total_new += len(jpg_bytes)

        jpg_name = f'images/{png.stem}.jpg'
        zf.writestr(jpg_name, jpg_bytes)

    print(f'  + images/ ({len(png_files)} files, {total_orig/1e6:.0f} MB → {total_new/1e6:.0f} MB)')

zip_mb = out_zip.stat().st_size / (1024 * 1024)
print(f'\nWrote:    {out_zip}')
print(f'ZIP size: {zip_mb:.1f} MB  (was {total_orig/1e6:.0f} MB of raw PNG)')
print(f'\nUpload this ZIP to Amazon KDP → Kindle eBook → manuscript file.')
