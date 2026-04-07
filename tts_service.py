#!/usr/bin/env python3
"""
TTS Service — supports Minimax and ElevenLabs providers.
Set TTS_PROVIDER=elevenlabs and ELEVENLABS_API_KEY to use ElevenLabs.
"""
import base64
import os
import requests

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-NFnfASzuMPdbIP-UUqccOfX6nG6vqAt8RxNg9vw0o3fxoiRAGV8EnFyPoYhFUmomX_57eWcAcyNfecs8_I6S2B_O_T7cYoa8CEdXMPc-YFkuooURO0nmvqU")
MINIMAX_API_BASE = "https://api.minimax.io/v1"

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "minimax")

MINIMAX_VOICE_IDS = {
    "female-tianmei": "female-tianmei",
    "male-tianlei": "male-tianlei",
    "female-yunjian": "female-yunjian",
}

ELEVENLABS_VOICE_IDS = {
    "female-child": "pFZPnxbGlWUjxwdfRNrA",
    "female-warm": "EXAVITQu4vr4xnSDxMaL",
    "male-friendly": "VR6AewLTigWG4SRSQUuC",
}


class TTSService:
    def __init__(self, provider=None, api_key=None):
        self.provider = provider or TTS_PROVIDER
        if self.provider == "elevenlabs":
            self.api_key = api_key or ELEVENLABS_API_KEY
            if not self.api_key:
                raise ValueError("ELEVENLABS_API_KEY environment variable not set")
        else:
            self.api_key = MINIMAX_API_KEY

    def generate_audio(self, text, voice_id=None, output_path=None, voice_profile="female-tianmei"):
        if self.provider == "elevenlabs":
            return self._elevenlabs_generate(text, voice_id or "female-child", output_path)
        else:
            return self._minimax_generate(text, voice_id or voice_profile, output_path)

    def _minimax_generate(self, text, voice_id, output_path):
        response = requests.post(
            f"{MINIMAX_API_BASE}/t2a_v2",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
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
        audio_url = result["data"]["audio_file"]["url"]
        if output_path:
            self._download(audio_url, output_path)
        return audio_url

    def _elevenlabs_generate(self, text, voice_id, output_path):
        voice_id = ELEVENLABS_VOICE_IDS.get(voice_id, voice_id)
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            },
            timeout=60
        )
        response.raise_for_status()
        audio_data = response.content
        if output_path:
            with open(output_path, "wb") as f:
                f.write(audio_data)
        return audio_data

    def _download(self, url, path):
        response = requests.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)


def generate_audio_for_text(text, voice_profile="female-child", output_path=None, provider=None):
    service = TTSService(provider=provider or TTS_PROVIDER)
    return service.generate_audio(text, voice_profile=voice_profile, output_path=output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python tts_service.py <text> <output.mp3> [provider]")
        print("  provider: minimax (default) or elevenlabs")
        sys.exit(1)
    text = sys.argv[1]
    output = sys.argv[2]
    provider = sys.argv[3] if len(sys.argv) > 3 else TTS_PROVIDER
    result = generate_audio_for_text(text, output_path=output, provider=provider)
    print(f"Audio saved to {output}")