#!/usr/bin/env python3
import base64
import json
import os
import requests
import sys
from datetime import datetime
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
API_BASE = "https://api.minimax.io/v1"
GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "2031978439547822419")

FIFI_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly."""

OLIVER_PROMPT = """A round, fluffy owl with warm tan and brown feathers, big round spectacles 
with gold frames, and a wise tuft of feathers on top of the head. Large expressive 
eyes behind the spectacles. Soft, friendly appearance with rounded features. 
Children's book illustration style."""

SCENE_PROMPT = """Soft children's book watercolor illustration style. Warm color palette — 
oranges, creams, soft greens and blues. Large expressive dark eyes, rounded friendly 
shapes, gentle textures. Child-friendly and cozy. No sharp edges or dark shadows. 
Bright, warm lighting. Suitable for ages 1-5."""

def generate_image(scene_description, character_prompt, page_num, output_path):
    prompt = f"""{character_prompt}

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
        "text": "Fifi the Fox visits Oliver's Library Tree. Oliver the Owl has big colorful letter cards. 'Welcome, little fox! Today we learn our ABCs!'",
        "scene": "Inside a cozy tree trunk library. A cute baby red fox and a wise owl with spectacles sit among many colorful books. Warm golden light. Soft watercolor style.",
        "character": FIFI_PROMPT
    },
    {
        "text": "'A is for Acorn!' says Oliver, pointing to a big brown acorn. 'B is for Butterfly!' Fifi flaps her tiny paws like wings.",
        "scene": "A cute red fox and an owl with spectacles looking at letter cards. An acorn and a colorful butterfly appear in magical sparkles around them. Warm storybook style.",
        "character": FIFI_PROMPT
    },
    {
        "text": "'C is for Caterpillar!' chirps Fifi. 'D is for Duck!' quacks Oliver. They wiggle and waddle, laughing with joy.",
        "scene": "A playful red fox and a spectacled owl acting out letters C and D. A green caterpillar and a yellow duck float nearby in magical sparkles. Cozy children's book illustration.",
        "character": FIFI_PROMPT
    },
    {
        "text": "'E is for Elephant!' rumbles Oliver. 'F is for Flower!' giggles Fifi. They stomp and smell the pretty petals.",
        "scene": "A red fox and an owl playing with letters E and F. A cute small elephant and a pink flower appear in golden sparkles. Warm, soft watercolor illustration.",
        "character": FIFI_PROMPT
    },
    {
        "text": "'G is for Goat!' says Fifi. 'H is for House!' adds Oliver. They pretend to climb and build with happy smiles.",
        "scene": "A red fox and an owl with spectacles having fun with letters G and H. A friendly goat and a cozy cottage appear in magical sparkles. Warm children's book style.",
        "character": FIFI_PROMPT
    },
    {
        "text": "Oliver and Fifi sing their ABCs together. 'A, B, C, D, E, F, G, H!' they cheer. Learning letters is the best adventure!",
        "scene": "A happy red fox and a wise owl celebrating with big smiles. Colorful letter cards float around them like magic. Warm golden light. Soft cozy storybook illustration.",
        "character": FIFI_PROMPT
    }
]

book_dir = Path("books/fifi-abc")
images_dir = book_dir / "images"
book_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

print("Generating Book 6: ABCs with Fifi and Oliver")
for i, page in enumerate(pages, 1):
    img_path = images_dir / f"page-{i}.png"
    print(f"  Page {i}: {page['text'][:50]}...")
    try:
        generate_image(page["scene"], page["character"], i, img_path)
        page["image"] = f"images/page-{i}.png"
        print(f"    Image saved: page-{i}.png")
    except Exception as e:
        print(f"    Failed: {e}")
        page["image"] = None

book_data = {
    "id": "fifi-abc",
    "title": "ABCs with Fifi and Oliver",
    "description": "Join Fifi the Fox and Oliver the Owl on an alphabet adventure in Oliver's magical library tree!",
    "coverColor": "e67e22",
    "coverEmoji": "🦊",
    "pages": pages,
    "metadata": {
        "mainCharacter": "Fifi the Fox",
        "sideCharacters": ["Oliver the Owl"],
        "theme": "alphabet",
        "targetAge": "3-5",
        "wordCount": sum(len(p["text"].split()) for p in pages),
        "generatedAt": datetime.utcnow().isoformat()
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

print(f"Book saved to {book_dir}")