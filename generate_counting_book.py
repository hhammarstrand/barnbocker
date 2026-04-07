#!/usr/bin/env python3
import json
import os
import requests
from pathlib import Path

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID")
MINIMAX_API_BASE = "https://api.minimax.io/v1"

headers = {
    "Authorization": f"Bearer {MINIMAX_API_KEY}",
    "Content-Type": "application/json"
}

book_id = "fifi-counting"
book_dir = Path(f"books/{book_id}")
images_dir = book_dir / "images"
images_dir.mkdir(parents=True, exist_ok=True)

prompt = """Write a short counting story for ages 2-4.

Main character: Fifi the Fox (a cute baby red fox with bright orange fur and cream-colored belly and snout, large expressive dark eyes, fluffy white-tipped tail)
Side character: Oliver the Owl (a round, fluffy owl with warm tan/brown feathers, big round spectacles, wise and kind)

Theme: Counting 1 to 5 in a sunny meadow

Write about Fifi and Oliver exploring a meadow and counting things they find:
1. One big red apple on the ground
2. Two orange butterflies dancing
3. Three pink flowers swaying
4. Four smooth grey pebbles
5. Five golden dandelions

Requirements:
- Exactly 6 pages total (one title/intro page + the 5 counting pages)
- Each page: 10-20 words (simple for ages 2-4)
- Use playful, discovery language - "Look!", "One!", "Two!"
- Positive and curious feeling - counting is an adventure
- Return ONLY valid JSON, no markdown or extra text

Format:
{"pages": [{"text": "Page 1 text..."}, {"text": "Page 2 text..."}]}"""

print("Generating counting story text...")
response = requests.post(
    f"{MINIMAX_API_BASE}/text/chatcompletion_v2",
    headers=headers,
    json={
        "model": "MiniMax-M2.7-highspeed",
        "messages": [{"role": "user", "content": prompt}]
    },
    timeout=60
)
response.raise_for_status()
result = response.json()
content = result["choices"][0]["message"]["content"]
print(f"Raw response: {content[:500]}")

if content.startswith("```json"):
    content = content[7:]
if content.endswith("```"):
    content = content[:-3]
content = content.strip()

story_data = json.loads(content)
print(f"Generated {len(story_data['pages'])} pages")

for i, page in enumerate(story_data["pages"], 1):
    print(f"  Page {i}: {page['text'][:60]}...")

print("\nGenerating illustrations...")

FIFI_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail.
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. Standing upright 
in a friendly pose."""

OLIVER_PROMPT = """A round, fluffy owl with warm tan/brown feathers, big round spectacles with gold frames, 
a wise tuft of feathers on top of head. Large wise eyes behind spectacles. 
Soft children's book illustration style. Warm colors, gentle and kind expression."""

SCENE_PROMPTS = [
    "Fifi the baby fox and Oliver the owl meeting in a sunny meadow, excited to explore and count together. Bright summer day with soft grass.",
    "Fifi and Oliver finding ONE big shiny red apple on the ground in the meadow. They look at it with wonder and curiosity.",
    "Fifi and Oliver watching TWO orange butterflies dancing and fluttering around them. The butterflies look like tiny flames dancing in the air.",
    "Fifi and Oliver discovering THREE pink flowers swaying gently in the warm breeze. A beautiful meadow scene.",
    "Fifi and Oliver counting FOUR smooth grey pebbles by a sunny path. Oliver uses his wing to point at each one.",
    "Fifi and Oliver picking up FIVE golden dandelions, counting each one with big smiles. The meadow glows golden in the sunlight."
]

generated_pages = []
for i, page in enumerate(story_data["pages"], 1):
    page_text = page["text"]
    scene_prompt = SCENE_PROMPTS[i-1]
    
    full_prompt = f"""{FIFI_PROMPT}

{OLIVER_PROMPT}

Children's book illustration for page {i}:
Scene: {page_text}
Additional scene details: {scene_prompt}

Style: Warm, colorful children's book illustration with soft edges, friendly characters, and engaging backgrounds. Soft watercolor style. Suitable for ages 2-4. Bright, sunny, curious atmosphere."""
    
    print(f"  Generating image for page {i}...")
    try:
        img_response = requests.post(
            f"{MINIMAX_API_BASE}/image_generation",
            headers=headers,
            json={
                "model": "image-01",
                "prompt": full_prompt
            },
            timeout=120
        )
        img_response.raise_for_status()
        img_result = img_response.json()
        image_url = img_result["data"]["image_urls"][0]
        print(f"    Image URL: {image_url[:80]}...")
        
        img_data_response = requests.get(image_url)
        img_data_response.raise_for_status()
        image_path = images_dir / f"page-{i}.png"
        with open(image_path, "wb") as f:
            f.write(img_data_response.content)
        print(f"    Saved: {image_path}")
        page["image"] = f"images/page-{i}.png"
    except Exception as e:
        print(f"    Image generation failed: {e}")
        page["image"] = None
    
    page["audio"] = None
    page["video"] = None
    generated_pages.append(page)

book_data = {
    "id": book_id,
    "title": "Counting with Fifi and Oliver",
    "description": "Join Fifi the Fox and Oliver the Owl on a sunny meadow adventure as they count from one to five!",
    "coverColor": "e67e22",
    "coverEmoji": "🦊",
    "pages": generated_pages,
    "metadata": {
        "mainCharacter": "Fifi the Fox",
        "sideCharacters": ["Oliver the Owl"],
        "theme": "counting",
        "targetAge": "2-4",
        "wordCount": sum(len(p["text"].split()) for p in generated_pages),
        "generatedAt": __import__("datetime").datetime.utcnow().isoformat()
    }
}

with open(book_dir / "book.json", "w") as f:
    json.dump(book_data, f, indent=2)
print(f"\nSaved: {book_dir / 'book.json'}")

meta_data = {
    "id": book_id,
    "title": book_data["title"],
    "description": book_data["description"],
    "pageCount": len(generated_pages),
    "coverColor": book_data["coverColor"],
    "coverEmoji": book_data["coverEmoji"]
}

with open(book_dir / "meta.json", "w") as f:
    json.dump(meta_data, f, indent=2)
print(f"Saved: {book_dir / 'meta.json'}")

cover_prompt = f"""{FIFI_PROMPT}

{OLIVER_PROMPT}

Book cover illustration:
Fifi the baby fox sitting happily in a sunny meadow with Oliver the owl wearing spectacles nearby.
They are surrounded by floating numbers 1, 2, 3, 4, 5 and colorful butterflies. 
A big red apple sits between them. The meadow is bright and golden.
Warm, playful, curious atmosphere. Title area should be clear on the right side.

Style: Warm, colorful children's book cover with soft edges. Bright, curious, playful atmosphere."""

print("\nGenerating cover image...")
try:
    cover_response = requests.post(
        f"{MINIMAX_API_BASE}/image_generation",
        headers=headers,
        json={
            "model": "image-01",
            "prompt": cover_prompt
        },
        timeout=120
    )
    cover_response.raise_for_status()
    cover_result = cover_response.json()
    cover_url = cover_result["data"]["image_urls"][0]
    
    cover_data_response = requests.get(cover_url)
    cover_data_response.raise_for_status()
    cover_path = book_dir / "cover.png"
    with open(cover_path, "wb") as f:
        f.write(cover_data_response.content)
    print(f"Saved cover: {cover_path}")
except Exception as e:
    print(f"Cover generation failed: {e}")

print("\nBook generation complete!")
print(f"Book ID: {book_id}")
print(f"Pages: {len(generated_pages)}")
print(f"Total words: {book_data['metadata']['wordCount']}")