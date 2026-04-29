import json

with open('work/book.json', 'r', encoding='utf-8') as f:
    book_text = f.read()

replacements = {
    "Weight Loss": "Fat-Loss",
    "weight loss": "fat-loss",
    "Weight loss": "Fat-loss",
    "Lose Weight": "Lose Fat",
    "lose weight": "lose fat",
    "losing weight": "losing fat",
    "Losing weight": "Losing fat"
}

for old, new in replacements.items():
    book_text = book_text.replace(old, new)

with open('work/book.json', 'w', encoding='utf-8') as f:
    f.write(book_text)

print("Text replaced successfully.")
