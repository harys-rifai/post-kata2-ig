import json
import os
import time
from pathlib import Path
from django.conf import settings
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import requests


class AIService:
    @staticmethod
    def _call_ai(messages, model=None):
        model = model or settings.AI_MODEL
        response = requests.post(
            f"{settings.AI_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
            },
            timeout=120,
        )
        response.raise_for_status()
        data = AIService._parse_response_json(response)
        if "choices" not in data or not data["choices"]:
            raise ValueError("AI response missing 'choices'")
        choice = data["choices"][0]
        if "message" not in choice or "content" not in choice["message"]:
            raise ValueError("AI response missing 'message.content'")
        return choice["message"]["content"]

    @staticmethod
    def _parse_response_json(response):
        import json
        import re
        text = response.text
        # Strip SSE framing: server appends "data: [DONE]" or sends "data: {...}" lines
        sse_lines = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                sse_lines.append(line[6:])
        if sse_lines:
            text = "".join(sse_lines)
        # Some servers stream multiple chunks that form one JSON object
        text = text.replace("data: ", "")
        text = text.replace("[DONE]", "")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return json.loads(text)

    TOPIC_CATEGORY = {
    "hidup": "hidup",
    "life": "hidup",
    "motivasi": "hidup",
    "inspirasi": "hidup",
    "kesedihan": "hidup",
    "kebahagiaan": "hidup",
    "cinta": "hidup",
    "persahabatan": "hidup",
    "ai": "ai",
    "teknologi": "ai",
    "robot": "ai",
    "machine learning": "ai",
    "deep learning": "ai",
    "astrology": "astrology",
    "zodiak": "astrology",
    "horoscope": "astrology",
    "bintang": "astrology",
    "ramalan": "astrology",
    "pisces": "astrology",
    "aries": "astrology",
    "taurus": "astrology",
    "gemini": "astrology",
    "cancer": "astrology",
    "leo": "astrology",
    "virgo": "astrology",
    "libra": "astrology",
    "scorpio": "astrology",
    "sagittarius": "astrology",
    "capricorn": "astrology",
    "aquarius": "astrology",
}

    @staticmethod
    def classify_topic(topic):
        """Detect category: hidup, ai, or astrology."""
        t = topic.lower().strip()
        for key, cat in AIService.TOPIC_CATEGORY.items():
            if key in t:
                return cat
        return "hidup"  # default

    @staticmethod
    def generate_caption(topic):
        category = AIService.classify_topic(topic)
        prompts = {
            "hidup": f"""
Buat 1 quote/motto tentang hidup dengan topik: {topic}.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, memotivasi.

Output JSON:
{{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote/motto lengkap. Bersih, pendek, powerful.",
    "hashtags": "15 hashtag relevan tentang motivasi/kehidupan",
    "cta": "CTA untuk comment/share",
    "category": "hidup"
}}""",
            "ai": f"""
Buat 1 quote tentang AI/teknologi dengan topik: {topic}.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, visioner.

Output JSON:
{{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote tentang AI/teknologi. Futuristik, menyentuh, relatable.",
    "hashtags": "15 hashtag relevan tentang AI/teknologi",
    "cta": "CTA untuk follow/comment",
    "category": "ai"
}}""",
            "astrology": f"""
Buat 1 quote/motto tentang astrologi dengan topik: {topic}.
Quote harus pendek (maks 2 kalimat), dalam Bahasa Indonesia, misterius & aesthetic.

Output JSON:
{{
    "title": "Judul singkat (maks 6 kata)",
    "caption": "Quote astrologi. Mystical, aesthetic, menyentuh hati.",
    "hashtags": "15 hashtag relevan tentang astrologi/zodiak",
    "cta": "CTA untuk tag teman zodiak",
    "category": "astrology"
}}""",
        }
        prompt = prompts.get(category, prompts["hidup"])
        content = AIService._call_ai([{"role": "user", "content": prompt}])
        result = AIService._parse_json(content)
        result["category"] = category
        result["topic"] = topic
        return result

    @staticmethod
    def _parse_json(content):
        import json
        import re
        try:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(content)
        except Exception:
            return {
                "title": content[:100],
                "caption": content,
                "hashtags": "#viral #trending #instagram",
                "cta": "Follow for more!",
                "image_prompt": "Modern social media design, vibrant colors",
            }

    @staticmethod
    def generate_image(prompt):
        response = requests.post(
            f"{settings.AI_API_BASE}/images/generations",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.AI_IMAGE_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
            },
            timeout=120,
        )
        if response.status_code != 200:
            return AIService._generate_placeholder_image(prompt)
        data = AIService._parse_response_json(response)
        image_url = data["data"][0]["url"]
        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        return image_response.content, image_url

    @staticmethod
    def _generate_placeholder_image(text):
        """1024x1024 dark gradient image with wrapped text — readable fallback."""
        from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter, ImageEnhance
        import io, math

        # Gradient background: dark purple → deep blue
        img = PILImage.new("RGB", (1024, 1024))
        draw_bg = ImageDraw.Draw(img)
        for y in range(1024):
            r = int(30 + 20 * (y / 1024))
            g = int(10 + 10 * (y / 1024))
            b = int(80 + 60 * (y / 1024))
            draw_bg.line([(0, y), (1024, y)], fill=(r, g, b))

        # Decorative circles
        overlay = PILImage.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for cx, cy, radius, alpha in [(200, 300, 120, 30), (800, 700, 90, 25), (500, 150, 60, 20)]:
            draw_ov.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=(255, 255, 255, alpha),
            )
        img = PILImage.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        # Text
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 44)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            font = ImageFont.load_default()
            font_small = font

        # Wrap text
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= 850:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        # Truncate to max 6 lines
        lines = lines[:6]
        total_height = len(lines) * 56
        y_start = (1024 - total_height) // 2

        # Draw each line with shadow
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (1024 - tw) // 2
            y = y_start + i * 56
            # Shadow
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0), font=font)
            # Main text
            draw.text((x, y), line, fill=(255, 255, 255), font=font)

        # Bottom label
        label = "AI Generated Content"
        lb = draw.textbbox((0, 0), label, font=font_small)
        draw.text(((1024 - (lb[2] - lb[0])) // 2, 960), label, fill=(180, 180, 220), font=font_small)

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "placeholder"


class InstagramAutomationService:
    @staticmethod
    def _get_browser_context():
        storage_path = str(settings.INSTAGRAM_SESSION_PATH)
        storage_dir = os.path.dirname(storage_path)
        os.makedirs(storage_dir, exist_ok=True)

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        if os.path.exists(storage_path):
            try:
                with open(storage_path, "r") as f:
                    storage_state = json.load(f)
                context.add_cookies(storage_state)
            except Exception:
                pass
        return p, browser, context

    @staticmethod
    def _save_session(context):
        storage_path = str(settings.INSTAGRAM_SESSION_PATH)
        try:
            state = context.storage_state()
            with open(storage_path, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Failed to save session: {e}")

    @staticmethod
    def login(page):
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        if "login" not in page.url:
            return True

        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        username_input.fill(settings.INSTAGRAM_USERNAME)
        password_input.fill(settings.INSTAGRAM_PASSWORD)

        page.click('button[type="submit"]')
        page.wait_for_timeout(5000)

        try:
            page.wait_for_selector('input[name="username"]', timeout=3000)
            page.locator('input[name="username"]').fill(settings.INSTAGRAM_USERNAME)
            verification_code = input("Enter Instagram verification code: ")
            page.locator('input[name="verificationCode"]').fill(verification_code)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
        except PlaywrightTimeout:
            pass

        return "challenge" not in page.url and "login" not in page.url

    @staticmethod
    def publish_post(post):
        p, browser, context = InstagramAutomationService._get_browser_context()
        page = context.new_page()
        try:
            InstagramAutomationService.login(page)
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            if post.image:
                image_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
                if not os.path.exists(image_path):
                    image_path = str(post.image.path)

                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(image_path)
                page.wait_for_timeout(5000)

                caption = f"{post.title}\n\n{post.caption}\n\n{post.hashtags}\n\n{post.caption.split(chr(10))[-1] if chr(10) in post.caption else ''}"

                try:
                    text_area = page.locator('div[contenteditable="true"]').first
                    text_area.fill(caption)
                except Exception:
                    try:
                        text_area = page.locator('textarea').first
                        text_area.fill(caption)
                    except Exception:
                        pass

                page.wait_for_timeout(2000)
                share_btn = page.locator('text=Share')
                if share_btn.count() > 0:
                    share_btn.first.click()
                else:
                    page.keyboard.press("Enter")
                page.wait_for_timeout(8000)
            else:
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                create_btn = page.locator('text=Create')
                if create_btn.count() > 0:
                    create_btn.first.click()
                    page.wait_for_timeout(2000)
                    caption = f"{post.title}\n\n{post.caption}\n\n{post.hashtags}"
                    try:
                        text_area = page.locator('div[contenteditable="true"]').first
                        text_area.fill(caption)
                    except Exception:
                        text_area = page.locator('textarea').first
                        text_area.fill(caption)
                    page.wait_for_timeout(2000)
                    share_btn = page.locator('text=Share')
                    if share_btn.count() > 0:
                        share_btn.first.click()
                    else:
                        page.keyboard.press("Enter")
                    page.wait_for_timeout(8000)
                else:
                    raise Exception("Could not find Create button")

            InstagramAutomationService._save_session(context)
            return True
        except Exception as e:
            print(f"Instagram publish error: {e}")
            return False
        finally:
            context.close()
            browser.close()
            p.stop()
