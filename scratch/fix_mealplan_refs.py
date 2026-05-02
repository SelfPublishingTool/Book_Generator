import json
import re

book_path = '/Users/michael/Desktop/Self Publishing/Tool Creazione Libri in html/work/book.json'

with open(book_path, 'r') as f:
    data = json.load(f)

recipes = {r['number']: r['title'] for r in data['recipes']}

def fix_references(text):
    # Find all RXX patterns
    refs = re.findall(r'R(\d+)\s*[—\-]\s*([^|]+)', text)
    new_text = text
    for num, title in refs:
        num = int(num)
        title = title.strip()
        # Find the correct number for this title
        correct_num = None
        for r_num, r_title in recipes.items():
            if title.lower() in r_title.lower() or r_title.lower() in title.lower():
                correct_num = r_num
                break
        
        if correct_num and correct_num != num:
            old_ref = f'R{num} — {title}'
            new_ref = f'R{correct_num} — {title}'
            # Also try dash if — fails
            if old_ref not in new_text:
                old_ref = f'R{num} - {title}'
                new_ref = f'R{correct_num} - {title}'
            
            # Use regex to be safe with spacing
            pattern = re.escape(f'R{num}') + r'\s*[—\-]\s*' + re.escape(title)
            replacement = f'R{correct_num} — {title}'
            new_text = re.sub(pattern, replacement, new_text)
            print(f"Fixed: {title} (R{num} -> R{correct_num})")
    return new_text

# Update Meal Plan
for week in data['mealplan']['weeks']:
    new_body = []
    for line in week['body_lines']:
        new_line = fix_references(line)
        new_body.append(new_line)
    week['body_lines'] = new_body

with open(book_path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
