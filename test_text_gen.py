#!/usr/bin/env python3
import requests
import json

MINIMAX_API_KEY = 'sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU'
headers = {
    'Authorization': f'Bearer {MINIMAX_API_KEY}',
    'Content-Type': 'application/json'
}

prompt = '''Skriv en kort barnbokshistoria på svenska för barn i åldrarna 1-5.

Huvudkaraktär: Fifi (en liten räv)
Bikaraktärer: Bruno (en björn)
Tema: helping

Krav:
- Minst 10 sidor totalt
- Varje sida: 25-50 ord
- Enkel vocabular som passar små barn
- Positiv och engagerande berättelse
- Färg, rörelse och spänning i varje scen
- Ha ALLTID svensk text i alla svar, inget engelska

Exempel format:
{"pages": [{"text": "Sidtext på svenska..."}, {"text": "Mer svensk text..."}]}'''

print('Generating text...')
response = requests.post(
    'https://api.minimax.io/v1/text/chatcompletion_v2',
    headers=headers,
    json={
        'model': 'MiniMax-M2.7-highspeed',
        'messages': [{'role': 'user', 'content': prompt}]
    },
    timeout=110
)
print(f'Status: {response.status_code}')
result = response.json()
content = result['choices'][0]['message']['content']

if content.startswith('```json'):
    content = content[7:]
if content.endswith('```'):
    content = content[:-3]

data = json.loads(content.strip())
print(f'Pages: {len(data["pages"])}')
for i, page in enumerate(data['pages'][:3], 1):
    print(f'Page {i}: {page["text"][:80]}...')

with open('books/fifi-helping/book.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Saved book.json')