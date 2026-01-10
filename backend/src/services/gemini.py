import os
from PIL import Image
import io
import random
from google import genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'august-sandbox-483210-c7')

# Initialize Gemini client with Nano Banana project configuration
GEMINI_CLIENT = None
if GEMINI_API_KEY:
    GEMINI_CLIENT = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={'api_version': 'v1alpha'}
    )

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
    model: str = 'imagen-3.0-generate-001',
    aspect_ratio: str = '1:1',
    resolution: str = '1K',
    response_modality: str = 'TEXT_IMAGE',
    google_search_enabled: bool = False
) -> dict:
    """
    Generate an image using Nano Banana (Google Gemini/Imagen API).

    Uses the august-sandbox-483210-c7 Google Cloud project with Imagen 3.0.
    Falls back to mock mode if API is unavailable or encounters errors.
    """

    # Use Nano Banana API (Google Imagen) if client is available
    if GEMINI_CLIENT:
        try:
            # Map aspect ratios to Imagen format
            aspect_ratio_map = {
                '1:1': '1:1',
                '16:9': '16:9',
                '9:16': '9:16',
                '4:3': '4:3',
                '3:4': '3:4',
            }

            imagen_aspect_ratio = aspect_ratio_map.get(aspect_ratio, '1:1')

            # Generate image using Nano Banana (Imagen API)
            response = GEMINI_CLIENT.models.generate_images(
                model=model,
                prompt=prompt,
                config={
                    'number_of_images': 1,
                    'aspect_ratio': imagen_aspect_ratio,
                    'safety_filter_level': 'block_some',
                    'person_generation': 'allow_adult',
                }
            )

            # Get the first generated image
            if response.generated_images and len(response.generated_images) > 0:
                image = response.generated_images[0]

                # Extract image bytes
                image_bytes = image.image.data

                return {
                    'image_data': image_bytes,
                    'text_response': 'Image generated successfully via Nano Banana API',
                    'token_count': 0,
                    'thought_signature': None,
                    'grounding_metadata': None,
                    'is_mock': False
                }
        except Exception as e:
            print(f"Nano Banana API error: {e}. Falling back to mock mode.")
            # Log full error for debugging
            import traceback
            traceback.print_exc()

    # Fallback to mock mode
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

def generate_mock_video(prompt: str, aspect_ratio: str = '16:9', duration: str = '5s') -> tuple:
    """Generate a mock video when Veo3 API is not available."""

    ratios = {
        '16:9': (640, 360),
        '9:16': (360, 640),
    }

    width, height = ratios.get(aspect_ratio, (640, 360))
    duration_seconds = 5 if duration == '5s' else 8
    fps = 24
    total_frames = duration_seconds * fps

    colors = [
        (255, 182, 193),
        (255, 218, 185),
        (176, 224, 230),
        (221, 160, 221),
        (144, 238, 144),
    ]

    base_color = random.choice(colors)
    accent_color = random.choice(colors)

    frames = []
    for frame_num in range(total_frames):
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        progress = frame_num / total_frames

        for y in range(height):
            for x in range(width):
                ratio = ((x + y) / (width + height) + progress) % 1.0
                r = int(base_color[0] * (1 - ratio) + accent_color[0] * ratio)
                g = int(base_color[1] * (1 - ratio) + accent_color[1] * ratio)
                b = int(base_color[2] * (1 - ratio) + accent_color[2] * ratio)
                pixels[x, y] = (r, g, b)

        frames.append(img)

    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=int(1000/fps),
        loop=0
    )

    return buffer.getvalue(), f"Mock video generated for prompt: {prompt[:100]}..."

async def generate_video(
    prompt: str,
    model: str = 'veo-3.0-generate',
    aspect_ratio: str = '16:9',
    duration: str = '5s',
    image_path: str = None
) -> dict:
    """
    Generate a video using Veo API via Nano Banana.

    Supports both text-to-video and image-to-video generation.
    Falls back to mock mode if API is unavailable or encounters errors.

    Args:
        prompt: Motion prompt describing the video content
        model: Veo model to use (veo-3.0-generate or veo-2.0-generate)
        aspect_ratio: Video aspect ratio (16:9 or 9:16)
        duration: Video duration ('5s' or '8s')
        image_path: Optional path to starting image for image-to-video
    """

    if GEMINI_CLIENT:
        try:
            config = {
                'duration': duration,
                'aspect_ratio': aspect_ratio,
            }

            # If image path provided, load and include in config
            if image_path:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                config['starting_image'] = image_data

            # Generate video using Veo API
            response = GEMINI_CLIENT.models.generate_video(
                model=model,
                prompt=prompt,
                config=config
            )

            if response.generated_videos and len(response.generated_videos) > 0:
                video = response.generated_videos[0]
                return {
                    'video_data': video.video.data,
                    'duration': duration,
                    'text_response': f'Video generated successfully via Nano Banana API ({model})',
                    'is_mock': False
                }
        except Exception as e:
            print(f"Veo API error: {e}. Falling back to mock mode.")
            import traceback
            traceback.print_exc()

    # Fallback to mock mode
    video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
    return {
        'video_data': video_data,
        'text_response': text_response,
        'is_mock': True
    }
