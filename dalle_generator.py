import os
import json
import time
import requests
from openai import OpenAI
from pathlib import Path

# Load .env file if present
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.getenv("OPENAI_API_KEY", "")
if not API_KEY or API_KEY.startswith("INCOLLA"):
    raise SystemExit("❌ Chiave mancante. Modifica il file .env e incolla la tua OPENAI_API_KEY.")

client = OpenAI(api_key=API_KEY)

BOOK_JSON_PATH = "work/book.json"
IMAGES_DIR = "images"

# Every prompt must obey these rules — baked into the suffix AND the opening line
STYLE_SUFFIX = (
    "Strict 90-degree top-down overhead flat lay. "
    "FULL PLATE completely visible within frame, wide shot, entire dish from edge to edge. "
    "ONE single plate or bowl centered with empty space around all sides. "
    "Hyper-realistic professional food photography, Hasselblad quality, ultra-sharp, 8K. "
    "Soft diffused natural daylight from above. Clean white marble surface. "
    "Vibrant colors, photorealistic textures, perfect exposure. "
    "No text, no labels, no watermarks, no people, no hands, no extra dishes, no cutlery."
)


def build_prompt(recipe: dict) -> str:
    n = recipe["number"]

    # shared opener enforced on every recipe
    def shot(description: str) -> str:
        return (
            f"Top-down overhead flat lay of ONE single plate: {description} "
            + STYLE_SUFFIX
        )

    # ── CHAPTER 2: Low-Carb Breakfasts (1-14) ──────────────────────────────
    if n == 1:
        return shot(
            "six golden-brown mini egg muffins in a white ceramic dish, "
            "filled with vibrant green spinach, red bell pepper, melted cheddar, steam rising"
        )
    if n == 2:
        return shot(
            "white ceramic bowl of thick Greek yogurt topped with fresh blueberries, "
            "raspberries, sliced almonds, golden honey drizzle, and chia seeds"
        )
    if n == 3:
        return shot(
            "wide glass jar of overnight chia oats layered with creamy cottage cheese, "
            "topped with fresh blueberries and a cinnamon dusting"
        )
    if n == 4:
        return shot(
            "cast-iron skillet with golden turkey sausage rounds, caramelized orange "
            "sweet potato cubes, wilted kale, fresh parsley garnish"
        )
    if n == 5:
        return shot(
            "white ceramic baking dish of spinach and feta egg bake: golden set custard "
            "with deep green spinach, crumbled white feta, fresh dill on top"
        )
    if n == 6:
        return shot(
            "white plate with two slices of low-carb toast topped with thick cottage cheese, "
            "thin smoked salmon, capers, red onion slivers, fresh dill, lemon wedge"
        )
    if n == 7:
        return shot(
            "white bowl of fully-cooked breakfast scramble: vibrant red, yellow, orange "
            "bell pepper strips folded with creamy scrambled eggs, fresh cilantro on top, "
            "NO runny yolks, NO raw eggs"
        )
    if n == 8:
        return shot(
            "white plate with a stack of three fluffy golden protein pancakes, "
            "topped with fresh banana slices, blueberries, light maple syrup drizzle"
        )
    if n == 9:
        return shot(
            "white bowl of fluffy cottage cheese topped with fresh pineapple chunks, "
            "toasted coconut flakes, mint leaf"
        )
    if n == 10:
        return shot(
            "white rectangular baking dish with breakfast casserole: sliced turkey sausage, "
            "diced red peppers, mushrooms set in golden baked egg custard, "
            "melted cheese, parsley garnish"
        )
    if n == 11:
        return shot(
            "glass jar of peanut butter protein overnight oats: peanut butter swirl on top, "
            "dark chocolate chips, sliced banana, chia seeds"
        )
    if n == 12:
        return shot(
            "cast-iron skillet with golden frittata loaded with cherry tomatoes, "
            "fresh spinach, melted cheese, sliced into wedges, fresh basil garnish"
        )
    if n == 13:
        return shot(
            "white bowl of banana protein smoothie bowl: creamy pale-yellow base, "
            "topped with sliced banana, granola, blueberries, peanut butter drizzle"
        )
    if n == 14:
        return shot(
            "white bowl of creamy cottage cheese scrambled eggs: FULLY COOKED fluffy eggs, "
            "no runny yolks, garnished with fresh chives, cracked pepper, cherry tomatoes"
        )

    # ── CHAPTER 3: Low-Carb Lunches (15-29) ───────────────────────────────
    if n == 15:
        return shot(
            "white bowl with Greek chicken prep bowl: sliced grilled chicken breast, "
            "cauliflower rice, cucumber, cherry tomatoes, kalamata olives, tzatziki dollop"
        )
    if n == 16:
        return shot(
            "white plate with butter lettuce cups filled with chipotle ground turkey, "
            "diced red bell peppers, avocado crema drizzle, fresh cilantro"
        )
    if n == 17:
        return shot(
            "white plate with tuna and mushroom salad: flaked tuna, sliced mushrooms, "
            "mixed greens, cherry tomatoes, lemon vinaigrette drizzle"
        )
    if n == 18:
        return shot(
            "white plate with seared salmon fillet on mixed arugula, "
            "sliced cucumber, lemon zest, capers, fresh herbs"
        )
    if n == 19:
        return shot(
            "white bowl with chicken Caesar salad: chopped romaine, "
            "grilled chicken chunks, parmesan shavings, Caesar dressing drizzle"
        )
    if n == 20:
        return shot(
            "white bowl with cauliflower rice topped with grilled shrimp, "
            "mango chunks, avocado slices, red cabbage, fresh lime, cilantro"
        )
    if n == 21:
        return shot(
            "white plate with butter lettuce cups filled with creamy egg salad: "
            "chopped hard-boiled eggs, celery, Dijon, chives, paprika dusting"
        )
    if n == 22:
        return shot(
            "white plate with romaine lettuce leaves filled with egg salad, "
            "garnished with paprika, fresh chives, avocado slices alongside"
        )
    if n == 23:
        return shot(
            "white bowl power bowl with roasted walnuts, roasted zucchini, "
            "bell peppers, red onion, fresh arugula, avocado fan, balsamic glaze"
        )
    if n == 24:
        return shot(
            "white plate with green butter lettuce cups filled with shredded buffalo chicken, "
            "blue cheese dressing drizzle, celery pieces, hot sauce"
        )
    if n == 25:
        return shot(
            "white bowl with zucchini noodles topped with flaked tuna, "
            "cherry tomatoes, fresh basil, lemon zest, olive oil drizzle"
        )
    if n == 26:
        return shot(
            "white plate with two red bell peppers stuffed with seasoned ground turkey "
            "and hemp hearts, fresh parsley garnish"
        )
    if n == 27:
        return shot(
            "white bowl with zucchini noodles topped with sliced grilled chicken, "
            "shredded carrots, cucumber, sesame seeds, peanut sauce drizzle"
        )
    if n == 28:
        return shot(
            "white plate with tuna and mushroom salad: flaked tuna, "
            "sautéed mushrooms, mixed greens, lemon dressing, cracked pepper"
        )
    if n == 29:
        return shot(
            "white bowl with cauliflower rice topped with sliced seared beef, "
            "roasted broccoli, avocado, sesame seeds, soy glaze drizzle"
        )

    # ── CHAPTER 4: Lean Dinners (30-61) ───────────────────────────────────
    if n == 30:
        return shot(
            "white plate with butter lettuce cups filled with sliced grilled chicken "
            "and avocado, lime crema drizzle, fresh cilantro, red chili flakes"
        )
    if n == 31:
        return shot(
            "white bowl with mushroom and veggie salad: baby spinach, roasted mushrooms, "
            "cherry tomatoes, cucumbers, vinaigrette"
        )
    if n == 32:
        return shot(
            "dark bowl with cauliflower rice topped with teriyaki glazed chicken strips, "
            "edamame, purple cabbage, sesame seeds, green onions"
        )
    if n == 33:
        return shot(
            "white plate with shrimp and avocado salad: plump shrimp, "
            "diced avocado, cherry tomatoes, red onion, lime dressing, cilantro"
        )
    if n == 34:
        return shot(
            "white plate with Greek turkey meatballs in tomato sauce, "
            "tzatziki drizzle, fresh dill, cucumber slices"
        )
    if n == 35:
        return shot(
            "white plate with cauliflower rice paper rolls filled with salmon and cucumber, "
            "sliced to show filling, sesame seeds, soy dipping sauce alongside"
        )
    if n == 36:
        return shot(
            "sheet pan with golden garlic butter salmon fillet, "
            "roasted asparagus, lemon slices, fresh dill, capers"
        )
    if n == 37:
        return shot(
            "white bowl with sliced seared beef, roasted red and yellow peppers, "
            "cauliflower rice, fresh parsley, chili drizzle"
        )
    if n == 38:
        return shot(
            "white plate with Mediterranean turkey meatballs, tzatziki sauce, "
            "sliced cucumber, cherry tomatoes, fresh mint"
        )
    if n == 39:
        return shot(
            "deep white bowl with chicken and mushroom stew: tender chicken, "
            "sliced mushrooms, herb broth, fresh thyme"
        )
    if n == 40:
        return shot(
            "sheet pan with golden chicken thighs and roasted asparagus, "
            "lemon slices, garlic, fresh rosemary, caramelized edges"
        )
    if n == 41:
        return shot(
            "white plate with two bell peppers stuffed with seasoned ground turkey, "
            "melted cheese on top, fresh parsley"
        )
    if n == 42:
        return shot(
            "deep white bowl with beef and mushroom stew: tender beef chunks, "
            "sliced mushrooms, dark rich broth, fresh thyme"
        )
    if n == 43:
        return shot(
            "white skillet with creamy Tuscan chicken: golden chicken breast in "
            "sun-dried tomato cream sauce, fresh spinach, parmesan, basil"
        )
    if n == 44:
        return shot(
            "white bowl of smoky beef chili with diced bell peppers, "
            "ground beef, tomatoes, jalapeño, sour cream dollop, cilantro"
        )
    if n == 45:
        return shot(
            "dark bowl with cauliflower rice topped with teriyaki glazed salmon, "
            "edamame, sesame seeds, pickled ginger, green onions"
        )
    if n == 46:
        return shot(
            "white baking dish with herb-crusted cod fillets, "
            "roasted broccoli florets, lemon slices, fresh parsley"
        )
    if n == 47:
        return shot(
            "white bowl with chicken and broccoli stir-fry: tender chicken strips, "
            "bright green broccoli, soy ginger sauce, sesame seeds, cauliflower rice base"
        )
    if n == 48:
        return shot(
            "white plate with sliced pork tenderloin medallions, "
            "caramelized apple slices, Dijon sauce, fresh thyme, roasted vegetables"
        )
    if n == 49:
        return shot(
            "white bowl with ground turkey taco filling, shredded purple cabbage, "
            "pico de gallo, avocado slices, lime, cilantro"
        )
    if n == 50:
        return shot(
            "white plate with garlic butter shrimp on zucchini noodles, "
            "cherry tomatoes, fresh parsley, lemon zest"
        )
    if n == 51:
        return shot(
            "white baking dish with honey mustard chicken thighs, "
            "caramelized golden glaze, roasted vegetables, fresh rosemary"
        )
    if n == 52:
        return shot(
            "dark bowl with beef and broccoli on cauliflower rice: "
            "tender beef slices, bright broccoli, savory brown sauce, sesame seeds"
        )
    if n == 53:
        return shot(
            "white plate with sliced baked turkey meatloaf, "
            "tomato glaze on top, roasted green beans, fresh parsley"
        )
    if n == 54:
        return shot(
            "sheet pan with golden salmon fillet and roasted sweet potato wedges, "
            "asparagus, lemon slices, dill"
        )
    if n == 55:
        return shot(
            "white skillet with tikka-style chicken: golden chicken pieces in vibrant "
            "orange-red spiced tomato sauce, fresh cilantro, yogurt swirl"
        )
    if n == 56:
        return shot(
            "cast-iron skillet with beef taco filling: crumbled ground beef, "
            "diced tomatoes, jalapeño, shredded cheese, cilantro, lime wedge"
        )
    if n == 57:
        return shot(
            "white plate with seared lemon garlic chicken breast, golden crust, "
            "lemon slices, fresh thyme, roasted green vegetables"
        )
    if n == 58:
        return shot(
            "white bowl with shrimp and cauliflower rice stir-fry: plump pink shrimp, "
            "snap peas, soy sesame sauce, green onions"
        )
    if n == 59:
        return shot(
            "white bowl with turkey bolognese on zucchini noodles: "
            "rich tomato meat sauce, fresh basil, parmesan, spiralized zucchini"
        )
    if n == 60:
        return shot(
            "deep white bowl of slow cooker beef and mushroom stew: "
            "tender beef chunks, mushrooms, carrots, dark rich broth, fresh thyme"
        )
    if n == 61:
        return shot(
            "white plate with golden Greek chicken thighs, kalamata olives, "
            "cherry tomatoes, fresh oregano, lemon slices, crumbled feta"
        )

    # ── CHAPTER 5: Snacks (62-75) ─────────────────────────────────────────
    if n == 62:
        return shot(
            "white plate with bite-sized peanut butter protein balls coated in "
            "dark chocolate chips and oats, dusted with cocoa powder"
        )
    if n == 63:
        return shot(
            "white plate with halved hard-boiled eggs (yolk FULLY set, firm, no runny yolk), "
            "sliced avocado fan, sea salt flakes, everything bagel seasoning"
        )
    if n == 64:
        return shot(
            "white plate with turkey slices rolled around hummus, "
            "sliced cucumber and bell pepper sticks neatly arranged"
        )
    if n == 65:
        return shot(
            "white bowl with thick cottage cheese dip, sliced cucumbers, "
            "fresh dill, cracked pepper, olive oil drizzle"
        )
    if n == 66:
        return shot(
            "white bowl with creamy Greek yogurt ranch dip surrounded by "
            "colorful raw vegetable sticks: carrots, celery, cucumber, bell pepper"
        )
    if n == 67:
        return shot(
            "white plate with mini sweet peppers halved and filled with tuna salad, "
            "garnished with capers, fresh dill"
        )
    if n == 68:
        return shot(
            "white bowl overflowing with bright green steamed edamame pods, "
            "flaky sea salt, sesame seeds"
        )
    if n == 69:
        return shot(
            "white plate with snack arrangement: whole almonds, "
            "string cheese pieces, apple slices, simple and elegant"
        )
    if n == 70:
        return shot(
            "white plate with smoked salmon rosettes on cucumber rounds, "
            "cream cheese, capers, fresh dill, lemon zest"
        )
    if n == 71:
        return shot(
            "white bowl with golden roasted walnut halves, "
            "lightly salted, fresh rosemary sprig"
        )
    if n == 72:
        return shot(
            "white plate with two slices of low-carb toast topped with cottage cheese, "
            "sliced cherry tomatoes, fresh basil, olive oil drizzle"
        )
    if n == 73:
        return shot(
            "white plate with turkey and cheese roll-ups sliced into pinwheels, "
            "showing turkey and melted cheese inside, mustard dipping sauce"
        )
    if n == 74:
        return shot(
            "white bowl of thick Greek yogurt, golden honey drizzle, "
            "walnut halves, fresh berries"
        )
    if n == 75:
        return shot(
            "white bowl with protein trail mix: mixed nuts, dark chocolate chips, "
            "pumpkin seeds, dried cranberries"
        )

    # ── CHAPTER 6: Soups & Stews (76-88) ──────────────────────────────────
    if n == 76:
        return shot(
            "deep white bowl of chicken zucchini noodle soup: clear broth, "
            "shredded chicken, zucchini noodles, carrot rounds, fresh parsley, steam"
        )
    if n == 77:
        return shot(
            "white bowl of turkey mushroom kale soup: amber broth, "
            "ground turkey, sliced mushrooms, dark leafy kale"
        )
    if n == 78:
        return shot(
            "dark bowl of spicy beef and mushroom stew: thick rich broth, "
            "tender beef, mushrooms, chili flakes, fresh parsley"
        )
    if n == 79:
        return shot(
            "white bowl of creamy broccoli cheddar soup: "
            "vibrant green broccoli florets, melted cheddar swirl, croutons"
        )
    if n == 80:
        return shot(
            "white bowl of shrimp corn chowder: plump pink shrimp, corn kernels, "
            "cream broth, fresh chives, paprika"
        )
    if n == 81:
        return shot(
            "deep white bowl of smoky chicken and walnut stew: "
            "shredded chicken, tomatoes, roasted walnuts, smoked paprika oil"
        )
    if n == 82:
        return shot(
            "wide white bowl of beef and vegetable minestrone: "
            "rich tomato broth, beef, zucchini, carrots, celery, fresh basil"
        )
    if n == 83:
        return shot(
            "white bowl of turkey and sweet potato chili: orange sweet potato cubes, "
            "ground turkey, tomatoes, cilantro, sour cream dollop"
        )
    if n == 84:
        return shot(
            "white bowl of salmon and potato chowder: salmon chunks, "
            "potato cubes, leeks, cream broth, fresh dill"
        )
    if n == 85:
        return shot(
            "white bowl of mushroom and spinach soup: dark earthy mushrooms, "
            "wilted spinach, clear herb broth, fresh thyme"
        )
    if n == 86:
        return shot(
            "white bowl of chicken lettuce soup: clear broth, shredded chicken, "
            "butter lettuce, mushrooms, green onions, sesame oil swirl"
        )
    if n == 87:
        return shot(
            "white bowl of beef and bell pepper soup: diced beef, "
            "colorful pepper chunks, tomato broth, fresh parsley"
        )
    if n == 88:
        return shot(
            "white bowl of creamy chicken and mushroom soup: tender chicken, "
            "sliced cremini mushrooms, cream base, fresh thyme"
        )

    # ── CHAPTER 7: Protein Treats (89-96) ─────────────────────────────────
    if n == 89:
        return shot(
            "white plate with dark chocolate peanut butter protein fudge squares "
            "on parchment, crushed peanuts, sea salt flakes on top"
        )
    if n == 90:
        return shot(
            "white plate with golden lemon cheesecake protein bars, "
            "creamy filling visible from side, lemon zest, parchment paper"
        )
    if n == 91:
        return shot(
            "white plate with frozen Greek yogurt bark broken into shards, "
            "mixed berries, granola, honey drizzle on top"
        )
    if n == 92:
        return shot(
            "dark elegant glass with creamy cottage cheese chocolate mousse, "
            "dusted with cocoa powder, dark chocolate shavings"
        )
    if n == 93:
        return shot(
            "white ceramic mug with freshly baked banana protein mug cake, "
            "fluffy texture, banana slices on top, cinnamon dusting"
        )
    if n == 94:
        return shot(
            "white plate with golden peanut butter protein cookies, "
            "fork-pressed pattern, dark chocolate chips"
        )
    if n == 95:
        return shot(
            "white plate with chocolate protein energy bites coated in cocoa, "
            "cacao nibs scattered, light icing sugar dust"
        )
    if n == 96:
        return shot(
            "glass with vanilla cottage cheese parfait layers: "
            "creamy white cottage cheese, granola, fresh berries, honey drizzle"
        )

    # ── CHAPTER 8: Sauces (97-102) ────────────────────────────────────────
    if n == 97:
        return shot(
            "small glass jar of chipotle lime marinade: vibrant orange-red sauce, "
            "lime slices beside, fresh cilantro, chili pepper"
        )
    if n == 98:
        return shot(
            "white ceramic bowl of fresh tzatziki: thick Greek yogurt, "
            "cucumber, fresh dill, olive oil drizzle, cracked pepper"
        )
    if n == 99:
        return shot(
            "small jar of creamy Caesar dressing: pale yellow, "
            "garlic, lemon zest, parmesan visible, dark background"
        )
    if n == 100:
        return shot(
            "small white bowl of lemon garlic herb sauce: bright green herbs, "
            "parsley, basil, lemon zest, olive oil"
        )
    if n == 101:
        return shot(
            "small white bowl of creamy peanut sauce: smooth with swirl pattern, "
            "crushed peanuts on top, lime wedge, ginger"
        )
    if n == 102:
        return shot(
            "white bowl of avocado lime crema: smooth bright green sauce, "
            "lime zest, cilantro, jalapeño slice"
        )
    if n == 103:
        return shot(
            "white plate with Greek grilled chicken souvlaki: golden char-grilled "
            "chicken pieces, tzatziki, cherry tomatoes, cucumber, fresh oregano, lemon wedge"
        )

    # ── FALLBACK ───────────────────────────────────────────────────────────
    title = recipe["title"]
    return shot(f"elegant serving of {title}, beautifully plated, fresh herb garnish")


