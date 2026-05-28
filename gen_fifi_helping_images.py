#!/usr/bin/env python3
import base64
import json
import os
import requests
from pathlib import Path
import time

MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', 'sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU')
headers = {
    'Authorization': f'Bearer {MINIMAX_API_KEY}',
    'Content-Type': 'application/json'
}

FIFI_PROMPT = '''A cute baby red fox with bright orange fur and cream-colored belly and snout. 
Large expressive dark eyes with sparkle of curiosity. Fluffy white-tipped tail. 
Small friendly appearance with soft rounded features. Children's book illustration 
style. Warm colors, soft edges, adorable and child-friendly. Standing upright 
in a friendly pose.'''

BRUNO_PROMPT = '''A cute baby brown bear with soft fur, large expressive dark eyes full of warmth, fluffy round ears, gentle friendly appearance with soft rounded features. Children's book illustration style. Warm brown colors, soft edges, adorable and child-friendly. Standing upright in a friendly pose.'''

book_dir = Path('books/fifi-helping')
images_dir = book_dir / 'images'
images_dir.mkdir(exist_ok=True)

with open(book_dir / 'image-prompts.json') as f:
    prompts = json.load(f)

for page in prompts['pages']:
    page_num = page['page']
    image_prompt = page['imagePrompt']
    
    full_prompt = f'''{FIFI_PROMPT}

Bruno character: {BRUNO_PROMPT}

Children's book illustration for page {page_num}:
Scene: {image_prompt}

Important requirements:
- NO text in the image - no words, letters or numbers of any kind
- MULTIPLE characters in each scene where appropriate
- Rich and complex background with details
- Movement and dynamics - characters moving, interacting, expressing emotions
- Engaging scene with lots to see
- Warm, child-friendly colors
- Cute and playful style suitable for ages 1-5

Style: Colorful children's book illustration with soft edges, multiple friendly characters, dynamic scenes with lots of activity and life. NO TEXT whatsoever in the image.'''
    
    print(f'Generating page {page_num}...')
    
    for attempt in range(3):
        try:
            payload = {
                'model': 'image-01',
                'prompt': full_prompt,
                'response_format': 'base64'
            }
            
            response = requests.post(
                'https://api.minimax.io/v1/image_generation',
                headers=headers,
                json=payload,
                timeout=180
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('data') and result['data'].get('image_base64'):
                image_data = base64.b64decode(result['data']['image_base64'][0])
                with open(images_dir / f'page-{page_num}.png', 'wb') as f:
                    f.write(image_data)
                print(f'  Saved: page-{page_num}.png')
                break
            else:
                print(f'  Attempt {attempt+1}: No image data, retrying...')
                time.sleep(5)
        except Exception as e:
            print(f'  Attempt {attempt+1} failed: {e}, retrying...')
            time.sleep(10)
    else:
        print(f'  Failed to generate page {page_num} after 3 attempts')

print('Done!')