import os
from PIL import Image
import io
import random

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

def generate_mock_image(prompt: str, aspect_ratio: str = '1:1', resolution: str = '1K') -> tuple:
    """Generate a mock image when Gemini API is not available."""

    ratios = {
        '1:1': (512, 512),
        '2:3': (512, 768),
        '3:2': (768, 512),
        '3:4': (512, 683),
        '4:3': (683, 512),
        '4:5': (512, 640),
        '5:4': (640, 512),
        '9:16': (512, 910),
        '16:9': (910, 512),
        '21:9': (1024, 439),
    }

    width, height = ratios.get(aspect_ratio, (512, 512))

    if resolution == '2K':
        width, height = width * 2, height * 2
    elif resolution == '4K':
        width, height = width * 4, height * 4

    colors = [
        (255, 182, 193),
        (255, 218, 185),
        (176, 224, 230),
        (221, 160, 221),
        (144, 238, 144),
        (255, 255, 224),
    ]

    base_color = random.choice(colors)
    accent_color = random.choice(colors)

    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            ratio = (x + y) / (width + height)
            r = int(base_color[0] * (1 - ratio) + accent_color[0] * ratio)
            g = int(base_color[1] * (1 - ratio) + accent_color[1] * ratio)
            b = int(base_color[2] * (1 - ratio) + accent_color[2] * ratio)
            pixels[x, y] = (r, g, b)

    text_response = f"Mock image generated for prompt: {prompt[:100]}..."

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue(), text_response

async def generate_image(
    prompt: str,
    model: str = 'gemini-2.5-flash-image',
    aspect_ratio: str = '1:1',
    resolution: str = '1K',
    response_modality: str = 'TEXT_IMAGE',
    google_search_enabled: bool = False
) -> dict:
    """Generate an image using Gemini API or mock if not available."""

    image_data, text_response = generate_mock_image(prompt, aspect_ratio, resolution)
    return {
        'image_data': image_data,
        'text_response': text_response,
        'token_count': len(prompt.split()) * 2,
        'thought_signature': None,
        'grounding_metadata': None,
        'is_mock': True
    }

async def edit_image(
    image_path: str,
    prompt: str,
    model: str = 'gemini-2.5-flash-image',
    aspect_ratio: str = '1:1',
    resolution: str = '1K'
) -> dict:
    """Edit an existing image with a new prompt."""
    return await generate_image(
        prompt=f"Edit: {prompt}",
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution
    )
