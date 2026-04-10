#!/usr/bin/env python3
import base64
import json
import os
import requests
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
API_BASE = "https://api.minimax.io/v1"

FIFI_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly."""

SCENE_PROMPT = """Soft children's book watercolor illustration style. Warm color palette — 
oranges, creams, soft greens and blues. Large expressive dark eyes, rounded friendly 
shapes, gentle textures. Child-friendly and cozy. No sharp edges or dark shadows. 
Bright, warm lighting. Suitable for ages 1-5."""

def generate_image(scene_description, page_num, output_path):
    prompt = f"""{FIFI_PROMPT}

Page {page_num}: {scene_description}

{SCENE_PROMPT}"""

    response = requests.post(
        f"{API_BASE}/image_generation",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "image-02", "prompt": prompt},
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

pages = [
    {
        "text": "Fifi räven hälsar på Oliver ugglan i hans biblioteksträd. Oliver har stora färgglada bokstavskort. 'Välkommen, lilla räven! Idag lär vi oss ABC!'",
        "scene": "Inside a cozy tree trunk library with books everywhere. A cute baby red fox and a wise owl with round spectacles sit together. Warm golden lamplight. Soft watercolor children's book style."
    },
    {
        "text": "'A är för Ekollon!' säger Oliver och pekar på en stor brun ekollon. 'B är för Fjäril!' Fifi flaxar med sina små tassar som vingar.",
        "scene": "A cute red fox and a spectacled owl looking at colorful letter cards. A big brown acorn and a beautiful orange butterfly appear in magical sparkles around them. Warm storybook illustration."
    },
    {
        "text": "'C är för Fjäril!' kvittrar Fifi. 'D är för Anka!' säger Oliver. De vickar och vankar och skrattar av glädje.",
        "scene": "A playful red fox and an owl with spectacles acting out letters C and D. A green caterpillar and a yellow duck float nearby in magical sparkles. Cozy children's book illustration."
    },
    {
        "text": "'E är för Elefant!' mullrar Oliver. 'F är för Blomma!' fnissar Fifi. De stoltserar och doftar på de vackra kronbladen.",
        "scene": "A red fox and an owl playing with letters E and F. A cute small grey elephant and a pink flower appear in golden sparkles. Warm soft watercolor illustration."
    },
    {
        "text": "'G är för Get!' säger Fifi. 'H är för Hus!' lägger Oliver till. De låtsas klättra och bygga med glada leenden.",
        "scene": "A red fox and a spectacled owl having fun with letters G and H. A friendly goat and a cozy cottage appear in magical sparkles. Warm children's book style."
    },
    {
        "text": "Oliver och Fifi sjunger ABC tillsammans. 'A, B, C, D, E, F, G, H!' jublar de. Att lära sig bokstäver är det bästa äventyret!",
        "scene": "A happy red fox and a wise owl celebrating with big smiles. Colorful letter cards float around them like magic. Warm golden light. Soft cozy storybook illustration."
    }
]

book_dir = Path("books/fifi-abc")
images_dir = book_dir / "images"
book_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

print("Generating Swedish ABC Book: ABC med Fifi och Oliver")
for i, page in enumerate(pages, 1):
    img_path = images_dir / f"page-{i}.png"
    print(f"  Page {i}: {page['text'][:50]}...")
    try:
        generate_image(page["scene"], i, img_path)
        page["image"] = f"images/page-{i}.png"
        print(f"    Image saved: page-{i}.png")
    except Exception as e:
        print(f"    Failed: {e}")
        page["image"] = None

book_data = {
    "id": "fifi-abc",
    "title": "ABC med Fifi och Oliver",
    "description": "Häng med Fifi räven och Oliver ugglan på ett alfabet-äventyr i Olivers magiska biblioteksträd!",
    "coverColor": "e67e22",
    "coverEmoji": "🦊",
    "pages": pages,
    "metadata": {
        "mainCharacter": "Fifi the Fox",
        "sideCharacters": ["Oliver the Owl"],
        "theme": "alphabet",
        "targetAge": "3-5",
        "wordCount": sum(len(p["text"].split()) for p in pages),
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }
}

with open(book_dir / "book.json", "w") as f:
    json.dump(book_data, f, indent=2)

meta = {
    "id": "fifi-abc",
    "title": book_data["title"],
    "description": book_data["description"],
    "pageCount": len(pages),
    "coverColor": book_data["coverColor"],
    "coverEmoji": book_data["coverEmoji"]
}
with open(book_dir / "meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print(f"Swedish book saved to {book_dir}")