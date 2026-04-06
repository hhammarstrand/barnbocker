# Book Content Format Specification

## Overview

Books are stored as structured JSON with accompanying image and audio assets. The format is designed to be:
- Easy for the web app reader to consume
- Compatible with Minimax generation pipeline output
- Extensible for future features (video, interactivity)

## Directory Structure

```
books/
  {book-id}/
    book.json          # Main book data
    meta.json          # Library metadata
    cover.png          # Cover image (optional, can be generated)
    images/
      page-{n}.png     # Page illustrations
    audio/
      page-{n}.mp3     # Page narration audio
    video/
      page-{n}.mp4     # Optional animated page video
```

## book.json Schema

```json
{
  "id": "string (unique book identifier, kebab-case)",
  "title": "string (book title)",
  "description": "string (1-2 sentence description for library view)",
  "coverColor": "string (hex color for placeholder, e.g. '6366f1')",
  "coverEmoji": "string (emoji for placeholder, e.g. '🦊')",
  "pages": [
    {
      "text": "string (page text, 20-80 words for ages 1-5)",
      "image": "string (URL to illustration, relative path, or null)",
      "audio": "string (URL to narration MP3, relative path, or null)",
      "video": "string (optional URL to animated video, relative path, or null)"
    }
  ],
  "metadata": {
    "mainCharacter": "string (character name for consistency)",
    "sideCharacters": ["string (array of side character names)"],
    "theme": "string (animals|emotions|bedtime|adventure|seasons|etc)",
    "targetAge": "string ('1-3' or '3-5')",
    "wordCount": "number (total words across all pages)",
    "generatedAt": "string (ISO 8601 timestamp)"
  }
}
```

## meta.json Schema (Library Display)

```json
{
  "id": "string (matches book.json id)",
  "title": "string (book title)",
  "description": "string (short description for library card)",
  "pageCount": "number (total number of pages)",
  "coverColor": "string (optional, overrides book.json)",
  "coverEmoji": "string (optional, overrides book.json)",
  "cover": "string (optional, URL to cover image)"
}
```

## Page Illustration Specifications

- **Format**: PNG with transparency
- **Dimensions**: 1024x768 (4:3 ratio) or 1024x1024 (1:1)
- **Style**: Children's book illustration, warm colors, simple shapes
- **Character Consistency**: Use character prompts from Character Bible

## Audio Specifications

- **Format**: MP3, 128kbps minimum
- **Duration**: 10-30 seconds per page (matches page text reading time)
- **Voice**: Child-friendly, warm, age-appropriate pace
- **Naming**: `page-{n}.mp3` where n is 1-indexed

## Video Specifications (Optional)

- **Format**: MP4, H.264
- **Dimensions**: 1280x720
- **Duration**: 15-45 seconds per page
- **Content**: Animated illustration with synced narration

## Generation Pipeline Flow

1. **Text Generation** → story text in correct format
2. **Illustration Generation** → Minimax image for each page
3. **Audio Generation** → Minimax TTS for each page narration
4. **Video Generation** (optional) → Minimax video for animated storybook
5. **Output** → Save as `book.json` + asset files

## Example

See `/books/fox-adventure/book.json` for a complete example.