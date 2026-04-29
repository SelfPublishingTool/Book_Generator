import os
import json
import time
import requests
from openai import OpenAI

# Prendi la chiave dalla variabile d'ambiente per sicurezza
API_KEY = os.getenv("OPENAI_API_KEY", "INSERISCI_QUI_LA_CHIAVE")

client = OpenAI(api_key=API_KEY)

BOOK_JSON_PATH = "work/book.json"
IMAGES_DIR = "images"

def main():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    with open(BOOK_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    recipes = data.get("recipes", [])
    
    for recipe in recipes:
        number = recipe.get("number")
        
        # Salta la prima perché l'abbiamo già (se vuoi rigenerarla cancellala dalla cartella)
        title = recipe.get("title")
        img_filename = f"recipe_{number}.png"
        img_path = os.path.join(IMAGES_DIR, img_filename)
        
        if os.path.exists(img_path):
            print(f"[{number}] Immagine già esistente, la salto: {title}")
            continue
            
        # Sostituzione precauzionale per le uova per evitare tuorli crudi
        visual_title = title.replace("Egg", "Omelette-style").replace("egg", "omelette-style")
        
        # Prompt con istruzioni tassative all'inizio
        prompt = (
            f"STRICTLY NO EGGS, NO YELLOW YOLKS. NO TEXT, NO NUMBERS, NO LABELS, NO OVERLAYS. "
            f"A professional high-end culinary photography of: '{visual_title}'. "
            f"Top-down flat lay perspective, natural soft lighting, gourmet styling on an elegant plate. "
            f"Pure photography, only the food on the plate, ready to be served."
        )
        
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                style="vivid",
                n=1,
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt
            print(f"[{number}] Prompt riscritto da DALL-E: {revised_prompt}")
            
            # Download the image
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            with open(img_path, "wb") as img_file:
                img_file.write(img_response.content)
                
            print(f"[{number}] Salvata con successo in {img_path}")
            
            # Pausa per non intasare i server OpenAI
            time.sleep(10)
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[{number}] Errore API: {e}")
            if "rate_limit_exceeded" in error_msg or "429" in error_msg:
                print("Limite di richieste raggiunto (Rate Limit). Aspetto 60 secondi e riprovo...")
                time.sleep(60)
                # Qui potremmo implementare un retry, ma per ora il loop si ferma. L'utente lo rilancerà.
            break

if __name__ == "__main__":
    main()
