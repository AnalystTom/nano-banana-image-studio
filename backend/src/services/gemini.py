import os
from PIL import Image
import io
import random
import base64
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Get environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY', '')
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', '')
GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'global')
USE_VERTEX_AI = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'False').lower() == 'true'

# Initialize client based on configuration
if USE_VERTEX_AI and GOOGLE_CLOUD_API_KEY:
    # Use Vertex AI client
    client = genai.Client(
        vertexai=True,
        api_key=GOOGLE_CLOUD_API_KEY,
    )
    print(f"Using Vertex AI client with project: {GOOGLE_CLOUD_PROJECT}")
elif GEMINI_API_KEY:
    # Use standard Gemini API client
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("Using standard Gemini API client")
else:
    client = None
    print("No API key configured, using mock generation")

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

    if not client:
        image_data, text_response = generate_mock_image(prompt, aspect_ratio, resolution)
        return {
            'image_data': image_data,
            'text_response': text_response,
            'token_count': len(prompt.split()) * 2,
            'thought_signature': None,
            'grounding_metadata': None,
            'is_mock': True
        }

    try:
        # Use Nano Banana Pro (gemini-3-pro-image-preview) for Vertex AI
        if USE_VERTEX_AI:
            model = 'gemini-3-pro-image-preview'

        # Prepare the prompt as a Part
        text_part = types.Part.from_text(text=prompt)
        contents = [types.Content(role="user", parts=[text_part])]

        # Configure image generation
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            max_output_tokens=32768,
            response_modalities=["TEXT", "IMAGE"],
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
                output_mime_type="image/png",
            ),
        )

        # Generate image
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        # Extract image from response
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        text_response = response.text if hasattr(response, 'text') else None
                        return {
                            'image_data': image_data,
                            'text_response': text_response,
                            'token_count': None,
                            'thought_signature': None,
                            'grounding_metadata': None,
                            'is_mock': False
                        }

        # Fallback to mock if no image in response
        image_data, text_response = generate_mock_image(prompt, aspect_ratio, resolution)
        return {
            'image_data': image_data,
            'text_response': text_response,
            'is_mock': True
        }

    except Exception as e:
        print(f"Error generating image with Gemini API: {e}")
        import traceback
        traceback.print_exc()
        image_data, text_response = generate_mock_image(prompt, aspect_ratio, resolution)
        return {
            'image_data': image_data,
            'text_response': text_response,
            'is_mock': True,
            'error': str(e)
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
    model: str = 'veo-3.0-generate-preview',
    aspect_ratio: str = '16:9',
    duration: str = '5s'
) -> dict:
    """Generate a video using Veo 3.1 API or mock if not available."""

    if not client:
        video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
        return {
            'video_data': video_data,
            'text_response': text_response,
            'is_mock': True
        }

    try:
        # Use Veo 3.1 for Vertex AI
        if USE_VERTEX_AI:
            model = 'veo-3.1-generate-001'

            # Configure video generation
            from google.genai.types import GenerateVideosConfig

            config = GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                # Note: output_gcs_uri is optional - without it, video returns inline
            )

            print(f"Generating video with Veo 3.1, prompt: {prompt[:100]}...")

            # Trigger video generation (long-running operation)
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                config=config,
            )

            # Poll the operation until complete (with timeout)
            max_wait_seconds = 120  # 2 minutes timeout
            poll_interval = 5  # Check every 5 seconds
            elapsed = 0

            print("Waiting for video generation to complete...")
            while not operation.done and elapsed < max_wait_seconds:
                time.sleep(poll_interval)
                elapsed += poll_interval
                operation = client.operations.get(operation)
                print(f"Still waiting... ({elapsed}s elapsed)")

            if not operation.done:
                print("Video generation timed out, falling back to mock")
                video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
                return {
                    'video_data': video_data,
                    'text_response': 'Video generation timed out',
                    'is_mock': True
                }

            # Extract the generated video
            if operation.response and hasattr(operation.result, 'generated_videos'):
                generated_videos = operation.result.generated_videos
                if generated_videos and len(generated_videos) > 0:
                    video_obj = generated_videos[0]

                    # Check if video has inline data or URI
                    if hasattr(video_obj, 'video') and video_obj.video:
                        if hasattr(video_obj.video, 'inline_data') and video_obj.video.inline_data:
                            video_data = video_obj.video.inline_data.data
                            print(f"Video generated successfully, size: {len(video_data)} bytes")
                            return {
                                'video_data': video_data,
                                'text_response': f'Video generated with Veo 3.1',
                                'is_mock': False
                            }
                        elif hasattr(video_obj.video, 'uri'):
                            # Video is stored in GCS, would need to download
                            print(f"Video URI: {video_obj.video.uri}")
                            video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
                            return {
                                'video_data': video_data,
                                'text_response': f'Video stored at: {video_obj.video.uri}',
                                'is_mock': True,
                                'video_uri': video_obj.video.uri
                            }

            # Fallback if unexpected response format
            print("Unexpected response format from Veo 3.1")
            video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
            return {
                'video_data': video_data,
                'text_response': text_response,
                'is_mock': True
            }
        else:
            # For non-Vertex AI, use the old method (will likely fail)
            config = {
                'response_modalities': ['VIDEO'],
            }

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )

            # Extract video data from the response
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    video_part = candidate.content.parts[0]

                    if hasattr(video_part, 'inline_data') and video_part.inline_data:
                        video_data = video_part.inline_data.data
                        return {
                            'video_data': video_data,
                            'text_response': response.text if hasattr(response, 'text') else None,
                            'is_mock': False
                        }

            # Fallback to mock if response format is unexpected
            video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
            return {
                'video_data': video_data,
                'text_response': text_response,
                'is_mock': True
            }

    except Exception as e:
        # Fallback to mock on error
        print(f"Error generating video with Gemini API: {e}")
        import traceback
        traceback.print_exc()
        video_data, text_response = generate_mock_video(prompt, aspect_ratio, duration)
        return {
            'video_data': video_data,
            'text_response': text_response,
            'is_mock': True,
            'error': str(e)
        }
