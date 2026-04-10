#!/usr/bin/env python3
import json
import os
import requests
import subprocess
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
API_BASE = "https://api.minimax.io/v1"

FIFI_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. NO TEXT OR WORDS IN IMAGE."""

def generate_image(text, page_num, output_path):
    prompt = f"""{FIFI_PROMPT}

Children's book illustration for page {page_num}:
Scene: {text}

Style: Warm, colorful children's book illustration with soft edges, friendly characters, and engaging backgrounds. Suitable for ages 1-5."""
    
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

def create_book(book_id, title, theme, main_char, side_chars, pages_text):
    book_dir = Path(f"books/{book_id}")
    images_dir = book_dir / "images"
    book_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    pages = []
    for i, text in enumerate(pages_text, 1):
        img_path = images_dir / f"page-{i}.png"
        print(f"  Page {i}...")
        try:
            generate_image(text, i, img_path)
        except Exception as e:
            print(f"    Failed: {e}")
            continue
        pages.append({"text": text, "image": f"images/page-{i}.png", "audio": None, "video": None})
    
    book_data = {
        "id": book_id,
        "title": title,
        "description": f"Join {main_char} on an exciting {theme} adventure!",
        "coverColor": "6366f1",
        "coverEmoji": "🦊",
        "pages": pages,
        "metadata": {
            "mainCharacter": main_char,
            "sideCharacters": side_chars,
            "theme": theme,
            "targetAge": "1-5",
            "wordCount": sum(len(p.split()) for p in pages_text),
            "generatedAt": datetime.utcnow().isoformat()
        }
    }
    
    with open(book_dir / "book.json", "w") as f:
        json.dump(book_data, f, indent=2)
    
    meta = {
        "id": book_id,
        "title": title,
        "description": book_data["description"],
        "pageCount": len(pages),
        "coverColor": book_data["coverColor"],
        "coverEmoji": book_data["coverEmoji"]
    }
    with open(book_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    
    return book_data

def auto_push():
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            subprocess.run(["git", "commit", "-m", "Auto-push: new book content\n\nCo-Authored-By: Paperclip <noreply@paperclip.ing>"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("  Auto-pushed to git")
    except Exception as e:
        print(f"  Auto-push failed: {e}")

if __name__ == "__main__":
    import sys
    
    books = [
        {
            "id": "fifi-forest-adventure",
            "title": "Fifi Explores the Forest",
            "theme": "adventure",
            "main_char": "Fifi the Fox",
            "side_chars": ["Oliver the Owl"],
            "pages": [
                "One bright morning, Fifi the Fox woke up and decided to explore the big forest. She packed some snacks and waved goodbye to her family.",
                "Fifi walked past tall trees and heard a hoot from above. Oliver the Owl looked down and asked, Where are you going, little fox?",
                "I am exploring the forest, said Fifi. Would you like to come? Oliver flew down and said, I know every tree here!",
                "Together they discovered a sparkling stream. Fifi drank cool water while Oliver pointed out colorful butterflies dancing nearby.",
                "Oliver showed Fifi a hidden cave with beautiful paintings on the walls. Fifi gasped with wonder at the ancient art.",
                "As the sun set, Fifi and Oliver found a cozy hollow tree. They snuggled together and fell asleep under the twinkling stars."
            ]
        }
    ]
    
    for book in books:
        print(f"Generating: {book['title']}")
        create_book(book["id"], book["title"], book["theme"], book["main_char"], book["side_chars"], book["pages"])
        auto_push()