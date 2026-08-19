import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from ai.services import AIService

prompt = """Buat 1 quote/motto tentang astrologi dengan topik: Aquarius.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, misterius & aesthetic.

Output JSON:
{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote astrologi. Mystical, aesthetic, menyentuh hati.",
    "hashtags": "15 hashtag relevan tentang astrologi/zodiak",
    "cta": "CTA untuk tag teman zodiak",
    "image_prompt": "Deskripsi gambar kosmik/misterius untuk quote ini, dalam bahasa Inggris",
    "category": "astrology"
}"""

try:
    result = AIService._call_ai([{"role": "user", "content": prompt}])
    print("SUCCESS:", result)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e))
