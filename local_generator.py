import os
import json
import torch
import time
from diffusers import StableDiffusionXLPipeline, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

BOOK_JSON = "work/book.json"
IMAGES_DIR = "images"

def main():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    print("--- GENERATORE BLINDATO (STRETTO CONTROLLO QUALITÀ) ---")
    device = torch.device("mps")
    
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    # Usiamo bfloat16 per velocità e stabilità su M3
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id, 
        torch_dtype=torch.bfloat16, 
        use_safetensors=True
    ).to(device)

    pipe.safety_checker = None
    pipe.requires_safety_checker = False
    pipe.enable_attention_slicing()

    print("Caricamento pesi Lightning...")
    checkpoint = hf_hub_download("ByteDance/SDXL-Lightning", "sdxl_lightning_4step_unet.safetensors")
    state_dict = load_file(checkpoint, device="cpu")
    pipe.unet.load_state_dict(state_dict)
    pipe.unet.to(device, torch.bfloat16)
    
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    with open(BOOK_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    recipes = data.get("recipes", [])
    
    for r in recipes:
        num = r.get("number")
        title = r.get("title")
        path = os.path.join(IMAGES_DIR, f"recipe_{num}.png")
        
        # NON CANCELLIAMO NULLA: se l'immagine esiste ed è buona, la teniamo
        if os.path.exists(path) and os.path.getsize(path) > 100000: 
            print(f"[{num}] Già presente: {title}")
            continue

        # PROMPT OTTIMIZZATO: focus solo sugli ingredienti, uova bandite
        prompt = (
            f"Gourmet culinary shot of {title}. High-end restaurant plating, "
            f"natural lighting, professional food photography, 8k. "
            f"Focus on fresh herbs and vegetables. NO EGGS, NO YELLOW CIRCLES, NO TEXT."
        )
        # NEGATIVE PROMPT AGGRESSIVO: per uccidere le uova e il testo
        negative_prompt = (
            "eggs, egg yolk, fried egg, boiled egg, yellow circles, omelette, "
            f"text, letters, watermark, blurry, low quality, infographic, cartoon, "
            f"numbers, labels, messy, eggs in background"
        )
        
        print(f"[{num}] Generando (Senza Uova): {title}...")
        start_time = time.time()
        
        try:
            with torch.inference_mode():
                image = pipe(
                    prompt=prompt, 
                    negative_prompt=negative_prompt, 
                    num_inference_steps=4, 
                    guidance_scale=0.0 # Cruciale per Lightning
                ).images[0]
            
            image.save(path)
            elapsed = time.time() - start_time
            print(f"    [OK] {elapsed:.2f}s")
        except Exception as e:
            print(f"    [ERRORE] {e}")

if __name__ == "__main__":
    main()
