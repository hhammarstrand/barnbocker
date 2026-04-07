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
NO TEXT OR WORDS IN IMAGE."""

BELLA_PROMPT = """A small pale-grey rabbit with long ears, fluffy white tail, pink inner ears.
Children's book illustration style. Warm colors, soft edges, sweet and shy expression.
NO TEXT OR WORDS IN IMAGE."""

OLIVER_PROMPT = """A round, fluffy owl with warm tan/brown feathers, big round spectacles with gold frames.
Children's book illustration style. Warm colors, soft edges, wise and friendly expression.
NO TEXT OR WORDS IN IMAGE."""

MILO_PROMPT = """A tiny brown field mouse with big round ears and bright eyes. Small and adorable.
Children's book illustration style. Warm colors, soft edges, sweet expression.
NO TEXT OR WORDS IN IMAGE."""

SCENE_PROMPT = """Children's book illustration with soft colors and gentle shapes. Multiple animal characters 
celebrating together in a forest clearing. Warm, friendly, and engaging scene suitable for ages 1-5. 
NO TEXT OR WORDS IN IMAGE."""

def generate_image(prompt, page_num, output_path):
    full_prompt = f"""{prompt}

Page {page_num} illustration. Style: Warm, colorful children's book illustration 
with soft edges, friendly characters, and engaging backgrounds. Suitable for ages 1-5."""
    
    response = requests.post(
        f"{API_BASE}/image_generation",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "image-01", "prompt": full_prompt},
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

def create_thankyou_book():
    book_id = "fifi-thankyou"
    book_dir = Path(f"books/{book_id}")
    images_dir = book_dir / "images"
    book_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    pages_text = [
        "Fifi vaknade en morgon och tänkte på alla sina vänner. Bruno hade burit henne över floden. Bella hade delat sina karotter. Oliver hade lärt henne bokstäver. Och Milo... Milo hade gett henne en glädje i hjärtat.",
        "'Jag vill säga tack till alla!' sa Fifi glatt. Hon packade en liten korg med blommor och började sin resa.",
        "Först kom Fifi till Brunos koja. 'Tack för att du bar mig över floden!' sa Fifi och gav Bruno en stor kram och en gul blomma.",
        "Sedan besökte Fifi Bella vid hennes hus. 'Tack för att du delade dina karotter!' sa Fifi och gav Bella en ros och en kram.",
        "Oliver satt i sitt biblioteksträd och läste. 'Tack för att du lärde mig bokstäver!' sa Fifi och gav Oliver en vacker fjäder.",
        "Till slut hittade Fifi Milo i skogen. 'Tack för att du var en så fin vän!' sa Fifi och de gav varandra en värmekram.",
        "Alla Fifi:s vänner samlades i skogen och hade en liten fest. 'Tack för att ni finns!' sa Fifi. 'Att säga tack visar att man bryr sig!'"
    ]
    
    scene_prompts = [
        "Fifi the fox thinking about her friends with a warm smile, morning sunlight, cozy den interior",
        "Fifi packing a small basket with flowers, preparing to visit friends, excited expression",
        "Fifi hugging a large brown bear and giving him a yellow flower in front of his cozy cabin",
        "Fifi hugging a small grey bunny and giving her a beautiful rose near her rabbit house",
        "Fifi giving a wise owl with spectacles a beautiful feather in his library tree, grateful scene",
        "Fifi hugging a tiny mouse in the forest, warm friendship moment, golden afternoon light",
        "All of Fifi's friends (bear, bunny, owl, mouse) gathering in a forest clearing for a small celebration, group hug scene"
    ]
    
    pages = []
    for i, (text, scene) in enumerate(zip(pages_text, scene_prompts), 1):
        img_path = images_dir / f"page-{i}.png"
        print(f"  Page {i}...")
        try:
            prompt = f"""{FIFI_PROMPT}

{SCENE_PROMPT}

Scene details: {scene}"""
            generate_image(prompt, i, img_path)
        except Exception as e:
            print(f"    Failed: {e}")
            continue
        pages.append({"text": text, "image": f"images/page-{i}.png", "audio": None, "video": None})
    
    book_data = {
        "id": book_id,
        "title": "Fifi säger tack",
        "description": "Fifi tackar alla sina vänner för deras hjälpsamhet och vänskap. En varm historia om tacksamhet.",
        "coverColor": "E67E22",
        "coverEmoji": "🦊",
        "pages": pages,
        "metadata": {
            "mainCharacter": "Fifi the Fox",
            "sideCharacters": ["Bruno the Bear", "Bella the Bunny", "Oliver the Owl", "Milo the Mouse"],
            "theme": "gratitude",
            "targetAge": "2-5",
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
    print("Generating: Fifi säger tack (Book 10)")
    book = create_thankyou_book()
    print(f"\nDone! Generated {len(book['pages'])} pages")
    print(f"Book saved to: books/{book['id']}/")