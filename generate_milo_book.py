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

MILO_PROMPT = """A tiny brown field mouse with big round ears and bright nervous eyes. 
Small and delicate with a brown #A0785A fur coat and cream #F5DEB3 belly. 
Children's book illustration style. Warm colors, soft edges, adorable and timid. 
The mouse should look small but sweet. NO TEXT OR WORDS IN IMAGE."""

SCENE_PROMPT = """Children's book illustration with soft colors and gentle shapes. 
A small red fox and a tiny mouse are together in a forest setting near a tree stump.
Warm, friendly, and engaging scene suitable for ages 1-5. NO TEXT OR WORDS IN IMAGE."""

def generate_image(prompt, page_num, output_path):
    full_prompt = f"""{prompt}

Page {page_num} illustration. Style: Warm, colorful children's book illustration 
with soft edges, friendly characters, and engaging backgrounds. Suitable for ages 1-5."""
    
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

def create_milo_book():
    book_id = "fifi-milo"
    book_dir = Path(f"books/{book_id}")
    images_dir = book_dir / "images"
    book_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    pages_text = [
        "En dag hittade Fifi en liten mus nära en gammal trädstubbe. 'Vem är du?' frågade Fifi vänligt. 'Jag är Milo,' sa musen med darrande röst. 'Jag är vilse.'",
        "Fifi såg att Milo var väldigt liten och nervös. 'Var inte rädd,' sa Fifi och log varmt. 'Jag ska hjälpa dig hitta hem!'",
        "Milo berättade att hans hus var under den stora eken. Fifi lyssnade noga och nickade. 'Jag känner den eken! Det är inte långt härifrån.'",
        "Tillsammans gick de genom skogen. Milo var liten så Fifi gick långsamt. 'Tack för att du är så snäll,' viskade Milo.",
        "Plötsligt hittade de den stora eken. Under roten syntes ett litet musbo! 'Här är ditt hem!' ropade Fifi glatt.",
        "Milo log brett för första gången. 'Tack, Fifi! Du är en underbar vän.' De gav varandra en liten kram.",
        "Fifi vinkade hejdå och gick hem med en varm känsla i hjärtat. Att hjälpa nya vänner var det bästa som fanns!"
    ]
    
    scene_prompts = [
        "Cute red fox finding a tiny nervous mouse near a tree stump in a forest, friendly introduction scene",
        "Fifi the fox looking gently at a tiny scared mouse, warm and reassuring expression, forest background",
        "Fifi listening attentively while the tiny mouse Milo explains where his home is, kind and patient expression",
        "Fifi and Milo walking together through the forest, Fifi going slowly to match Milo's small steps, friendship scene",
        "Fifi and Milo arriving at a big oak tree with a small mouse hole visible at the roots, happy discovery",
        "Tiny Milo mouse smiling broadly for the first time, giving Fifi a small hug, grateful friendship moment",
        "Fifi the fox waving goodbye to Milo the mouse, warm sunset light, walking home with happy expression"
    ]
    
    pages = []
    for i, (text, scene) in enumerate(zip(pages_text, scene_prompts), 1):
        img_path = images_dir / f"page-{i}.png"
        print(f"  Page {i}...")
        try:
            prompt = f"""{FIFI_PROMPT}

{MILO_PROMPT}

{SCENE_PROMPT}

Scene details: {scene}"""
            generate_image(prompt, i, img_path)
        except Exception as e:
            print(f"    Failed: {e}")
            continue
        pages.append({"text": text, "image": f"images/page-{i}.png", "audio": None, "video": None})
    
    book_data = {
        "id": book_id,
        "title": "Fifi träffar Milo",
        "description": "Fifi hittar en liten vilsekommen mus som heter Milo. Med tålamod och vänlighet hjälper Fifi honom hitta hem.",
        "coverColor": "E67E22",
        "coverEmoji": "🦊",
        "pages": pages,
        "metadata": {
            "mainCharacter": "Fifi the Fox",
            "sideCharacters": ["Milo the Mouse"],
            "theme": "new-friends",
            "targetAge": "3-5",
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
    print("Generating: Fifi träffar Milo (Book 9)")
    book = create_milo_book()
    print(f"\nDone! Generated {len(book['pages'])} pages")
    print(f"Book saved to: books/{book['id']}/")