import os
import uuid
from datetime import datetime
from pathlib import Path

IMAGES_DIR = Path('/home/user/backend/static/images')
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def generate_filename(extension: str = 'png') -> str:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f'{timestamp}_{unique_id}.{extension}'

def save_image(image_data: bytes, filename: str) -> str:
    file_path = IMAGES_DIR / filename
    with open(file_path, 'wb') as f:
        f.write(image_data)
    return str(file_path)

def delete_image(filename: str) -> bool:
    file_path = IMAGES_DIR / filename
    if file_path.exists():
        os.remove(file_path)
        return True
    return False

def get_image_url(filename: str) -> str:
    return f'/static/images/{filename}'
