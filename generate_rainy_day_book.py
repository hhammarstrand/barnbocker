#!/usr/bin/env python3
import json
import os
import requests
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
API_BASE = "https://api.minimax.io/v1"

FIFI_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. NO TEXT OR WORDS IN IMAGE."""

BRUNO_PROMPT = """A large, warm brown bear with round belly, soft fur, and a kind smile.
Children's book illustration style. Warm colors, soft edges, friendly and approachable.
The bear should look gentle and caring. NO TEXT OR WORDS IN IMAGE."""

RAINY_SCENE_PROMPT = """Cozy indoor scene with a warm, cozy den interior. A small red fox and a large friendly bear
are playing together inside. Soft blankets, pillows, and toys scattered around. A window shows rain falling outside.
Warm golden light inside, soft grey rain visible through the window. Children's book illustration
style with soft colors and gentle shapes. NO TEXT OR WORDS IN IMAGE."""

def generate_image(prompt, page_num, output_path):
    full_prompt = f"""{prompt}

Children's book illustration for page {page_num}.

Style: Warm, colorful children's book illustration with soft edges, friendly characters, and engaging backgrounds. Suitable for ages 1-5."""
    
    response = requests.post(
        f"{API_BASE}/image_generation",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "image-02", "prompt": full_prompt},
        timeout=180
    )
    response.raise_for_status()
    result = response.json()
    image_url = result["data"]["image_urls"][0]

    img_response = requests.get(image_url)
    img_response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(img_response.content)
    return True

def create_rainy_day_book():
    book_id = "fifi-rainy-day"
    book_dir = Path(f"books/{book_id}")
    images_dir = book_dir / "images"
    book_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    pages_text = [
        "Fifi vaknade en regnig morgon och tittade ut genom fönstret. Dropparna föll från himlen och Fifi suckade: 'Jag vill gå ut och leka!'",
        "Molly mos och undrade vad hon skulle göra på hela dagen. Hon var så uttråkad utan sina vänner.",
        "PLÖTSLIGEN hörde Fifi en dunk på dörren. Det var Bruno björnen! 'Får jag komma in?' frågade han glatt.",
        "'Ja, ja, kom in!' ropade Fifi och hennes ögon lyste upp. Bruno hade en stor kartong med täcka och kuddar!",
        "Tillsammans byggde de en mysig fort i vardagsrummet. 'Nu har vi vårt eget litet hus!' sa Fifi glatt.",
        "De ritade fina bilder, lagade leksaksmat i köket och hade jättekul. Regnet utanför gjorde ingenting!",
        "Till slut somnade Fifi och Bruno i sin mjuka fort, trötta men glada. 'Regniga dagar är magiska!' viskade Fifi."
    ]
    
    scene_prompts = [
        "Sad little fox cub looking out a window at rain, bored expression, cozy den interior with soft morning light",
        "Fifi the fox looking bored and restless in her cozy den, toys scattered around, window showing rainy weather",
        "Friendly large brown bear standing at a wooden door with a cardboard box, cheerful expression, rainy day outside",
        "Happy Fifi the fox welcoming Bruno the bear inside, both looking excited and friendly, cozy home interior",
        "Fifi the fox and Bruno the bear building a blanket fort together, using pillows and blankets, joyful expressions",
        "Fifi and Bruno playing inside their blanket fort, drawing pictures and playing pretend cooking, warm happy scene",
        "Fifi and Bruno sleeping peacefully in their cozy blanket fort, peaceful happy expressions, rain visible through window"
    ]
    
    pages = []
    for i, (text, scene) in enumerate(zip(pages_text, scene_prompts), 1):
        img_path = images_dir / f"page-{i}.png"
        print(f"  Page {i}...")
        try:
            prompt = f"""{FIFI_PROMPT}

{RAINY_SCENE_PROMPT}

Additional scene details: {scene}"""
            generate_image(prompt, i, img_path)
        except Exception as e:
            print(f"    Failed: {e}")
            continue
        pages.append({"text": text, "image": f"images/page-{i}.png", "audio": None, "video": None})
    
    book_data = {
        "id": book_id,
        "title": "Fifi och den magiska regndagen",
        "description": "En regnig dag blir magisk när Bruno björnen kommer på besök! Fifi och Bruno hittar på underbara inomhuslekar.",
        "coverColor": "E67E22",
        "coverEmoji": "🦊",
        "pages": pages,
        "metadata": {
            "mainCharacter": "Fifi the Fox",
            "sideCharacters": ["Bruno the Bear"],
            "theme": "rainy-day",
            "targetAge": "2-4",
            "wordCount": sum(len(p.split()) for p in pages_text),
            "generatedAt": datetime.utcnow().isoformat()
        }
    }
    
    with open(book_dir / "book.json", "w") as f:
        json.dump(book_data, f, indent=2)
    
    meta = {
        "id": book_id,
        "title": book_data["title"],
        "description": book_data["description"],
        "pageCount": len(pages),
        "coverColor": book_data["coverColor"],
        "coverEmoji": book_data["coverEmoji"]
    }
    with open(book_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    
    return book_data

if __name__ == "__main__":
    print("Generating: Fifi och den magiska regndagen (Book 8)")
    book = create_rainy_day_book()
    print(f"\nDone! Generated {len(book['pages'])} pages")
    print(f"Book saved to: books/{book['id']}/")