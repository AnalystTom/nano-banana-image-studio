import aiosqlite
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / 'database.db'

async def get_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT NOT NULL DEFAULT 'gemini-2.5-flash-image',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                prompt TEXT NOT NULL,
                model TEXT NOT NULL,
                aspect_ratio TEXT NOT NULL DEFAULT '1:1',
                resolution TEXT,
                response_modality TEXT NOT NULL DEFAULT 'TEXT_IMAGE',
                google_search_enabled BOOLEAN DEFAULT 0,
                token_count INTEGER,
                thought_signature TEXT,
                grounding_metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message TEXT,
                image_id INTEGER,
                thought_signature TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                api_key TEXT,
                default_model TEXT DEFAULT 'gemini-2.5-flash-image',
                default_aspect_ratio TEXT DEFAULT '1:1',
                default_resolution TEXT DEFAULT '1K',
                default_response_modality TEXT DEFAULT 'TEXT_IMAGE',
                google_search_default BOOLEAN DEFAULT 0,
                auto_save_conversations BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                template TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS image_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_image_id INTEGER NOT NULL,
                edited_image_id INTEGER NOT NULL,
                edit_prompt TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (original_image_id) REFERENCES images(id) ON DELETE CASCADE,
                FOREIGN KEY (edited_image_id) REFERENCES images(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                prompt TEXT NOT NULL,
                model TEXT NOT NULL,
                aspect_ratio TEXT NOT NULL DEFAULT '16:9',
                duration TEXT NOT NULL DEFAULT '5s',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            INSERT OR IGNORE INTO settings (id) VALUES (1);

            INSERT OR IGNORE INTO prompt_templates (name, category, template, description) VALUES
            ('Photorealistic Portrait', 'portrait', 'A photorealistic portrait of {subject}, professional studio lighting, sharp focus, 8k resolution', 'Creates highly realistic portrait images'),
            ('Fantasy Landscape', 'landscape', 'A breathtaking fantasy landscape with {elements}, magical atmosphere, dramatic lighting, digital art style', 'Generates fantasy-themed landscapes'),
            ('Product Shot', 'product', 'Professional product photography of {product}, clean white background, studio lighting, commercial quality', 'Perfect for e-commerce product images'),
            ('Minimalist Design', 'design', 'Minimalist {subject} design, clean lines, simple color palette, modern aesthetic', 'Creates clean minimalist designs'),
            ('Cyberpunk City', 'sci-fi', 'Cyberpunk cityscape at night, neon lights, rain-slicked streets, flying vehicles, blade runner inspired', 'Futuristic urban sci-fi scenes');
        ''')
        await db.commit()
