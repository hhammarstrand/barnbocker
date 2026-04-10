#!/usr/bin/env python3
import json
import os
import time
import requests
from pathlib import Path

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
MINIMAX_API_BASE = "https://api.minimax.io/v1"

headers = {
    "Authorization": f"Bearer {MINIMAX_API_KEY}",
    "Content-Type": "application/json"
}

book_id = "fifi-abc"
book_dir = Path(f"books/{book_id}")
images_dir = book_dir / "images"

with open(book_dir / "book.json") as f:
    book_data = json.load(f)

def generate_image(text, page_num, retries=3):
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

    for attempt in range(retries):
        try:
            response = requests.post(
                f"{MINIMAX_API_BASE}/image_generation",
                headers=headers,
                json={
                    "model": "image-02",
                    "prompt": prompt
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            image_url = result["data"]["image_urls"][0]
            return image_url
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return None

def download_file(url, path):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)

for i, page in enumerate(book_data["pages"], 1):
    if page["image"] is None:
        print(f"Generating image for page {i}...")
        for attempt in range(3):
            try:
                image_url = generate_image(page["text"], i)
                if image_url:
                    page["image"] = f"images/page-{i}.png"
                    download_file(image_url, images_dir / f"page-{i}.png")
                    print(f"  Saved: page-{i}.png")
                    break
                else:
                    print(f"  Attempt {attempt+1}: no URL returned")
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}")
                time.sleep(5)
        time.sleep(3)

with open(book_dir / "book.json", "w") as f:
    json.dump(book_data, f, indent=2, ensure_ascii=False)

print(f"Done! Updated {book_dir / 'book.json'}")