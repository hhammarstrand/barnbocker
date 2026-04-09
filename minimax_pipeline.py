#!/usr/bin/env python3
import base64
import json
import os
import sys
import requests
import subprocess
from pathlib import Path

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "2031978439547822419")
MINIMAX_API_BASE = "https://api.minimax.io/v1"

class MinimaxPipeline:
    def __init__(self, output_dir="books"):
        self.output_dir = Path(output_dir)
        self.api_key = MINIMAX_API_KEY
        self.group_id = MINIMAX_GROUP_ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_text(self, theme, main_character, side_characters=None, target_age="1-5"):
        side_chars_text = ", ".join(side_characters) if side_characters else "Inga bikaraktärer"
        prompt = f"""Skriv en kort barnbokshistoria på svenska för barn i åldrarna {target_age}.

Huvudkaraktär: {main_character}
Bikaraktärer: {side_chars_text}
Tema: {theme}

Krav:
- Minst 10 sidor totalt
- Varje sida: 25-50 ord
- Enkel vocabular som passar små barn
- Positiv och engagerande berättelse
- Färg, rörelse och spänning i varje scen
- Ha ALLTID svensk text i alla svar, inget engelska

Exempel format:
{{"pages": [{{"text": "Sidtext på svenska..."}}, {{"text": "Mer svensk text..."}}]}}"""
        
        response = requests.post(
            f"{MINIMAX_API_BASE}/text/chatcompletion_v2",
            headers=self.headers,
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

    def generate_image(self, text, character_prompt, page_num, use_base64=False):
        prompt = f"""{character_prompt}

Barnbokillustration för sid {page_num}:
Scen: {text}

Viktiga krav:
- INGEN text i bilden - inga ord, bokstäver eller siffror av något slag
- FLERA karaktärer i varje scen där så är lämpligt
- Rich och komplex bakgrund med detaljer
- Rörelse och dynamik - karaktärer som rör sig, interagerar, uttrycker känslor
- Livlig och engagerande scen med mycket att se
- Varma, barnvänliga färger
- Söt och lekfull stil lämplig för åldrarna 1-5

Style: Colorful children's book illustration with soft edges, multiple friendly characters, dynamic scenes with lots of activity and life. NO TEXT whatsoever in the image."""
        
        payload = {
            "model": "image-01",
            "prompt": prompt
        }
        if use_base64:
            payload["response_format"] = "base64"
        
        response = requests.post(
            f"{MINIMAX_API_BASE}/image_generation",
            headers=self.headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        if use_base64:
            image_data = base64.b64decode(result["data"]["image_base64"][0])
            return image_data
        return result["data"]["image_urls"][0]

    def generate_audio(self, text, voice_id="female-tianmei"):
        response = requests.post(
            f"{MINIMAX_API_BASE}/t2a_v2",
            headers=self.headers,
            json={
                "model": "speech-02-hd",
                "text": text,
                "voice_setting": {
                    "voice_id": voice_id,
                    "speed": 85,
                    "volume": 100,
                    "pitch": 11
                }
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result["data"]["audio_file"]["url"]

    def generate_video(self, image_url, text):
        response = requests.post(
            f"{MINIMAX_API_BASE}/video_generation",
            headers=self.headers,
            json={
                "model": "video-01",
                "image_url": image_url,
                "prompt": text
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["data"]["video_url"]

    def generate_book(self, theme, main_character, side_characters=None, 
                     character_prompt=None, book_id=None, target_age="1-5",
                     auto_push=True):
        book_id = book_id or main_character.lower().replace(" ", "-") + "-adventure"
        book_dir = self.output_dir / book_id
        images_dir = book_dir / "images"
        audio_dir = book_dir / "audio"
        
        book_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        audio_dir.mkdir(exist_ok=True)
        
        print(f"Generating book: {book_id}")
        story_data = self.generate_text(theme, main_character, side_characters, target_age)
        
        for i, page in enumerate(story_data["pages"], 1):
            print(f"  Generating page {i}: {page['text'][:50]}...")
            page["image"] = None
            page["audio"] = None
            page["video"] = None
            
            if character_prompt:
                try:
                    image_data = self.generate_image(
                        page["text"], 
                        character_prompt, 
                        i,
                        use_base64=True
                    )
                    page["image"] = f"images/page-{i}.png"
                    with open(images_dir / f"page-{i}.png", "wb") as f:
                        f.write(image_data)
                    print(f"    Image saved: page-{i}.png")
                except Exception as e:
                    print(f"    Image generation failed: {e}")
            
            try:
                audio_url = self.generate_audio(page["text"])
                page["audio"] = f"audio/page-{i}.mp3"
                self._download_file(audio_url, audio_dir / f"page-{i}.mp3")
                print(f"    Audio saved: page-{i}.mp3")
            except Exception as e:
                print(f"    Audio generation failed: {e}")
        
        swedish_themes = {
            "friendship": "vänskap",
            "adventure": "äventyr",
            "nature": "natur",
            "bedtime": "godnattsagor",
            "emotions": "känslor",
            "animals": "djur",
            "seasons": "årstider",
            "family": "familj"
        }
        theme_sv = swedish_themes.get(theme.lower(), theme)
        
        book_data = {
            "id": book_id,
            "title": f"{main_character}s {theme_sv.title()}-äventyr",
            "description": f" följd {main_character} på ett spännande {theme_sv} äventyr!",
            "coverColor": "6366f1",
            "coverEmoji": "📚",
            "pages": story_data["pages"],
            "metadata": {
                "mainCharacter": main_character,
                "sideCharacters": side_characters or [],
                "theme": theme,
                "targetAge": target_age,
                "wordCount": sum(len(p["text"].split()) for p in story_data["pages"]),
                "generatedAt": __import__("datetime").datetime.utcnow().isoformat()
            }
        }
        
        with open(book_dir / "book.json", "w") as f:
            json.dump(book_data, f, indent=2)
        
        meta_data = {
            "id": book_id,
            "title": book_data["title"],
            "description": book_data["description"],
            "pageCount": len(story_data["pages"]),
            "coverColor": book_data["coverColor"],
            "coverEmoji": book_data["coverEmoji"]
        }
        
        with open(book_dir / "meta.json", "w") as f:
            json.dump(meta_data, f, indent=2)
        
        print(f"Book generated: {book_dir / 'book.json'}")
        
        if auto_push:
            self.auto_push(commit_message=f"Generated book: {book_data['title']}")
        
        return book_data

    def _download_file(self, url, path):
        response = requests.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)

    def auto_push(self, commit_message=None):
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.output_dir.parent)
            if not result.stdout.strip():
                print("No changes to commit.")
                return
            
            subprocess.run(["git", "add", "."], cwd=self.output_dir.parent, check=True)
            
            if commit_message is None:
                commit_message = f"Auto-commit: book generated at {__import__('datetime').datetime.utcnow().isoformat()}"
            
            subprocess.run(["git", "commit", "-m", commit_message], cwd=self.output_dir.parent, check=True)
            subprocess.run(["git", "push"], cwd=self.output_dir.parent, check=True)
            print(f"Auto-pushed: {commit_message}")
        except subprocess.CalledProcessError as e:
            print(f"Auto-push failed: {e}")
            raise


FIFI_BASE_PROMPT = """A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. Standing upright 
in a friendly pose."""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python minimax_pipeline.py <theme> <main_character> [side_characters...] [--prompt '<character_prompt>'] [--no-auto-push]")
        sys.exit(1)
    
    theme = sys.argv[1]
    main_character = sys.argv[2]
    side_characters = None
    character_prompt = FIFI_BASE_PROMPT
    auto_push = True
    
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == '--prompt':
            character_prompt = args[i + 1]
            i += 2
        elif args[i] == '--no-auto-push':
            auto_push = False
            i += 1
        else:
            side_characters = args[i:]
            break
    
    pipeline = MinimaxPipeline()
    pipeline.generate_book(theme, main_character, side_characters, character_prompt=character_prompt, auto_push=auto_push)