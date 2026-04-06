#!/usr/bin/env python3
import json
import os
import requests
from pathlib import Path

API_KEY = "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU"
API_BASE = "https://api.minimax.io/v1"

auth_headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

FIFI_BASE_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. Standing upright 
in a friendly pose."""

book_dir = Path("books/fifi-the-fox-adventure")
book_json_path = book_dir / "book.json"
book_data = json.loads(book_json_path.read_text())

def download_file(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)

def generate_image(text, page_num):
    prompt = f"""{FIFI_BASE_PROMPT}

Children's book illustration for page {page_num}:
Scene: {text}

Style: Warm, colorful children's book illustration with soft edges, friendly characters, and engaging backgrounds. Suitable for ages 1-5."""
    
    print(f"  Generating image for page {page_num}...")
    response = requests.post(
        f"{API_BASE}/image_generation",
        headers=auth_headers,
        json={"model": "image-01", "prompt": prompt},
        timeout=180
    )
    response.raise_for_status()
    result = response.json()
    image_url = result["data"]["image_urls"][0]
    
    img_path = book_dir / "images" / f"page-{page_num}.png"
    download_file(image_url, img_path)
    print(f"    Saved: {img_path}")
    return f"images/page-{page_num}.png"

def generate_audio(text, page_num):
    print(f"  Generating audio for page {page_num}...")
    response = requests.post(
        f"{API_BASE}/t2a_v2",
        headers=auth_headers,
        json={
            "model": "speech-02-hd",
            "text": text,
            "voice_setting": {
                "voice_id": "female-tianmei",
                "speed": 0.85,
                "volume": 1,
                "pitch": 1
            }
        },
        timeout=60
    )
    response.raise_for_status()
    result = response.json()
    audio_url = result["data"]["audio_file"]["url"]
    
    audio_path = book_dir / "audio" / f"page-{page_num}.mp3"
    download_file(audio_url, audio_path)
    print(f"    Saved: {audio_path}")
    return f"audio/page-{page_num}.mp3"

print(f"Generating assets for {book_data['title']}")
print(f"Pages: {len(book_data['pages'])}")

for i, page in enumerate(book_data["pages"], 1):
    print(f"\nPage {i}: {page['text'][:60]}...")
    
    try:
        page["image"] = generate_image(page["text"], i)
    except Exception as e:
        print(f"    Image failed: {type(e).__name__}: {e}")
        page["image"] = None
    
    try:
        page["audio"] = generate_audio(page["text"], i)
    except Exception as e:
        print(f"    Audio failed: {type(e).__name__}: {e}")
        page["audio"] = None
    
    page["video"] = None
    
    with open(book_json_path, "w") as f:
        json.dump(book_data, f, indent=2)

print("\nDone! Book saved to:", book_json_path)