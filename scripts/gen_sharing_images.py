#!/usr/bin/env python3
import json
import os
import requests
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY")
BOOK_DIR = Path("books/fifi-sharing")
IMAGES_DIR = BOOK_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

SHARING_PROMPT = """Adorable young orange fox with bright fur and cream-colored belly, playing with a small pink and white bunny rabbit in a sunny meadow. Both animals smiling warmly at each other. Children's book illustration with soft colors, gentle shapes, warm sunlight, and friendly expressions."""

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

with open(BOOK_DIR / "book.json") as f:
    book = json.load(f)

pages = book["pages"]
print(f"Generating {len(pages)} page images for fifi-sharing")

for i, page in enumerate(pages, 1):
    scene = page["text"]
    prompt = f"""{SHARING_PROMPT}

Children's book illustration for page {i}:
Scene: {scene}

Style: Warm, soft children's book illustration with cozy meadow atmosphere, pastel colors, Beatrix Potter inspired."""

    print(f"  Page {i}...", end=" ", flush=True)
    
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.minimax.io/v1/image_generation",
                headers=headers,
                json={"model": "image-02", "prompt": prompt},
                timeout=300
            )
            data = resp.json()
            if data.get("base_resp", {}).get("status_code") == 0:
                img_url = data["data"]["image_urls"][0]
                print(f"URL received, downloading...", end=" ", flush=True)
                img_resp = requests.get(img_url, headers=headers, timeout=10)
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    with open(IMAGES_DIR / f"page-{i}.png", "wb") as f:
                        f.write(img_resp.content)
                    page["image"] = f"images/page-{i}.png"
                    print("OK")
                    break
                else:
                    print(f"Download failed: {img_resp.status_code} size={len(img_resp.content)}")
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
    else:
        print("FAILED")

with open(BOOK_DIR / "book.json", "w") as f:
    json.dump(book, f, indent=2)

print(f"\nUpdated {BOOK_DIR / 'book.json'}")