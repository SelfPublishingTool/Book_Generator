import requests
from openai import OpenAI
import sys

API_KEY = "YOUR_API_KEY_HERE"
client = OpenAI(api_key=API_KEY)

title = "High-Protein Egg & Veggie Muffins"

# Clean, direct prompt matching the user's request for realism without the "camera" artifacts
prompt = f'A hyper-realistic, top-down view of a single plate of {title}. The food is fully cooked, delicious, and perfectly plated. No raw ingredients, no split screens, no collages, no cameras. Just the pure finished dish.'

print("Generating 16:9 image...")
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1792x1024",
    quality="standard",
    n=1,
)
image_url = response.data[0].url
img_response = requests.get(image_url)
with open("images/recipe_1.png", "wb") as img_file:
    img_file.write(img_response.content)
print("Finito!")
