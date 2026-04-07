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

book_id = "fifi-bedtime"
book_dir = Path(f"books/{book_id}")
images_dir = book_dir / "images"
images_dir.mkdir(parents=True, exist_ok=True)

prompt = """Write a short bedtime story for ages 1-3.

Main character: Fifi the Fox (a cute baby red fox with bright orange fur and cream-colored belly and snout, large expressive dark eyes, fluffy white-tipped tail)

Theme: Bedtime routine

Write about Fifi going through her bedtime routine step by step in a cozy fox den:
1. Putting on cozy star-patterned pajamas
2. Brushing teeth with a fruity toothpaste
3. Listening to a bedtime story
4. Getting a warm goodnight hug from Mom
5. Turning off the light with a soft glow nightlight
6. Falling asleep and dreaming sweet dreams

Requirements:
- Exactly 6 pages total (one for each step above)
- Each page: 10-20 words (very simple for ages 1-3)
- Use soft, sleepy, warm language
- Positive and cozy feeling - bedtime is safe and wonderful
- Return ONLY valid JSON, no markdown or extra text

Format:
{"pages": [{"text": "Page 1 text..."}, {"text": "Page 2 text..."}]}"""

print("Generating bedtime story text...")
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

FIFI_BEDTIME_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail.
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. Standing upright 
in a friendly pose."""

page_prompts = [
    "Fifi the baby fox putting on cozy star-patterned pajamas in her warm den. Soft amber lamplight. Sleepy happy expression.",
    "Fifi the baby fox brushing her teeth with a fruity toothpaste, standing on a small stool. Cute bubbly toothpaste. Warm bathroom.",
    "Fifi the baby fox sitting in a cozy armchair, listening to a bedtime story being read. Book open on lap. Cozy den atmosphere.",
    "Fifi the baby fox receiving a warm goodnight hug from her mother fox. Both smiling. Soft warm embrace in the den.",
    "Fifi the baby fox turning off the lamp, a soft glowing nightlight on. Cozy dark room with stars visible through window.",
    "Fifi the baby fox sleeping peacefully in her small cozy bed, dreaming with tiny smile. Soft moonlight through window. Sweet dreams."
]

generated_pages = []
for i, page in enumerate(story_data["pages"], 1):
    page_text = page["text"]
    scene_prompt = page_prompts[i-1]
    
    full_prompt = f"""{FIFI_BEDTIME_PROMPT}

Children's book illustration for page {i}:
Scene: {page_text}
Additional scene details: {scene_prompt}

Style: Warm, colorful children's book illustration with soft edges, friendly characters, and engaging backgrounds. Soft watercolor style. Suitable for ages 1-3. Calm, cozy, sleepy atmosphere."""
    
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
    "title": "Goodnight, Fifi!",
    "description": "Join Fifi the Fox on a cozy bedtime adventure. Follow her routine from pajamas to sweet dreams.",
    "coverColor": "6366f1",
    "coverEmoji": "🌙",
    "pages": generated_pages,
    "metadata": {
        "mainCharacter": "Fifi the Fox",
        "sideCharacters": [],
        "theme": "bedtime",
        "targetAge": "1-3",
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

cover_prompt = f"""{FIFI_BEDTIME_PROMPT}

Book cover illustration:
Fifi the baby fox yawning sleepily and stretching in her cozy starry bedroom at night. 
She's wearing cozy star-patterned pajamas. A soft moon is visible through the window.
Warm, magical, cozy bedtime atmosphere. Title area should be clear on the right side.

Style: Warm, colorful children's book cover with soft edges. Calm, sleepy atmosphere."""

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