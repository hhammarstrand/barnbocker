#!/usr/bin/env python3
import base64
import json
import os
import requests
from pathlib import Path

BOOK_DIR = Path("books/fifi-creek")
IMAGES_DIR = BOOK_DIR / "images"

def main():
    with open(BOOK_DIR / "image-prompts.json") as f:
        data = json.load(f)

    MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
    MINIMAX_API_BASE = "https://api.minimax.io/v1"

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    style_note = "Soft watercolor-inspired children's book illustration style. Warm, child-friendly atmosphere."

    for i, prompt_text in enumerate(data["imagePrompts"], 1):
        output_path = IMAGES_DIR / f"page-{i}.png"

        if output_path.exists():
            print(f"  Page {i} already exists, skipping")
            continue

        print(f"  Generating page {i}...")

        full_prompt = f"""{style_note} {prompt_text} No text in image whatsoever."""

        if len(full_prompt) > 2000:
            full_prompt = full_prompt[:1990] + "."

        try:
            payload = {
                "model": "image-01",
                "prompt": full_prompt
            }

            response = requests.post(
                f"{MINIMAX_API_BASE}/image_generation",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            if result.get("data") and result["data"].get("image_urls"):
                image_url = result["data"]["image_urls"][0]
                print(f"    Image URL: {image_url[:80]}...")

                img_response = requests.get(image_url)
                img_response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                print(f"    Saved: page-{i}.png")
            else:
                print(f"    Error: no image URL in response - {result}")

        except Exception as e:
            print(f"    Error generating page {i}: {e}")

    print("Image generation complete!")

if __name__ == "__main__":
    main()