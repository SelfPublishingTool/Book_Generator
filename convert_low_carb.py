import json
import re

with open('work/book.json', 'r', encoding='utf-8') as f:
    book = json.load(f)

# Update subtitle
book['subtitle'] = "101 Make-Ahead Low-Carb Recipes with 25g+ Protein Per Meal — Prep Once, Eat All Week, and Finally Lose Weight"

# Update chapters
for i, line in enumerate(book['toc_lines']):
    if "Chapter 2" in line:
        book['toc_lines'][i] = "Chapter 2 — Low-Carb Breakfasts (14 recipes)"
    elif "Chapter 3" in line:
        book['toc_lines'][i] = "Chapter 3 — Keto & Low-Carb Lunches (20 recipes)"
    elif "Chapter 4" in line:
        book['toc_lines'][i] = "Chapter 4 — Lean & Low-Carb Dinners (26 recipes)"

subs = {
    # Oats -> Chia
    r'\boats?\b': 'chia seeds',
    r'\bovernight oats?\b': 'chia seed pudding',
    r'\bOats?\b': 'Chia seeds',
    r'\bOvernight Oats?\b': 'Chia Pudding',
    
    # Rice -> Cauliflower Rice
    r'\bbrown rice\b': 'cauliflower rice',
    r'\brice\b': 'cauliflower rice',
    r'\bBrown Rice\b': 'Cauliflower Rice',
    r'\bRice\b': 'Cauliflower Rice',

    # Pasta/Noodles -> Zoodles
    r'\bwhole wheat pasta\b': 'zucchini noodles',
    r'\bpasta\b': 'zucchini noodles',
    r'\bnoodles?\b': 'zucchini noodles',
    r'\bWhole Wheat Pasta\b': 'Zucchini Noodles',
    r'\bPasta\b': 'Zucchini Noodles',
    r'\bNoodles?\b': 'Zucchini Noodles',

    # Potato -> Zucchini / Cauliflower
    r'\bsweet potatoes?\b': 'diced zucchini',
    r'\bpotatoes?\b': 'diced zucchini',
    r'\bSweet Potatoes?\b': 'Diced Zucchini',
    r'\bPotatoes?\b': 'Diced Zucchini',

    # Wraps/Tortilla -> Lettuce Wrap
    r'\bwraps?\b': 'lettuce wraps',
    r'\btortillas?\b': 'lettuce wraps',
    r'\bWraps?\b': 'Lettuce Wraps',
    r'\bTortillas?\b': 'Lettuce Wraps',

    # Bread/Toast -> Keto Bread
    r'\bbread\b': 'keto bread',
    r'\btoast\b': 'keto toast',
    r'\bbagels?\b': 'keto bagels',
    r'\bBread\b': 'Keto Bread',
    r'\bToast\b': 'Keto Toast',
    r'\bBagels?\b': 'Keto Bagels',

    # Beans/Lentils -> Mushrooms/Peppers
    r'\bblack beans?\b': 'diced bell peppers',
    r'\bwhite beans?\b': 'diced mushrooms',
    r'\bbeans?\b': 'diced mushrooms',
    r'\blentils?\b': 'chopped mushrooms',
    r'\bchickpeas?\b': 'roasted walnuts',
    r'\bquinoa\b': 'hemp hearts',

    r'\bBlack Beans?\b': 'Diced Bell Peppers',
    r'\bWhite Beans?\b': 'Diced Mushrooms',
    r'\bBeans?\b': 'Diced Mushrooms',
    r'\bLentils?\b': 'Chopped Mushrooms',
    r'\bChickpeas?\b': 'Roasted Walnuts',
    r'\bQuinoa\b': 'Hemp Hearts'
}

def apply_subs(text):
    for pattern, replacement in subs.items():
        text = re.sub(pattern, replacement, text)
    return text

for r in book.get('recipes', []):
    r['title'] = apply_subs(r['title'])
    r['ingredients'] = [apply_subs(ing) for ing in r['ingredients']]
    r['instructions'] = [apply_subs(inst) for inst in r['instructions']]

with open('work/book.json', 'w', encoding='utf-8') as f:
    json.dump(book, f, indent=2, ensure_ascii=False)

print("Conversion complete.")
