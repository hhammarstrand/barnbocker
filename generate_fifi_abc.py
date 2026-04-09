#!/usr/bin/env python3
import json
import os
import requests
from pathlib import Path

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "2031978439547822419")
MINIMAX_API_BASE = "https://api.minimax.io/v1"

headers = {
    "Authorization": f"Bearer {MINIMAX_API_KEY}",
    "Content-Type": "application/json"
}

def generate_text():
    prompt = """Skriv en kort barnbok på svenska för barn 3-5 år om bokstäver och alfabetet.

Huvudkaraktär: Fifi the Fox (nyfiken ung räv)
Bikaraktär: Oliver the Owl (vit uggle med glasögon, väldigt klok)
Setting: Oliver's biblioteksträd (ett stort träd fullt av böcker)

Tema: Fifi och Oliver utforskar alfabetet tillsammans i biblioteksträdet. På varje sida visas några bokstäver med djur eller saker som börjar på dessa bokstäver.

Krav:
- Exakt 8 sidor
- Varje sida: 15-25 ord
- Följ storyn: Fifi och Oliver hittar bokstäver i biblioteksträdet
- A-Ö: inkludera många bokstäver från alfabetet (A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, R, S, T, U, V, Z)
- Svensk text, inget engelska
- Varm, lekfull ton

Format ska vara JSON:
{"pages": [{"text": "sidtext här..."}, ...]}

Inga markdown, bara ren JSON."""

    response = requests.post(
        f"{MINIMAX_API_BASE}/text/chatcompletion_v2",
        headers=headers,
        json={
            "model": "MiniMax-M2.7-highspeed",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    response.raise_for_status()
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    
    return json.loads(content.strip())

def generate_image(text, page_num):
    character_prompt = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail.
Standing next to a wise white owl with round glasses and soft brown feathers.

Children's book illustration style. Warm golden light. No text in image."""

    prompt = f"""{character_prompt}

Page {page_num} illustration:
Scene: {text}

Requirements:
- NO text, letters, or numbers of any kind in the image
- Multiple friendly characters interacting
- Rich detailed background with books, leaves, magical forest elements
- Dynamic and lively scene with warmth and wonder
- Soft children's book art style suitable for ages 3-5
- Warm, child-friendly colors"""

    response = requests.post(
        f"{MINIMAX_API_BASE}/image_generation",
        headers=headers,
        json={
            "model": "image-01",
            "prompt": prompt
        },
        timeout=120
    )
    response.raise_for_status()
    result = response.json()
    return result["data"][0]["url"]

def download_file(url, path):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)

def main():
    book_id = "fifi-abc"
    book_dir = Path(f"books/{book_id}")
    images_dir = book_dir / "images"
    
    book_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    print("Generating ABC book text...")
    story_data = generate_text()
    
    for i, page in enumerate(story_data["pages"], 1):
        print(f"  Page {i}: {page['text'][:50]}...")
        page["image"] = None
        page["audio"] = None
        page["video"] = None
        
        try:
            image_url = generate_image(page["text"], i)
            page["image"] = f"images/page-{i}.png"
            download_file(image_url, images_dir / f"page-{i}.png")
            print(f"    Image saved: page-{i}.png")
        except Exception as e:
            print(f"    Image generation failed: {e}")
    
    book_data = {
        "id": book_id,
        "title": "Bokstäver med Fifi och Oliver",
        "description": "Fifi och Oliver utforskar alfabetet i det magiska biblioteksträdet!",
        "coverColor": "E67E22",
        "coverEmoji": "🦊",
        "pages": story_data["pages"],
        "metadata": {
            "mainCharacter": "Fifi the Fox",
            "sideCharacters": ["Oliver the Owl"],
            "theme": "alphabet",
            "targetAge": "3-5",
            "wordCount": sum(len(p["text"].split()) for p in story_data["pages"]),
            "generatedAt": __import__("datetime").datetime.utcnow().isoformat()
        }
    }
    
    with open(book_dir / "book.json", "w") as f:
        json.dump(book_data, f, indent=2, ensure_ascii=False)
    
    meta_data = {
        "id": book_id,
        "title": book_data["title"],
        "description": book_data["description"],
        "pageCount": len(story_data["pages"]),
        "coverColor": book_data["coverColor"],
        "coverEmoji": book_data["coverEmoji"]
    }
    
    with open(book_dir / "meta.json", "w") as f:
        json.dump(meta_data, f, indent=2, ensure_ascii=False)
    
    print(f"Book generated: {book_dir / 'book.json'}")
    return book_data

if __name__ == "__main__":
    main()