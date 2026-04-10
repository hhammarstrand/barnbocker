#!/usr/bin/env python3
import json
import os
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tts_service import TTSService, generate_audio_for_text

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
        json={"model": "image-02", "prompt": prompt},
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
    audio_path = book_dir / "audio" / f"page-{page_num}.mp3"
    try:
        generate_audio_for_text(
            text,
            voice_profile="female-child",
            output_path=str(audio_path)
        )
        print(f"    Saved: {audio_path}")
        return f"audio/page-{page_num}.mp3"
    except Exception as e:
        print(f"    Audio failed: {type(e).__name__}: {e}")
        return None

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