def main():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    with open(BOOK_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipes = data.get("recipes", [])
    to_generate = []

    for recipe in recipes:
        number = recipe.get("number")
        img_path = os.path.join(IMAGES_DIR, f"recipe_{number}.png")
        if os.path.exists(img_path) and os.path.getsize(img_path) > 150_000:
            print(f"[{number:03d}] ✓ Già presente: {recipe['title']}")
        else:
            to_generate.append(recipe)

    print(f"\nDa generare: {len(to_generate)} immagini\n")

    for recipe in to_generate:
        number = recipe["number"]
        title = recipe["title"]
        img_path = os.path.join(IMAGES_DIR, f"recipe_{number}.png")

        prompt = build_prompt(recipe)

        print(f"[{number:03d}] Generando: {title}")

        for attempt in range(3):
            try:
                import base64
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1792x1024",
                    quality="hd",
                    response_format="b64_json",
                    n=1,
                )

                image_b64 = response.data[0].b64_json
                image_bytes = base64.b64decode(image_b64)

                with open(img_path, "wb") as img_file:
                    img_file.write(image_bytes)

                size_kb = os.path.getsize(img_path) // 1024
                print(f"       ✓ Salvata ({size_kb} KB)")
                time.sleep(6)
                break

            except Exception as e:
                error_msg = str(e).lower()
                print(f"       ✗ Tentativo {attempt+1}/3: {e}")
                if "rate_limit" in error_msg or "429" in error_msg:
                    wait = 60 * (attempt + 1)
                    print(f"       Rate limit — aspetto {wait}s...")
                    time.sleep(wait)
                elif "content_policy" in error_msg or "safety" in error_msg:
                    print(f"       Content policy — salto.")
                    break
                else:
                    time.sleep(15)
        else:
            print(f"       ✗ Fallita dopo 3 tentativi: {title}")

    print("\n=== COMPLETATO ===")
    existing = sum(
        1 for r in recipes
        if os.path.exists(os.path.join(IMAGES_DIR, f"recipe_{r['number']}.png"))
        and os.path.getsize(os.path.join(IMAGES_DIR, f"recipe_{r['number']}.png")) > 150_000
    )
    print(f"Immagini valide: {existing}/{len(recipes)}")


if __name__ == "__main__":
    main()
